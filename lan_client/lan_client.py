import socket
import time
import json
import threading
import psutil
import subprocess
import platform

# Server IP and port
server_ip = '192.168.1.37'
server_port = 5001

# API Key for authentication
API_KEY = "API_KEY_HERE"

# Threshold values for detecting threats
UPLOAD_THRESHOLD = 2 * 1024 * 1024  # 2 MB
DOWNLOAD_THRESHOLD = 2 * 1024 * 1024  # 2 MB

# Global variable to track offline status
is_offline = False

# Function to get network status
def get_network_status(prev_upload, prev_download):
    global is_offline

    # Get CPU and memory usage
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    
    # If offline, return zeroed network stats
    if is_offline:
        return {
            'upload_speed': 0,
            'download_speed': 0,
            'connected_to_internet': False,
            'threat_detected': False,
            'total_upload': prev_upload,
            'total_download': prev_download,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'packet_sent': 0,
            'packet_recv': 0,
            'error_in': 0,
            'error_out': 0,
            'drop_in': 0,
            'drop_out': 0
        }

    # Get network I/O counters
    net_io = psutil.net_io_counters()
    current_upload = net_io.bytes_sent
    current_download = net_io.bytes_recv
    connected_to_internet = check_internet_connection()

    # Calculate upload and download speeds
    upload_speed = (current_upload - prev_upload) / 2
    download_speed = (current_download - prev_download) / 2

    return {
        'upload_speed': upload_speed,
        'download_speed': download_speed,
        'connected_to_internet': connected_to_internet,
        'threat_detected': detect_threat(upload_speed, download_speed),
        'total_upload': current_upload,
        'total_download': current_download,
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'packet_sent': net_io.packets_sent,
        'packet_recv': net_io.packets_recv,
        'error_in': net_io.errin,
        'error_out': net_io.errout,
        'drop_in': net_io.dropin,
        'drop_out': net_io.dropout
    }

# Function to check internet connection
def check_internet_connection():
    try:
        # Try to connect to Google Public DNS server
        socket.create_connection(("www.google.com", 80), timeout=2)
        return True
    except:
        return False

# Function to detect threats based on upload and download speeds
def detect_threat(upload_speed, download_speed):
    return upload_speed > UPLOAD_THRESHOLD or download_speed > DOWNLOAD_THRESHOLD

# Function to check for commands from the server
def check_for_commands(client_socket):
    global is_offline

    while True:
        try:
            # Receive command message from server
            command_message = client_socket.recv(1024).decode()
            if command_message:
                command_data = json.loads(command_message)
                command = command_data.get('command')
                # Set offline or online status based on command
                if command == 'go_offline':
                    #go_offline()
                    is_offline = True
                elif command == 'go_online':
                    #go_online()
                    is_offline = False
        except Exception as e:
            print(f"Error receiving command: {e}")
        time.sleep(2)

# Function to go offline (disable internet connection)
def go_offline():
    os_type = platform.system()
    try:
        if os_type == "Windows":
            # Windows specific command to disable internet using firewall
            subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "on"], check=True)
            subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", "name=BlockAll", "dir=out", "action=block", "enable=yes"], check=True)
            print("Internet disabled on Windows using firewall")
        elif os_type == "Linux":
            # Linux specific command to disable internet using firewall
            subprocess.run(["iptables", "-A", "OUTPUT", "-j", "DROP"], check=True)
            subprocess.run(["iptables", "-A", "INPUT", "-j", "DROP"], check=True)
            print("Internet disabled on Linux using firewall")
        else:
            print(f"Unsupported OS: {os_type}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to disable internet: {e}")

# Function to go online (enable internet connection)
def go_online():
    os_type = platform.system()
    try:
        if os_type == "Windows":
            # Windows specific command to enable internet using firewall
            subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", "name=BlockAll"], check=True)
            subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "off"], check=True)
            print("Internet enabled on Windows using firewall")
        elif os_type == "Linux":
            # Linux specific command to enable internet using firewall
            subprocess.run(["iptables", "-D", "OUTPUT", "-j", "DROP"], check=True)
            subprocess.run(["iptables", "-D", "INPUT", "-j", "DROP"], check=True)
            print("Internet enabled on Linux using firewall")
        else:
            print(f"Unsupported OS: {os_type}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to enable internet: {e}")

# Function to handle client-server communication
def client_sender():
    global server_ip, server_port
    while True:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Attempt to connect to the server
            client_socket.connect((server_ip, server_port))
            print(f"Connected to {server_ip}:{server_port}")
            break
        except ConnectionRefusedError:
            print(f"Connection to {server_ip}:{server_port} refused. Please check if the server is running.")
            server_ip = input("Enter the server IP address: ")
            server_port = int(input("Enter the server port: "))

    prev_upload = 0
    prev_download = 0

    # Start a thread to check for commands from the server
    command_thread = threading.Thread(target=check_for_commands, args=(client_socket,))
    command_thread.daemon = True
    command_thread.start()

    while True:
        # Get current network status
        network_status = get_network_status(prev_upload, prev_download)
        
        prev_upload = network_status['total_upload']
        prev_download = network_status['total_download']

        # Create a message to send to the server
        message = json.dumps({
            'ip': socket.gethostbyname(socket.gethostname()),
            'upload_speed': network_status['upload_speed'],
            'download_speed': network_status['download_speed'],
            'connected_to_internet': network_status['connected_to_internet'],
            'timestamp': time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()),
            'threat_detected': network_status['threat_detected'],
            'total_upload': network_status['total_upload'],
            'total_download': network_status['total_download'],
            'cpu_usage': network_status['cpu_usage'],
            'memory_usage': network_status['memory_usage'],
            'packet_sent': network_status['packet_sent'],
            'packet_recv': network_status['packet_recv'],
            'error_in': network_status['error_in'],
            'error_out': network_status['error_out'],
            'drop_in': network_status['drop_in'],
            'drop_out': network_status['drop_out'],
            'api_key': API_KEY  
        })
        try:
            # Send the message to the server
            client_socket.send(message.encode())
            time.sleep(2)
        except BrokenPipeError:
            print("Lost connection to the server. Attempting to reconnect...")
            client_socket.close()
            while True:
                try:
                    # Attempt to reconnect to the server
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((server_ip, server_port))
                    print(f"Reconnected to {server_ip}:{server_port}")
                    break
                except:
                    print("Reconnection failed. Retrying in 2 seconds...")
                    time.sleep(2)
                    continue
        except Exception as e:
            print(f"Unexpected error: {e}")
            client_socket.close()
            break

if __name__ == '__main__':
    # Start a thread to handle client-server communication
    sender_thread = threading.Thread(target=client_sender)
    sender_thread.daemon = True
    sender_thread.start()

    while True:
        time.sleep(1)
