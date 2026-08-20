import os
import time
import json
import socket
import threading
from kivy.clock import Clock
from database.db_manager import DatabaseManager

UDP_PORT = 50000
TCP_PORT = 50001
BUFFER_SIZE = 4096

class NetworkManager:
    def __init__(self, user_name="User", on_msg_received=None, on_peer_found=None):
        self.user_name = user_name
        self.on_msg_received = on_msg_received
        self.on_peer_found = on_peer_found
        self.discovered_peers = {}  # {peer_name: peer_ip}
        self.is_running = False
        self.db = DatabaseManager()

    def start_server(self, on_message_callback=None):
        if on_message_callback:
            self.on_msg_received = on_message_callback
        self.is_running = True
        threading.Thread(target=self._listen_udp_broadcast, daemon=True).start()
        threading.Thread(target=self._broadcast_presence, daemon=True).start()
        threading.Thread(target=self._start_tcp_server, daemon=True).start()
        print("NetworkManager started successfully...")

    def stop(self):
        self.is_running = False

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _broadcast_presence(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.is_running:
            try:
                my_ip = self._get_local_ip()
                data = json.dumps({"name": self.user_name, "ip": my_ip})
                sock.sendto(data.encode('utf-8'), ('<broadcast>', UDP_PORT))
                time.sleep(3)
            except Exception:
                pass
        sock.close()

    def _listen_udp_broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('', UDP_PORT))
        except Exception:
            return

        while self.is_running:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                info = json.loads(data.decode('utf-8'))
                peer_ip = info.get("ip")
                peer_name = info.get("name")
                my_ip = self._get_local_ip()

                if peer_ip and peer_ip != my_ip:
                    self.discovered_peers[peer_name] = peer_ip
                    if self.on_peer_found:
                        Clock.schedule_once(lambda dt: self.on_peer_found(peer_name, peer_ip), 0)
            except Exception:
                pass
        sock.close()

    def _start_tcp_server(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_sock.bind(('', TCP_PORT))
            server_sock.listen(5)
        except Exception:
            return

        while self.is_running:
            try:
                client_sock, addr = server_sock.accept()
                threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True).start()
            except Exception:
                pass
        server_sock.close()

    def _handle_client(self, client_sock):
        try:
            header_data = b""
            while b'\n<HEADER_END>\n' not in header_data:
                chunk = client_sock.recv(1024)
                if not chunk:
                    break
                header_data += chunk

            if b'\n<HEADER_END>\n' in header_data:
                raw_header, file_bytes = header_data.split(b'\n<HEADER_END>\n', 1)
                payload = json.loads(raw_header.decode('utf-8'))
                msg_type = payload.get("type", "text")
                sender = payload.get("sender", "Peer")

                if msg_type == "text":
                    text_msg = payload.get("message", "")
                    self.db.save_message(sender, "Me", text_msg, "text")
                    if self.on_msg_received:
                        Clock.schedule_once(lambda dt: self.on_msg_received(payload), 0)

                elif msg_type == "file":
                    file_name = payload.get("filename", "received_file")
                    file_size = payload.get("filesize", 0)
                    download_dir = os.path.join(os.getcwd(), 'downloads')
                    os.makedirs(download_dir, exist_ok=True)
                    save_path = os.path.join(download_dir, file_name)

                    received_bytes = len(file_bytes)
                    with open(save_path, 'wb') as f:
                        f.write(file_bytes)
                        while received_bytes < file_size:
                            chunk = client_sock.recv(min(BUFFER_SIZE, file_size - received_bytes))
                            if not chunk:
                                break
                            f.write(chunk)
                            received_bytes += len(chunk)

                    file_msg = f"[File] {file_name}"
                    self.db.save_message(sender, "Me", file_msg, "file")
                    if self.on_msg_received:
                        Clock.schedule_once(lambda dt: self.on_msg_received({
                            "type": "file",
                            "sender": sender,
                            "filename": file_name,
                            "filepath": save_path
                        }), 0)
        except Exception as e:
            print(f"[Handle Client Error]: {e}")
        finally:
            client_sock.close()

    def send_text_message(self, target_ip, target_name, message_text):
        if not target_ip or not isinstance(target_ip, str) or target_ip.strip() == "":
            print(f"[Send Message Error]: Invalid target IP -> {target_ip}")
            return

        def _send():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((target_ip, TCP_PORT))

                payload = {
                    "type": "text",
                    "sender": self.user_name,
                    "message": message_text
                }
                header = json.dumps(payload) + '\n<HEADER_END>\n'
                sock.sendall(header.encode('utf-8'))
                sock.close()

                self.db.save_message("Me", target_name, message_text, "text")
            except Exception as e:
                print(f"[Send Message Error]: {e}")

        threading.Thread(target=_send, daemon=True).start()

    def send_file(self, target_ip, file_path, callback_on_finish=None):
        if not target_ip or not os.path.exists(file_path):
            print(f"[Send File Error]: Invalid IP or File not found -> {file_path}")
            if callback_on_finish:
                callback_on_finish(False)
            return

        def _send():
            try:
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((target_ip, TCP_PORT))

                payload = {
                    "type": "file",
                    "sender": self.user_name,
                    "filename": filename,
                    "filesize": file_size
                }
                header = json.dumps(payload) + '\n<HEADER_END>\n'
                sock.sendall(header.encode('utf-8'))

                with open(file_path, "rb") as f:
                    while True:
                        chunk = f.read(BUFFER_SIZE)
                        if not chunk:
                            break
                        sock.sendall(chunk)

                sock.close()
                print(f"File '{filename}' sent successfully to {target_ip}")
                
                if callback_on_finish:
                    Clock.schedule_once(lambda dt: callback_on_finish(True), 0)
            except Exception as e:
                print(f"[Send File Error]: {e}")
                if callback_on_finish:
                    Clock.schedule_once(lambda dt: callback_on_finish(False), 0)

        threading.Thread(target=_send, daemon=True).start()