import socket
import time
import os
import threading
import json
from crc import Calculator, Crc8
#1 ThermoNode 
#2 WindSense 
#3 RainDetect
#4 AirQualityBox
#{"device": "ThermoNode", "type": "data", "token": "idk", "timestamp": int(time.time()), "battery_low": True, "data": "hi", "crc": ""}
            
class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = "127.0.0.1"
        self.port = 6666
        self.tokens = {}
        self.listening = False
        self.calculator =Calculator(Crc8.CCITT)

    def checksum(self, message):
        message_copy = message.copy()
        if "crc" in message_copy:
            message_copy['crc'] = ""
        data = json.dumps(message_copy, sort_keys=True).encode('utf-8')
        return self.calculator.checksum(data)
        
    def send_message(self, msg, addr):
        msg['crc'] = self.checksum(msg)
        self.sock.sendto(json.dumps(msg).encode(), addr)
        
    def listen(self):
        self.sock.bind((self.ip, self.port))
        print("Started listening.")
        time.sleep(1.55)
        self.listening = True
        while self.listening:
            data, addr = self.sock.recvfrom(1024)
            #print(addr,"message:",data,time.time())

            message = json.loads(data.decode())
            #print(self.checksum(message), message['crc'])
            if self.checksum(message) != message['crc']:
                print(f"WARNING: {message['device']} CORRUPTED DATA at {message['timestamp']}.")

            if message['type'] == "registration":

                token = message['device'] + "-" + str(message['timestamp'])

                self.tokens[message['device']] = token

                print(f"INFO: {message['device']} REGISTERED at {message['timestamp']}")
                self.send_message({"type": "registration-token", "device": message['device'], "token": token, "timestamp": int(time.time()), "battery_low": False, "crc": ""}, addr)

            elif message['type'] == "data":
                if message['device'] not in self.tokens or message['token'] != self.tokens[message['device']]:
                    print("wrong token gg")
                    self.send_message({"type": "invalid_token", "device": message['device'], "timestamp": int(time.time()), "battery_low": False, "crc": ""}, addr)
                    continue

                if  message['battery_low']:
                    print(f"INFO: {message['device']} DATA: {message['data']}")
                else:
                    print(f"WARNING: LOW BATTERY {message['device']} DATA: {message['data']}")
                
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
            print("2. Listen", ("[Running]" if self.listening else "[Stopped]"))
            print("3. Exit")
            choice = input("Choose: ")
            if choice == "1":
                self.configure()
                time.sleep(1.5)
            elif choice == "2":
                if self.listening:
                    print("Stopped listening.")
                    self.listening = False
                else:
                    threading.Thread(target=self.listen).start()
                time.sleep(1.5)
            elif choice == "3":
                exit()
                break

server = Server()
server.menu()
