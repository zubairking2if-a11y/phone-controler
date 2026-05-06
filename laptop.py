"""
Laptop Client Script
Run this on your laptop to control your phone
Connect to the phone server and send commands
"""

import socket
import json
import sys
from datetime import datetime

# Configuration
BUFFER_SIZE = 1024

class PhoneController:
    def __init__(self, phone_ip, port=5555):
        self.phone_ip = phone_ip
        self.port = port
        self.connected = False
        
    def connect(self):
        """Connect to the phone server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.phone_ip, self.port))
            self.connected = True
            print(f"✅ Connected to phone at {self.phone_ip}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("💡 Make sure:")
            print("   - Phone server is running")
            print("   - Phone IP address is correct")
            print("   - Both devices are on same WiFi network")
            return False
    
    def send_command(self, command_dict):
        """Send command to phone"""
        try:
            if not self.connected:
                print("❌ Not connected to phone. Please connect first.")
                return None
            
            command_json = json.dumps(command_dict)
            self.socket.send(command_json.encode('utf-8'))
            
            response = self.socket.recv(BUFFER_SIZE).decode('utf-8')
            return json.loads(response)
            
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            self.connected = False
            return None
    
    def ping(self):
        """Check if phone is online"""
        print("🔍 Pinging phone...")
        response = self.send_command({'action': 'ping'})
        if response and response.get('status') == 'success':
            print(f"✅ {response.get('message')}")
            print(f"⏰ {response.get('timestamp')}")
            return True
        return False
    
    def get_info(self):
        """Get phone information"""
        print("📱 Fetching phone info...")
        response = self.send_command({'action': 'info'})
        if response and response.get('status') == 'success':
            data = response.get('data', {})
            print("=" * 40)
            for key, value in data.items():
                print(f"{key.upper()}: {value}")
            print("=" * 40)
            return True
        return False
    
    def send_message(self, content):
        """Send message to phone"""
        print(f"📤 Sending message: {content}")
        response = self.send_command({'action': 'message', 'content': content})
        if response and response.get('status') == 'success':
            print(f"✅ {response.get('message')}")
            return True
        return False
    
    def echo(self, content):
        """Echo test"""
        print(f"🔊 Sending echo: {content}")
        response = self.send_command({'action': 'echo', 'content': content})
        if response and response.get('status') == 'success':
            print(f"✅ {response.get('echo')}")
            return True
        return False
    
    def list_files(self):
        """List files on phone"""
        print("📂 Fetching file list...")
        response = self.send_command({'action': 'files'})
        if response and response.get('status') == 'success':
            files = response.get('files', [])
            print("Files on phone:")
            for file in files:
                print(f"  📄 {file}")
            return True
        return False
    
    def disconnect(self):
        """Disconnect from phone"""
        if self.connected:
            self.socket.close()
            self.connected = False
            print("✅ Disconnected from phone")


def print_menu():
    """Print interactive menu"""
    print("\n" + "=" * 50)
    print("📱 PHONE CONTROLLER MENU")
    print("=" * 50)
    print("1. 🔍 Ping phone (check if online)")
    print("2. 📱 Get phone info")
    print("3. 💬 Send message")
    print("4. 🔊 Echo test")
    print("5. 📂 List files")
    print("6. 🚪 Disconnect")
    print("0. ❌ Exit")
    print("=" * 50)


def main():
    print("=" * 50)
    print("🖥️  LAPTOP CLIENT - PHONE CONTROLLER")
    print("=" * 50)
    
    # Get phone IP address
    phone_ip = input("\n📌 Enter your phone's IP address (e.g., 192.168.1.100): ").strip()
    
    if not phone_ip:
        print("❌ IP address cannot be empty!")
        sys.exit(1)
    
    # Create controller instance
    controller = PhoneController(phone_ip)
    
    # Connect to phone
    if not controller.connect():
        sys.exit(1)
    
    # Interactive menu
    while True:
        print_menu()
        choice = input("Enter your choice (0-6): ").strip()
        
        if choice == '1':
            controller.ping()
        
        elif choice == '2':
            controller.get_info()
        
        elif choice == '3':
            message = input("📝 Enter message to send: ").strip()
            if message:
                controller.send_message(message)
        
        elif choice == '4':
            test_msg = input("🔊 Enter text for echo test: ").strip()
            if test_msg:
                controller.echo(test_msg)
        
        elif choice == '5':
            controller.list_files()
        
        elif choice == '6':
            controller.disconnect()
            print("\n✅ Press any key to reconnect or 0 to exit")
            new_choice = input("Choice: ").strip()
            if new_choice == '0':
                break
            else:
                phone_ip = input("📌 Enter phone IP address: ").strip()
                controller = PhoneController(phone_ip)
                if not controller.connect():
                    break
        
        elif choice == '0':
            print("\n👋 Goodbye!")
            if controller.connected:
                controller.disconnect()
            break
        
        else:
            print("❌ Invalid choice! Please select 0-6")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted. Goodbye!")
        sys.exit(0)
