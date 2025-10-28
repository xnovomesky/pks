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
class Device:
    def __init__(self,type):
        self.type = type
        self.token = ""
        self.battery_low = False

class Tester:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = "127.0.0.1"
        self.port = 6666
        self.calculator =Calculator(Crc8.CCITT)
        self.devices = []
        self.devices.append(Device("ThermoNode"))
        self.devices.append(Device("WindSense"))
        self.devices.append(Device("RainDetect"))
        self.devices.append(Device("AirQualityBox"))
    
    def checksum(self, message):
        message_copy = message.copy()
        if "crc" in message_copy:
            message_copy['crc'] = ""
        data = json.dumps(message_copy, sort_keys=True).encode('utf-8')
        return self.calculator.checksum(data)
        
    def send_message(self, msg):
        msg['crc'] = self.checksum(msg)
        self.sock.sendto(json.dumps(msg).encode(), (self.ip, self.port))

    def generate_messages(self):
        print("Registering devices.")
        for device in self.devices:
            msg = {"type": "registration", "device": device.type, "timestamp": int(time.time()), "battery_low": False, "crc": ""}
            self.send_message(msg)
            data, addr = self.sock.recvfrom(1024)
            resp = json.loads(data.decode())
            if resp['type'] == "registration-token":
                device.token = resp['token']
        
        print("Started generating random messages.")
        while True:
            for device in self.devices:
                message = {"device": device.type,"type": "data", "token": device.token, "timestamp": int(time.time()), "battery_low": False, "data": "hi", "crc": ""}
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
            print("3. Custom Message")
            print("4. Exit")
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
