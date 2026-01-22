import math
import json
import socket

class BaseStation:
    def __init__(self, identifier, x, y, height, frequency, power, gain):
        self.identifier = identifier
        self.x = x
        self.y = y
        self.height = height
        self.frequency = frequency
        self.power = power
        self.gain = gain
        self.distance = None

        self.neigh_bs = []

    def to_dict(self):
        return {
            "identifier": self.identifier,
            "x": self.x,
            "y": self.y,
            "height": self.height,
            "frequency": self.frequency,
            "power": self.power,
            "gain": self.gain
        }
    
    def from_dict(data):
        return BaseStation(
            identifier=data["identifier"],
            x=data["x"],
            y=data["y"],
            height=data["height"],
            frequency=data["frequency"],
            power=data["power"],
            gain=data["gain"]
        )

    def find_neighbours(self, bs_dict):
        for possible_neighbour in bs_dict.values():
            distance = math.sqrt((possible_neighbour.x - self.x)**2 + (possible_neighbour.y - self.y)**2)
            if distance < 5000:
                self.neigh_bs.append(possible_neighbour)

    def get_neighbours(self, bs_dict):
        if len(self.neigh_bs) == 0:
            self.find_neighbours(bs_dict)
        return self.neigh_bs
    
    def send_signal(self, host, port):
        data_json = json.dumps(self.to_dict())

        for _ in range(5):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    s.sendall(data_json.encode("utf-8"))
                    return 
            except ConnectionRefusedError:
                import time
                time.sleep(0.1)
