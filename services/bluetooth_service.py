import socket
import threading
import json
import time

class BluetoothService:
    def __init__(self, port=1):
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.is_listening = False
        self.is_connected = False
        self.on_message_received_callback = None

    def start_server(self, on_message_callback=None):
        """ডিভাইসকে সার্ভার হিসেবে রেডি করে অন্য ডিভাইসের কানেকশনের জন্য অপেক্ষা করবে"""
        self.on_message_received_callback = on_message_callback
        try:
            self.server_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.server_socket.bind(("", self.port))
            self.server_socket.listen(1)
            self.is_listening = True
            
            listen_thread = threading.Thread(target=self._listen_for_connections, daemon=True)
            listen_thread.start()
            print("[Bluetooth] Server started. Listening for connections...")
            return True
        except Exception as e:
            print(f"[Bluetooth] Failed to start server: {e}")
            return False

    def _listen_for_connections(self):
        while self.is_listening:
            try:
                client, address = self.server_socket.accept()
                self.client_socket = client
                self.is_connected = True
                print(f"[Bluetooth] Connected to {address}")
                self._receive_messages()
            except Exception as e:
                print(f"[Bluetooth] Connection error: {e}")
                self.is_connected = False
                break

    def connect_to_device(self, mac_address, on_message_callback=None):
        """নির্দিষ্ট ব্লুটুথ MAC এড্রেসে কানেক্ট হবে"""
        self.on_message_received_callback = on_message_callback
        try:
            self.client_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.client_socket.connect((mac_address, self.port))
            self.is_connected = True
            print(f"[Bluetooth] Successfully connected to {mac_address}")

            recv_thread = threading.Thread(target=self._receive_messages, daemon=True)
            recv_thread.start()
            return True
        except Exception as e:
            print(f"[Bluetooth] Connection failed to {mac_address}: {e}")
            self.is_connected = False
            return False

    def send_message(self, text_message, sender_name="User"):
        """মেসেজ JSON ফরম্যাটে বাইট হিসেবে পাঠাবে"""
        if not self.is_connected or not self.client_socket:
            print("[Bluetooth] Cannot send message: Not connected")
            return False

        payload = {
            "sender": sender_name,
            "message": text_message
        }

        try:
            data = json.dumps(payload).encode('utf-8')
            self.client_socket.send(data)
            print(f"[Bluetooth] Message sent: {text_message}")
            return True
        except Exception as e:
            print(f"[Bluetooth] Error sending message: {e}")
            self.is_connected = False
            return False

    def _receive_messages(self):
        """ব্যাকগ্রাউন্ডে মেসেজ শোনার কাজ করবে"""
        while self.is_connected:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                
                payload = json.loads(data.decode('utf-8'))
                print(f"[Bluetooth] Received: {payload}")

                if self.on_message_received_callback:
                    self.on_message_received_callback(payload)

            except Exception as e:
                print(f"[Bluetooth] Connection lost/error: {e}")
                self.is_connected = False
                break

    def discover_devices(self, callback_on_found):
        """আশেপাশের পাওয়া ব্লুটুথ ডিভাইসগুলো খুঁজে বের করবে"""
        threading.Thread(target=self._scan_worker, args=(callback_on_found,), daemon=True).start()

    def _scan_worker(self, callback_on_found):
        found_devices = []
        try:
            import bluetooth  # type: ignore
            nearby = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True)
            for addr, name in nearby:
                found_devices.append({"name": name, "address": addr})
        except Exception:
            # Fallback for Windows Testing / Simulation
            time.sleep(2)
            found_devices = [
                {"name": "Friend's Phone (Bluetooth)", "address": "00:11:22:33:44:55"},
                {"name": "Nearby Galaxy Device", "address": "AA:BB:CC:DD:EE:FF"}
            ]
        
        if callback_on_found:
            callback_on_found(found_devices)