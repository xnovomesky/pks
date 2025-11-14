import socket
import time
import os
import threading
import json
from crc import Calculator, Crc8

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = "127.0.0.1"
        self.port = 6666
        self.tokens = {}
        self.no_ack_list = {}
        self.listening = False
        self.calculator =Calculator(Crc8.CCITT)

    def checksum(self, message):
        message_copy = message.copy()
        if "crc" in message_copy:
            message_copy['crc'] = ""
        data = json.dumps(message_copy, sort_keys=True).encode('utf-8')
        return self.calculator.checksum(data)
        
    def send_message(self, message, addr):
        message['crc'] = self.checksum(message)
        self.sock.sendto(json.dumps(message).encode(), addr)
        
    def listen(self):
        self.sock.bind((self.ip, self.port))
        self.listening = True
        while self.listening:
            data, addr = self.sock.recvfrom(1024)
            message = json.loads(data.decode())

            if self.checksum(message) != message['crc']:
                print(f"INFO: {message['device']} CORRUTPED DATA at {message['timestamp']}. REQUESTING DATA ")
                self.send_message({"type": "resend", "device": message['device'], "timestamp": int(time.time()),"crc": ""}, addr)
                continue
                
            if message['type'] == "registration":
                token = message['device'] + "-" + str(message['timestamp'])
                self.tokens[message['device']] = token
                print(f"INFO: {message['device']} REGISTERED at {message['timestamp']} ")
                self.send_message({"type": "token", "device": message['device'], "token": token, "timestamp": int(time.time()), "crc": ""}, addr)

            elif message['type'] == "data":
                if message['device'] not in self.tokens or message['token'] != self.tokens[message['device']]:
                    #print("wrong token gg")
                    self.send_message({"type": "invalid_token", "device": message['device'], "timestamp": int(time.time()), "crc": ""}, addr)
                    continue

                if  message['battery_low'] == False:
                    print(f"{message['timestamp']} - {message['device']} ")
                    print(" ".join([f"{k}: {v};" for k, v in message['data'].items()]))
                else:
                    print(f"{message['timestamp']} - WARNING: LOW BATTERY {message['device']} ")
                    print(" ".join([f"{k}: {v};" for k, v in message['data'].items()]))

                if message['device'] in self.no_ack_list and self.no_ack_list[message['device']] > 0:
                    self.no_ack_list[message['device']] -= 1
                    #print("not sending ack")
                else:
                    self.send_message({"type": "ack", "device": message['device'], "ack_time": message['timestamp'], "timestamp": int(time.time()),"crc": ""}, addr)
                    #print("sending ack")
                    
    def disable_ack(self):
        if 1:
            self.clear_screen()
            print("Select sensor:")
            print("1. ThermoNode")
            print("2. WindSense")
            print("3. RainDetect")
            print("4. AirQualityBox")
            choice = input("Choose: ")
            if choice == "1":
                self.no_ack_list["ThermoNode"] = 3
            elif choice == "2":
                self.no_ack_list["WindSense"] = 3
            elif choice == "3":
                self.no_ack_list["RainDetect"] = 3
            elif choice == "4":
                self.no_ack_list["AirQualityBox"] = 3
                
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
            print("3. Disable ACK")
            print("4. Exit")
            choice = input("Choose: ")
            if choice == "1":
                self.configure()
                time.sleep(1.5)
            elif choice == "2":
                if self.listening:
                    self.listening = False
                else:
                    threading.Thread(target=self.listen).start()
            elif choice == "3":
                self.disable_ack()
                time.sleep(1.5)
            elif choice == "4":
                exit()
                break

server = Server()
server.menu()
