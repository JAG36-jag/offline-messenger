import socket
import threading
import json

class NetworkService:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.active_connection = None  # উভয় দিকে কথা বলার জন্য সকেট রেফারেন্স
        self.is_running = False
        self.on_message_received_callback = None

    # ==========================================
    # 1. START SERVER (Host Mode)
    # ==========================================
    def start_server(self, on_message_callback):
        self.on_message_received_callback = on_message_callback
        self.is_running = True
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            listen_thread = threading.Thread(target=self._listen_for_clients, daemon=True)
            listen_thread.start()
            print(f"[Server] Started listening on port {self.port}...")
        except Exception as e:
            print(f"[Server Error] {str(e)}")

    def _listen_for_clients(self):
        while self.is_running:
            try:
                conn, addr = self.server_socket.accept()
                print(f"\n[Server] Client Connected from {addr}")
                self.active_connection = conn  # কানেক্টেড ক্লায়েন্টকে সেভ রাখা হলো
                
                recv_thread = threading.Thread(target=self._receive_data, args=(conn,), daemon=True)
                recv_thread.start()
            except Exception:
                break

    # ==========================================
    # 2. CONNECT TO DEVICE (Client Mode)
    # ==========================================
    def connect_to_device(self, target_ip, port=5000):
        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.connect((target_ip, port))
            self.active_connection = client_sock  # এক্টিভ সকেটে ক্লায়েন্ট সেভ হলো
            self.is_running = True
            
            print(f"[Client] Connected to Host {target_ip}")
            
            recv_thread = threading.Thread(target=self._receive_data, args=(client_sock,), daemon=True)
            recv_thread.start()
            return True
        except Exception as e:
            print(f"[Connection Error] {str(e)}")
            return False

    # ==========================================
    # 3. SEND MESSAGE (Both Host and Client use this)
    # ==========================================
    def send_message(self, text, sender_name):
        if not self.active_connection:
            print("\n[Error] No connected user to send message!")
            return False

        payload = {
            "type": "chat",
            "sender": sender_name,
            "text": text
        }
        
        try:
            data_bytes = json.dumps(payload).encode('utf-8')
            self.active_connection.sendall(data_bytes)
            return True
        except Exception as e:
            print(f"\n[Send Error] {str(e)}")
            return False

    # ==========================================
    # 4. RECEIVE DATA LOOP
    # ==========================================
    def _receive_data(self, conn):
        while self.is_running:
            try:
                data = conn.recv(4096)
                if not data:
                    print("\n[Notice] Connection closed by remote device.")
                    break
                
                decoded_data = json.loads(data.decode('utf-8'))
                if self.on_message_received_callback:
                    self.on_message_received_callback(decoded_data)

            except Exception:
                print("\n[Disconnected] Connection lost.")
                break

    # ==========================================
    # 5. CLOSE CONNECTION
    # ==========================================
    def stop(self):
        self.is_running = False
        if self.active_connection:
            try:
                self.active_connection.close()
            except:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass