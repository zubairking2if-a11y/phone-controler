"""
Phone Server Script
Run this on your Android phone using Termux or Python for Android
This script creates a server that listens for commands from your laptop
"""

import socket
import json
import sys
import os
from datetime import datetime

# Configuration
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 5555  # Port number
BUFFER_SIZE = 1024

class PhoneServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
    def start(self):
        """Start the phone server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            self.running = True
            
            print("=" * 50)
            print("📱 PHONE SERVER STARTED")
            print("=" * 50)
            print(f"🔗 Listening on {self.host}:{self.port}")
            print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n⚠️  Make sure your laptop is on the same WiFi network!")
            print("💡 Get your phone IP: Settings > WiFi > Your Network\n")
            
            self.listen_for_commands()
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)
    
    def listen_for_commands(self):
        """Listen and process commands from laptop"""
        try:
            while self.running:
                print("\n⏳ Waiting for commands from laptop...")
                client_socket, client_address = self.server_socket.accept()
                print(f"✅ Connected from: {client_address[0]}:{client_address[1]}")
                
                try:
                    data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                    
                    if data:
                        print(f"📨 Received: {data}")
                        response = self.process_command(data)
                        client_socket.send(response.encode('utf-8'))
                        
                except Exception as e:
                    print(f"❌ Error receiving data: {e}")
                
                finally:
                    client_socket.close()
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped by user")
            self.stop()
        except Exception as e:
            print(f"❌ Error in listener: {e}")
    
    def process_command(self, command):
        """Process commands from laptop"""
        try:
            cmd_data = json.loads(command)
            action = cmd_data.get('action', '').lower()
            
            if action == 'ping':
                return json.dumps({'status': 'success', 'message': 'Phone is online!', 'timestamp': datetime.now().isoformat()})
            
            elif action == 'info':
                info = {
                    'device': 'Android Phone',
                    'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
                    'timestamp': datetime.now().isoformat(),
                    'status': 'connected'
                }
                return json.dumps({'status': 'success', 'data': info})
            
            elif action == 'message':
                msg = cmd_data.get('content', '')
                print(f"💬 MESSAGE FROM LAPTOP: {msg}")
                return json.dumps({'status': 'success', 'message': f'Message received: {msg}'})
            
            elif action == 'screenshot':
                # Note: Requires additional permissions and PIL library
                return json.dumps({'status': 'error', 'message': 'Screenshot feature requires additional setup'})
            
            elif action == 'files':
                # List files in current directory
                files = os.listdir('.')
                return json.dumps({'status': 'success', 'files': files[:10]})  # Limit to 10 files
            
            elif action == 'battery':
                # Placeholder for battery info
                return json.dumps({'status': 'success', 'battery': 'Battery info not available in this setup'})
            
            elif action == 'echo':
                msg = cmd_data.get('content', '')
                return json.dumps({'status': 'success', 'echo': f'Echo: {msg}'})
            
            else:
                return json.dumps({'status': 'error', 'message': f'Unknown action: {action}'})
                
        except json.JSONDecodeError:
            return json.dumps({'status': 'error', 'message': 'Invalid JSON format'})
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("✅ Server closed")


if __name__ == '__main__':
    server = PhoneServer()
    server.start()
