# Mobile-Based LAN Monitoring Application

## Project Overview

The Mobile-Based LAN Monitoring application provides network administrators with a tool for remotely monitoring and managing Local Area Networks (LANs) via a mobile interface. It offers real-time insights into LAN status, device connectivity, network performance, and security. The application is composed of a server, LAN clients, and a mobile client.

## Project Structure

The project consists of the following main components:

### Server
- **server.py**: Implements the server using Flask. It handles communication with LAN clients, data storage, threat detection, and provides a RESTful API for mobile clients to access LAN information.

### LAN Client
- **lan_client.py**: Monitors network activities, detects potential threats, and communicates with the server. It gathers system metrics, checks internet connectivity, and sends data to the server.

### Mobile Client
- **ClientAdapter.kt**: Manages the display and handling of client data in the user interface.
- **ThreatAdapter.kt**: Manages the display and handling of threat data in the user interface.
- **ApiService.kt**: Handles API requests to the server.
- **Client.kt**: Defines the data model for a client.
- **Threat.kt**: Defines the data model for a threat.
- **Repository.kt**: Manages data operations and provides a clean API for data access.
- **MainViewModel.kt**: Provides data to the UI and handles UI-related data in a lifecycle-conscious way.
- **MainViewModelFactory.kt**: Factory class for creating MainViewModel instances.
- **MainActivity.kt**: The main activity of the application, responsible for setting up the UI.

## Requirements

To run the project, you need to have the following installed:

- Python 3.x
- Flask
- Flask-SocketIO
- psutil
- Kotlin
- Android Studio
- Retrofit
- Gson

## Installation

### Server Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/eemreguven/Mobile-LAN-Monitoring.git
    ```

2. Navigate to the server directory:

    ```bash
    cd Mobile-LAN-Monitoring/server
    ```

3. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the server:

    ```bash
    python server.py
    ```

### LAN Client Setup

1. Navigate to the LAN client directory:

    ```bash
    cd Mobile-LAN-Monitoring/lan_client
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the LAN client:

    ```bash
    python lan_client.py
    ```

### Mobile Client Setup

1. Open Android Studio.
2. Import the mobile client project located in `Mobile-LAN-Monitoring/mobile_client/MobileLanMonitor`.
3. Build and run the project on an Android device or emulator.

## Running the Project

### Server

1. Ensure that the server is running. It will listen for client connections and manage data storage and threat detection.
2. The server will be available at `http://0.0.0.0:5000`.

### LAN Client

1. Run the LAN client on the devices you want to monitor.
2. Ensure that the LAN clients are configured with the correct server IP and port.
3. LAN clients will send network status data to the server and receive commands.

### Mobile Client

1. Open the mobile client application on your Android device.
2. The application will fetch data from the server, display client statuses and threat information, and allow you to send commands to the LAN clients.

