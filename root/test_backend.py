import os
import sys

# root ফোল্ডার থেকে ১ ধাপ ওপরে প্রজেক্টের রুট ডিরেক্টরিতে পৌঁছানোর ফিক্স
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from network.socket_service import NetworkService

# মেসেজ রিসিভ হলে যা কল হবে
def on_message(data):
    print(f"\n📩 [NEW MESSAGE RECEIVED]: {data.get('sender', 'Unknown')} -> {data.get('text', '')}")

if __name__ == "__main__":
    net = NetworkService()

    print("1. Start as Host (Server)")
    print("2. Connect as Peer (Client)")
    choice = input("Enter choice (1 or 2): ")

    if choice == '1':
        print("\n--- Starting Host Mode ---")
        net.start_server(on_message_callback=on_message)
        
        while True:
            msg = input("Type message to send (or 'exit'): ")
            if msg.lower() == 'exit':
                break
            net.send_message(text=msg, sender_name="Host Laptop")

    elif choice == '2':
        target_ip = input("Enter Target IP (Default '127.0.0.1'): ") or "127.0.0.1"
        print(f"\n--- Connecting to {target_ip} ---")
        
        if net.connect_to_device(target_ip=target_ip):
            net.on_message_received_callback = on_message
            
            while True:
                msg = input("Type message to send (or 'exit'): ")
                if msg.lower() == 'exit':
                    break
                net.send_message(text=msg, sender_name="Client Laptop")

    net.stop()