import socket
import time
import os
import threading
import json

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = "127.0.0.1"
        self.port = 6666
        
    def listen(self):
        self.sock.bind((self.ip, self.port))
        print("Started listening.")
        while True:
            data, addr = self.sock.recvfrom(1024)
            print(addr,"message:",data,time.time())
            
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def configure(self):
        self.clear_screen()
        self.ip = input("Enter server IP (default 127.0.0.1): ") or "127.0.0.1"
        self.port = int(input("Enter server port (default 6666): ") or 6666)
        print(f"Configured to {self.ip}:{self.port}")

    def menu(self):
        while True:
            self.clear_screen()
            print("Server Menu:")
            print("1. Configure IP/Port")
            print("2. Listen")
            print("3. Exit")
            choice = input("Choose: ")
            if choice == "1":
                self.configure()
                time.sleep(1.5)
            elif choice == "2":
                threading.Thread(target=self.listen).start()
                time.sleep(1.5)
            elif choice == "3":
                exit()
                break




server = Server()
server.menu()
