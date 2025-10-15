import socket
import time
import os

class Tester:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ""
        self.port = 0

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def configure(self):
        self.clear_screen()
        self.ip = input("Enter tester IP (default 127.0.0.1): ") or "127.0.0.1"
        self.port = int(input("Enter tester port (default 6666): ") or 6666)
        print(f"Configured to {self.ip}:{self.port}")
        time.sleep(1.5)

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
            elif choice == "2":
                pass
            elif choice == "3":
                exit()
                break




tester = Tester()
tester.menu()
