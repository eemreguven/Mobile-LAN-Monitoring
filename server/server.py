from flask import Flask, request, jsonify
import threading
import socket
import time
import json
import os

app = Flask(__name__)

# Locks for thread-safe operations
clients_lock = threading.Lock()  # For client statuses
threats_lock = threading.Lock()  # For threat information

# Sockets for sending commands to clients
client_sockets = {}

# Directories for storing data
DATA_DIR = 'client_data'
THREATS_DIR = 'threat_data'

# Global variables for threat information
threats = {}
threat_timestamps = {}

# API Key for authentication
API_KEY = "API_KEY_HERE"

# Check if a port is in use
def check_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Initialize and clean data directories on startup
def initialize_directories():
    if os.path.exists(DATA_DIR):
        for filename in os.listdir(DATA_DIR):
            filepath = os.path.join(DATA_DIR, filename)
            os.remove(filepath)
    else:
        os.makedirs(DATA_DIR)

    if os.path.exists(THREATS_DIR):
        for filename in os.listdir(THREATS_DIR):
            filepath = os.path.join(THREATS_DIR, filename)
            os.remove(filepath)
    else:
        os.makedirs(THREATS_DIR)

# Get LAN IP address
def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to Google's public DNS server
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# Update threat status
def update_threat_status(ip, threat_detected, data):
    current_time = time.time()
    if threat_detected:
        if ip in threat_timestamps:
            threat_timestamps[ip].append(current_time)
        else:
            threat_timestamps[ip] = [current_time]
        
        # Only keep the last 10 seconds of timestamps
        threat_timestamps[ip] = [ts for ts in threat_timestamps[ip] if current_time - ts <= 10]

        if len(threat_timestamps[ip]) >= 2:  # If at least 2 threat messages in the last 10 seconds
            threats[ip] = {
                'details': data,
                'timestamp': time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(current_time))
            }
            write_threat_data(ip, threats[ip])
    else:
        if ip in threats:
            del threats[ip]
            del threat_timestamps[ip]
            write_threat_data(ip, {'details': data, 'timestamp': time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(current_time))})

# Handle client connection and data reception
def handle_client_connection(client_socket, client_address):
    print(f"Client connected: {client_address}")
    ip = client_address[0]
    client_sockets[ip] = client_socket
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                data = json.loads(message)
                if data.get("api_key") != API_KEY:
                    print(f"Invalid API key from {ip}")
                    client_socket.close()
                    break

                with clients_lock:
                    write_client_data(ip, data)
                with threats_lock:
                    update_threat_status(ip, data['threat_detected'], data)
                
                # Print the received message
                print(f"Received data from {ip}: {data}")
        except Exception as e:
            print(f"Error receiving data from {client_address}: {e}")
            break
    client_socket.close()
    with clients_lock:
        del client_sockets[ip]

# Listen for new clients
def client_listener(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Server listening on {get_lan_ip()}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client_connection, args=(client_socket, client_address)).start()

# Periodically clean up old client statuses
def cleanup_clients():
    while True:
        time.sleep(60)
        current_time = time.time()
        with clients_lock:
            for filename in os.listdir(DATA_DIR):
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                timestamp = time.mktime(time.strptime(data['timestamp'], "%d-%m-%Y %H:%M:%S"))
                if current_time - timestamp > 300:
                    os.remove(filepath)
            
        with threats_lock:
            for filename in os.listdir(THREATS_DIR):
                filepath = os.path.join(THREATS_DIR, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                timestamp = time.mktime(time.strptime(data['timestamp'], "%d-%m-%Y %H:%M:%S"))
                if current_time - timestamp > 3600:
                    os.remove(filepath)

# Broadcast threat information periodically
def broadcast_threats():
    while True:
        time.sleep(2)
        with threats_lock:
            for ip, threat in threats.items():
                print(f"Threat from {ip}: {threat}")

# Write client data to file
def write_client_data(ip, data):
    filepath = os.path.join(DATA_DIR, f'{ip}.json')
    with open(filepath, 'w') as f:
        json.dump(data, f)

# Read client data from file
def read_client_data(ip):
    filepath = os.path.join(DATA_DIR, f'{ip}.json')
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    return None

# Write threat data to file
def write_threat_data(ip, data):
    filepath = os.path.join(THREATS_DIR, f'{ip}.json')
    with open(filepath, 'w') as f:
        json.dump(data, f)

# Read threat data from file
def read_threat_data(ip):
    filepath = os.path.join(THREATS_DIR, f'{ip}.json')
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    return None

# API endpoint to get list of clients
@app.route('/clients', methods=['GET'])
def get_clients():
    with clients_lock:
        clients = []
        for filename in os.listdir(DATA_DIR):
            ip = filename.replace('.json', '')
            data = read_client_data(ip)
            if data:
                clients.append(data)
        return jsonify(clients)

# API endpoint to get status of a specific client
@app.route('/client/<ip>', methods=['GET'])
def get_client(ip):
    with clients_lock:
        data = read_client_data(ip)
        if data:
            return jsonify(data)
    return jsonify({'error': 'Client not found'}), 404

# API endpoint to send go online/offline commands
@app.route('/client/<ip>/command', methods=['POST'])
def send_command(ip):
    with clients_lock:
        data = read_client_data(ip)
        if data:
            command = request.json.get('command')
            if command in ['go_online', 'go_offline']:
                data['command'] = command
                write_client_data(ip, data)
                # Send command to client
                if ip in client_sockets:
                    client_sockets[ip].send(json.dumps({'command': command, 'api_key': API_KEY}).encode())
                return jsonify({'status': 'success'})
            return jsonify({'error': 'Invalid command'}), 400
    return jsonify({'error': 'Client not found'}), 404

# API endpoint to get threat information
@app.route('/threats', methods=['GET'])
def get_threats():
    with threats_lock:
        response = []
        for ip, threat in threats.items():
            response.append({
                'ip': ip,
                'timestamp': threat['timestamp'],
                'is_threat': True
            })
        return jsonify(response)

if __name__ == '__main__':
    initialize_directories()  # Clean directories on application startup

    # Check the port and find an available one
    base_port = 5001
    while check_port_in_use(base_port):
        base_port += 1

    threading.Thread(target=client_listener, args=(base_port,)).start()
    threading.Thread(target=cleanup_clients).start()
    threading.Thread(target=broadcast_threats).start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

    print(f"Client should connect to {get_lan_ip()}:{base_port}")
