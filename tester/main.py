import socket
import time
import os
import threading
import json
import random
from crc import Calculator, Crc8

class Device:
    def __init__(self,type):
        self.type = type
        self.token = ""
        self.battery_low = False
        self.last_message = ""
        self.last_message_ack = False

class Tester:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 0))
        self.ip = "127.0.0.1"
        self.port = 6666
        self.running = False
        self.calculator =Calculator(Crc8.CCITT)
        self.devices = []
        self.devices.append(Device("ThermoNode"))
        self.devices.append(Device("WindSense"))
        self.devices.append(Device("RainDetect"))
        self.devices.append(Device("AirQualityBox"))
    
    def checksum(self, message,fake = False):
        message_copy = message.copy()
        if "crc" in message_copy:
            message_copy['crc'] = ""
        data = json.dumps(message_copy, sort_keys=True).encode('utf-8')
        return self.calculator.checksum(data) if fake ==False else self.calculator.checksum(data+b"error :D")
        
    def send_message(self, message,error = False):
        message['crc'] = self.checksum(message,error)
        self.sock.sendto(json.dumps(message).encode(), (self.ip, self.port))

    def generate_messages(self):
        time.sleep(0.5)
        for device in self.devices:
            message = {"type": "registration", "device": device.type, "timestamp": int(time.time()), "battery_low": False, "crc": ""}
            self.send_message(message)
            time.sleep(0.2)
        self.running = True
        while self.running:
            for device in self.devices:
                if self.running:
                    data = {}
                    if device.type == "ThermoNode":
                        data = {"temperature": round(random.uniform(-50, 60), 1), "humidity": round(random.uniform(0, 100), 1), "dew_point": round(random.uniform(-50, 60), 1), "pressure": round(random.uniform(800, 1100), 2)}
                    elif device.type == "WindSense":
                        data = {"wind_speed": round(random.uniform(0, 50), 1), "wind_gust": round(random.uniform(0, 70), 1), "wind_direction": random.randint(0, 359), "turbulence": round(random.uniform(0, 1), 1)}
                    elif device.type == "RainDetect":
                        data = {"rainfall": round(random.uniform(0, 500), 1), "soil_moisture": round(random.uniform(0, 100), 1), "flood_risk": random.randint(0, 3), "rain_duration": random.randint(0, 60)}
                    elif device.type == "AirQualityBox":
                        data = {"co2": random.randint(300, 5000), "ozone": round(random.uniform(0, 500), 1), "air_quality_index": random.randint(0, 500)}

                    message = {"device": device.type,"type": "data", "token": device.token, "timestamp": int(time.time()), "battery_low": False, "data": data, "crc": ""}
                    device.last_message = message
                    self.send_message(message)
                    time.sleep(1)
                    while device.last_message_ack == False and self.running:
                        #print("didnt got ack, resending")
                        self.send_message(message)
                        time.sleep(1)
                    device.last_message_ack = False
            time.sleep(10)
            
    def custom_message(self):
        if 1:
            self.clear_screen()
            print("Select sensor:")
            print("1. ThermoNode")
            print("2. WindSense")
            print("3. RainDetect")
            print("4. AirQualityBox")
            choice = input("Choose: ")
          
            if choice == "1":
                device = next(d for d in self.devices if d.type == "ThermoNode")
            elif choice == "2":
                device = next(d for d in self.devices if d.type == "WindSense")
            elif choice == "3":
                device = next(d for d in self.devices if d.type == "RainDetect")
            elif choice == "4":
                device = next(d for d in self.devices if d.type == "AirQualityBox")
                
            self.clear_screen()
            print("Set low battery?")
            print("1. True")
            print("2. False")
            choice = input("Choose: ")
            if choice == "1":
                battery_low = True
            elif choice == "2":
                battery_low = False
                
            self.clear_screen()
            data = {}
            if device.type == "ThermoNode":
                data["temperature"] = float(input("temperature (-50.0 to 60.0): "))
                data["humidity"] = float(input("humidity (0.0 to 100.0): "))
                data["dew_point"] = float(input("dew_point (-50.0 to 60.0): "))
                data["pressure"] = float(input("pressure (800.00 to 1100.00): "))
            elif device.type == "WindSense":
                data["wind_speed"] = float(input("wind_speed (0.0 to 50.0): "))
                data["wind_gust"] = float(input("wind_gust (0.0 to 70.0): "))
                data["wind_direction"] = int(input("wind_direction (0 to 359): "))
                data["turbulence"] = float(input("turbulence (0.0 to 1.0): "))
            elif device.type == "RainDetect":
                data["rainfall"] = float(input("rainfall (0.0 to 500.0): "))
                data["soil_moisture"] = float(input("soil_moisture (0.0 to 100.0): "))
                data["flood_risk"] = int(input("flood_risk (0 to 3): "))
                data["rain_duration"] = int(input("rain_duration (0 to 60): "))
            elif device.type == "AirQualityBox":
                data["co2"] = int(input("co2 (300 to 5000): "))
                data["ozone"] = float(input("ozone (0.0 to 500.0): "))
                data["air_quality_index"] = int(input("air_quality_index (0 to 500): "))

            message = {"device": device.type,"type": "data", "token": device.token, "timestamp": int(time.time()), "battery_low": battery_low, "data": data, "crc": ""}
            self.send_message(message)
            print("Sending custom message")
            
    def test_error(self):
        if 1:
            self.clear_screen()
            print("Select sensor:")
            print("1. ThermoNode")
            print("2. WindSense")
            print("3. RainDetect")
            print("4. AirQualityBox")
            choice = input("Choose: ")
          
            if choice == "1":
                device = next(d for d in self.devices if d.type == "ThermoNode")
                data = {"temperature": round(random.uniform(-50, 60), 1), "humidity": round(random.uniform(0, 100), 1), "dew_point": round(random.uniform(-50, 60), 1), "pressure": round(random.uniform(800, 1100), 2)}
            elif choice == "2":
                device = next(d for d in self.devices if d.type == "WindSense")
                data = {"wind_speed": round(random.uniform(0, 50), 1), "wind_gust": round(random.uniform(0, 70), 1), "wind_direction": random.randint(0, 359), "turbulence": round(random.uniform(0, 1), 1)}
            elif choice == "3":
                device = next(d for d in self.devices if d.type == "RainDetect")
                data = {"rainfall": round(random.uniform(0, 500), 1), "soil_moisture": round(random.uniform(0, 100), 1), "flood_risk": random.randint(0, 3), "rain_duration": random.randint(0, 60)}
            elif choice == "4":
                device = next(d for d in self.devices if d.type == "AirQualityBox")
                data = {"co2": random.randint(300, 5000), "ozone": round(random.uniform(0, 500), 1), "air_quality_index": random.randint(0, 500)}
            
            message = {"device": device.type,"type": "data", "token": device.token, "timestamp": int(time.time()), "battery_low": False, "data": data, "crc": ""}
            device.last_message = message
            self.send_message(message,True)
            
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def configure(self):
        self.clear_screen()
        self.ip = input("Enter server IP (default 127.0.0.1): ") or "127.0.0.1"
        self.port = int(input("Enter server port (default 6666): ") or 6666)
        print(f"Configured to {self.ip}:{self.port}")

    def lissen(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            message = json.loads(data.decode())
            
            if message['type'] == "token":
                device = next(d for d in self.devices if d.type == message['device'])
                device.token = message['token']
                #print("recieved token:" ,message['token'])
            if message['type'] == "invalid_token":
                device = next(d for d in self.devices if d.type == message['device'])
                print("invalid token on device:",message['device'])
                message = {"type": "registration", "device": device.type, "timestamp": int(time.time()), "battery_low": False, "crc": ""}
                self.send_message(message)
            if message['type'] == "resend":
                device = next(d for d in self.devices if d.type == message['device'])
                self.send_message(device.last_message)
            if message['type'] == "ack":
                device = next(d for d in self.devices if d.type == message['device'])
                device.last_message_ack = True
                
    def menu(self):
        threading.Thread(target=self.lissen).start()
        while True:
            self.clear_screen()
            print("Tester Menu:")
            print("1. Configure IP/Port")
            print("2. Generate Messages", ("[Running]" if self.running else "[Stopped]"))
            print("3. Custom Message")
            print("4. Introduce Error")
            print("5. Exit")
            choice = input("Choose: ")
            if choice == "1":
                self.configure()
                time.sleep(1.5)
                self.clear_screen()
            elif choice == "2":
                if self.running:
                    self.running = False
                else:
                    threading.Thread(target=self.generate_messages).start()
            elif choice == "3":
                self.custom_message()
                time.sleep(1.5)
                self.clear_screen()
            elif choice == "4":
                self.test_error()
                time.sleep(1.5)
                self.clear_screen()
            elif choice == "5":
                exit()
                break

tester = Tester()
tester.menu()
