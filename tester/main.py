import socket
import time
import os
import threading
import json

class Tester:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = "127.0.0.1"
        self.port = 6666
        
    def send_message(self, msg):
        self.sock.sendto(json.dumps(msg).encode(), (self.ip, self.port))
    
    def generate_messages(self):
        print("Started generating random messages.")
        while True:
            message = {"device": "ThermoNode"+"-"+"tokenlol", "timestamp": int(time.time()), "low_battery": True, "data": "hi", "crc": ""}
            self.send_message(message)
            time.sleep(1)
            
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def configure(self):
        self.clear_screen()
        self.ip = input("Enter tester IP (default 127.0.0.1): ") or "127.0.0.1"
        self.port = int(input("Enter tester port (default 6666): ") or 6666)
        print(f"Configured to {self.ip}:{self.port}")

    def menu(self):
        while True:
            self.clear_screen()
            print("Tester Menu:")
            print("1. Configure IP/Port")
            print("2. Generate Messages")
            print("3. Exit")
            choice = input("Choose: ")
            if choice == "1":
                self.configure()
                time.sleep(1.5)
            elif choice == "2":
                threading.Thread(target=self.generate_messages).start()
                time.sleep(1.5)
            elif choice == "3":
                exit()
                break




tester = Tester()
tester.menu()
