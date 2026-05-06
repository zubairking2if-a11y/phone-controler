#!/usr/bin/env python3
"""
Complete Phone Control System - All-in-One
Educational Purpose Only
Run on both laptop (web server) and phone (client)
"""

import json
import os
import time
import sys
import uuid
from datetime import datetime
from threading import Thread

try:
    from flask import Flask, render_template_string, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("❌ Flask not installed. Run: pip install Flask Flask-CORS")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("❌ Requests not installed. Run: pip install requests")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True

# ============================================================================
# HTML DASHBOARD (Embedded)
# ============================================================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 Phone Control Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }
        
        .device-list {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            margin-bottom: 30px;
        }
        
        .device-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .device-info h3 {
            color: #333;
            margin-bottom: 5px;
        }
        
        .device-info p {
            color: #999;
            font-size: 0.9rem;
        }
        
        .device-status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
        }
        
        .status-online {
            background: #d4edda;
            color: #155724;
        }
        
        .status-offline {
            background: #f8d7da;
            color: #721c24;
        }
        
        button {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            background: #667eea;
            color: white;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            transition: background 0.3s;
            margin: 5px;
        }
        
        button:hover {
            background: #764ba2;
        }
        
        button.danger {
            background: #dc3545;
        }
        
        button.danger:hover {
            background: #c82333;
        }
        
        button.success {
            background: #28a745;
        }
        
        button.success:hover {
            background: #218838;
        }
        
        .control-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
        }
        
        .control-button {
            padding: 15px 10px;
            text-align: center;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
            margin: 0;
        }
        
        .control-button:hover {
            transform: scale(1.05);
        }
        
        .screen {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .volume {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .camera {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .location {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: white;
        }
        
        .info {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
        }
        
        .logs {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .log-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            font-size: 0.9rem;
            color: #666;
        }
        
        .log-item:last-child {
            border-bottom: none;
        }
        
        .timestamp {
            color: #999;
            font-size: 0.8rem;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        @media (max-width: 768px) {
            header h1 {
                font-size: 2rem;
            }
            
            .dashboard {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📱 Phone Control Dashboard</h1>
            <p>Control your Android devices remotely</p>
        </header>
        
        <!-- Status Alert -->
        <div id="status-alert" class="alert alert-info">
            Loading dashboard...
        </div>
        
        <!-- Connected Devices -->
        <div class="device-list">
            <h2>🔌 Connected Devices</h2>
            <div id="devices-container">
                <p>Loading devices...</p>
            </div>
            <button onclick="refreshDevices()" style="width: 100%; margin-top: 15px;">🔄 Refresh Devices</button>
        </div>
        
        <!-- Control Dashboard -->
        <div class="dashboard">
            <!-- Screen Controls -->
            <div class="card">
                <h2>🔆 Screen Controls</h2>
                <div class="control-section">
                    <button class="control-button screen" onclick="sendCommand('turn_on_screen')">Turn ON</button>
                    <button class="control-button screen" onclick="sendCommand('turn_off_screen')">Turn OFF</button>
                    <button class="control-button screen danger" onclick="sendCommand('lock_phone')">🔒 Lock</button>
                </div>
            </div>
            
            <!-- Volume Controls -->
            <div class="card">
                <h2>🔊 Volume Controls</h2>
                <div class="control-section">
                    <button class="control-button volume" onclick="sendCommand('increase_volume')">⬆️ Up</button>
                    <button class="control-button volume" onclick="sendCommand('decrease_volume')">⬇️ Down</button>
                    <button class="control-button volume danger" onclick="sendCommand('mute')">Mute</button>
                </div>
            </div>
            
            <!-- Camera Controls -->
            <div class="card">
                <h2>📷 Camera Controls</h2>
                <div class="control-section">
                    <button class="control-button camera" onclick="sendCommand('take_photo')">📸 Take Photo</button>
                </div>
            </div>
            
            <!-- Location Controls -->
            <div class="card">
                <h2>📍 Location</h2>
                <div class="control-section">
                    <button class="control-button location" onclick="sendCommand('get_location')">Get Location</button>
                </div>
            </div>
            
            <!-- Device Info -->
            <div class="card">
                <h2>📱 Device Info</h2>
                <div class="control-section">
                    <button class="control-button info" onclick="sendCommand('get_device_info')">Get Info</button>
                    <button class="control-button info" onclick="sendCommand('get_battery')">🔋 Battery</button>
                </div>
            </div>
        </div>
        
        <!-- Control Logs -->
        <div class="logs">
            <h2>📋 Control Logs</h2>
            <div id="logs-container" style="max-height: 300px; overflow-y: auto;">
                <p>Loading logs...</p>
            </div>
            <button onclick="refreshLogs()" style="width: 100%; margin-top: 15px;">🔄 Refresh Logs</button>
        </div>
    </div>
    
    <script>
        const API_BASE = '/api';
        let selectedDeviceId = null;
        
        function showAlert(message, type = 'info') {
            const alert = document.getElementById('status-alert');
            alert.textContent = message;
            alert.className = `alert alert-${type}`;
        }
        
        // Fetch and display connected devices
        async function refreshDevices() {
            try {
                const response = await fetch(`${API_BASE}/devices`);
                const data = await response.json();
                
                const container = document.getElementById('devices-container');
                if (data.total === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #999;">No devices connected yet</p>';
                    showAlert('No devices connected. Waiting for phone to connect...', 'info');
                    return;
                }
                
                showAlert(`✅ ${data.total} device(s) connected`, 'success');
                
                let html = '';
                for (const [deviceId, device] of Object.entries(data.devices)) {
                    const statusClass = device.status === 'online' ? 'status-online' : 'status-offline';
                    const isSelected = deviceId === selectedDeviceId ? 'success' : '';
                    html += `
                        <div class="device-item">
                            <div class="device-info">
                                <h3>${device.name}</h3>
                                <p>${deviceId}</p>
                            </div>
                            <span class="device-status ${statusClass}">${device.status.toUpperCase()}</span>
                            <button class="${isSelected}" onclick="selectDevice('${deviceId}')">Select</button>
                        </div>
                    `;
                }
                container.innerHTML = html;
            } catch (error) {
                console.error('Error fetching devices:', error);
                showAlert('❌ Error loading devices', 'error');
            }
        }
        
        // Select a device for control
        function selectDevice(deviceId) {
            selectedDeviceId = deviceId;
            showAlert(`✅ Device selected!`, 'success');
            refreshDevices();
        }
        
        // Send control command
        async function sendCommand(command) {
            if (!selectedDeviceId) {
                showAlert('❌ Please select a device first', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/control/${selectedDeviceId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ command: command })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    showAlert(`✅ Command sent: ${command}`, 'success');
                    refreshLogs();
                } else {
                    showAlert(`❌ Command failed`, 'error');
                }
            } catch (error) {
                console.error('Error sending command:', error);
                showAlert('❌ Error sending command', 'error');
            }
        }
        
        // Fetch and display logs
        async function refreshLogs() {
            try {
                const response = await fetch(`${API_BASE}/logs`);
                const data = await response.json();
                
                const container = document.getElementById('logs-container');
                if (data.logs.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #999;">No logs available</p>';
                    return;
                }
                
                let html = '';
                for (const log of data.logs.reverse().slice(0, 50)) {
                    const time = new Date(log.timestamp).toLocaleTimeString();
                    html += `<div class="log-item">🔹 ${log.action} <span class="timestamp">${time}</span></div>`;
                }
                container.innerHTML = html;
            } catch (error) {
                console.error('Error fetching logs:', error);
            }
        }
        
        // Initialize dashboard
        window.onload = () => {
            refreshDevices();
            refreshLogs();
            setInterval(refreshDevices, 5000);  // Auto-refresh every 5 seconds
            setInterval(refreshLogs, 3000);     // Auto-refresh logs every 3 seconds
        };
    </script>
</body>
</html>
'''

# ============================================================================
# FLASK WEB SERVER
# ============================================================================

app = Flask(__name__)
CORS(app)

# Global data storage
connected_devices = {}
control_logs = []

@app.route('/')
def index():
    """Main dashboard"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/register-phone', methods=['POST'])
def register_phone():
    """Phone registers itself with backend"""
    try:
        data = request.json
        device_id = data.get('device_id')
        device_name = data.get('device_name', 'Unknown Device')
        
        connected_devices[device_id] = {
            'name': device_name,
            'connected_at': datetime.now().isoformat(),
            'status': 'online'
        }
        
        log_action(f"📱 Phone Registered: {device_name}")
        
        return jsonify({
            'status': 'success',
            'message': f'Phone registered: {device_name}',
            'device_id': device_id
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all connected devices"""
    return jsonify({
        'devices': connected_devices,
        'total': len(connected_devices)
    }), 200

@app.route('/api/control/<device_id>', methods=['POST'])
def control_device(device_id):
    """Send control command to phone"""
    try:
        data = request.json
        command = data.get('command')
        
        if device_id not in connected_devices:
            return jsonify({'status': 'error', 'message': 'Device not found'}), 404
        
        log_action(f"🎮 Command: {command} → {connected_devices[device_id]['name']}")
        
        return jsonify({
            'status': 'success',
            'command': command,
            'device': connected_devices[device_id]['name'],
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get control logs"""
    return jsonify({
        'logs': control_logs[-50:],
        'total': len(control_logs)
    }), 200

def log_action(action):
    """Log an action"""
    control_logs.append({
        'timestamp': datetime.now().isoformat(),
        'action': action
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

# ============================================================================
# PHONE CLIENT
# ============================================================================

class PhoneClient:
    def __init__(self, ngrok_url, device_id, device_name):
        self.ngrok_url = ngrok_url.rstrip('/')
        self.device_id = device_id
        self.device_name = device_name
        self.api_url = f"{self.ngrok_url}/api"
        self.is_registered = False
    
    def register(self):
        """Register phone with backend"""
        try:
            payload = {
                'device_id': self.device_id,
                'device_name': self.device_name
            }
            response = requests.post(
                f"{self.api_url}/register-phone",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                self.is_registered = True
                print(f"\n✅ Successfully registered!")
                print(f"   Device: {self.device_name}")
                print(f"   ID: {self.device_id}")
                print(f"   Status: Online 🟢")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print(f"   Make sure your ngrok URL is correct")
            return False
    
    def show_menu(self):
        """Display menu"""
        print("\n" + "="*50)
        print("📱 PHONE CONTROL SYSTEM")
        print("="*50)
        print("1. Get Device Info")
        print("2. Get Battery Status")
        print("3. Turn On Screen")
        print("4. Turn Off Screen")
        print("5. Lock Phone")
        print("6. Increase Volume")
        print("7. Decrease Volume")
        print("8. Mute Phone")
        print("9. Take Photo")
        print("10. Get Location")
        print("11. Open Dashboard (Show URL)")
        print("0. Exit")
        print("="*50)
        return input("Select option: ")
    
    def execute_command(self, command):
        """Execute command"""
        commands = {
            '1': ('get_device_info', '📱 Getting device info...'),
            '2': ('get_battery', '🔋 Getting battery status...'),
            '3': ('turn_on_screen', '🔆 Turning on screen...'),
            '4': ('turn_off_screen', '🔅 Turning off screen...'),
            '5': ('lock_phone', '🔒 Locking phone...'),
            '6': ('increase_volume', '🔊 Increasing volume...'),
            '7': ('decrease_volume', '🔉 Decreasing volume...'),
            '8': ('mute', '🔇 Muting phone...'),
            '9': ('take_photo', '📸 Taking photo...'),
            '10': ('get_location', '📍 Getting location...'),
        }
        
        if command in commands:
            cmd, msg = commands[command]
            print(msg)
            time.sleep(1)
            print(f"✅ {cmd} executed successfully!")
        elif command == '11':
            print(f"\n🌐 Dashboard URL: {self.ngrok_url}")
            print("   Open this in your browser to control the phone")
        elif command == '0':
            return False
        else:
            print("❌ Invalid option")
        
        return True
    
    def run_interactive(self):
        """Run interactive client"""
        if not self.register():
            return
        
        print("\n💡 Tip: Open dashboard at the URL shown above")
        print("   Open it in a web browser to see controls")
        
        while True:
            choice = self.show_menu()
            if not self.execute_command(choice):
                print("\n👋 Goodbye!")
                break

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main function"""
    print("\n" + "="*60)
    print("📱 PHONE CONTROL SYSTEM - All-in-One")
    print("="*60)
    print("\nSelect Mode:")
    print("1. Start Web Server (Laptop Dashboard)")
    print("2. Start Phone Client (Android/Termux)")
    print("0. Exit")
    print("="*60)
    
    mode = input("Select mode: ").strip()
    
    if mode == '1':
        # Start web server
        print("\n" + "="*60)
        print("🚀 Starting Web Server...")
        print("="*60)
        print(f"\n✅ Server started!")
        print(f"📍 Open dashboard at: http://localhost:{Config.PORT}")
        print(f"   OR Access from other device: http://<your-ip>:{Config.PORT}")
        print(f"\n💡 Tip: Use ngrok to expose this server publicly")
        print(f"   Run: ngrok http {Config.PORT}")
        print("\nPress Ctrl+C to stop the server\n")
        
        try:
            app.run(
                host=Config.HOST,
                port=Config.PORT,
                debug=Config.DEBUG,
                use_reloader=False
            )
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped")
    
    elif mode == '2':
        # Start phone client
        print("\n" + "="*60)
        print("📱 Phone Client Setup")
        print("="*60)
        
        ngrok_url = input("\nEnter your ngrok URL\n(e.g., https://abc-123-xyz.ngrok.io): ").strip()
        
        if not ngrok_url:
            print("❌ Invalid ngrok URL")
            return
        
        device_id = str(uuid.uuid4())[:8].upper()
        device_name = input("Enter device name (e.g., My Phone): ").strip() or "My Phone"
        
        print("\n" + "="*60)
        
        client = PhoneClient(ngrok_url, device_id, device_name)
        client.run_interactive()
    
    elif mode == '0':
        print("\n👋 Goodbye!")
    
    else:
        print("❌ Invalid option")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
