from trilateration.geometry import trilateration
import heapq
import json
import socket
from domain.base_station import BaseStation
from models.okomura_hata import OkomuraHata

class User:
    def __init__(self, height, gain, model=OkomuraHata(), x=None, y=None, bs_dict={}, pl_dict={}, rp_dict={}):
        self.x = x
        self.y = y
        self.height = height
        self.gain = gain
        self.model = model
        self.bs_dict = bs_dict
        self.pl_dict = {}
        self.rp_dict = {}
        self.connected_bs = None
        self.fallback = False

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "height": self.height,
            "gain": self.gain,
            "bs_dict": {k: v.to_dict() for k, v in self.bs_dict.items()},
            "pl_dict": self.pl_dict,
            "rp_dict": self.rp_dict
        }
    
    def from_dict(data):
        return User(
            x=data.get("x"),
            y=data.get("y"),
            height=data["height"],
            gain=data["gain"],
            bs_dict={k: BaseStation.from_dict(bs_data) for k, bs_data in data.get("bs_dict", {}).items()}
        )

    def get_position(self):
        self.get_radii(self.model)
        nbs, altbs = self.nearest_base_stations(3, self.model)
        result = trilateration(nbs, altbs) 
        return result
    
    def connect(self):
        if self.connected_bs is None:
            strongest_received_power_bs = max(self.rp_dict, key=self.rp_dict.get)
            self.connected_bs = self.bs_dict[strongest_received_power_bs]
        else:
            if len(self.connected_bs.neigh_bs) == 0:
                self.connected_bs.neigh_bs.find_neighbours(self.bs_dict)
            best_bs = None
            best_bs_rp = float('-inf')
            for bs in self.connected_bs.neigh_bs.get_neighbours(self.bs_dict):
                rp = self.rp_dict[bs.identifier]
                if rp > best_bs_rp:
                    best_bs = bs
                    best_bs_rp = rp
            self.connected_bs = best_bs

    def nearest_base_stations(self, quantity, model):
        radii_with_bs = [
            (model.distance(bs, self, True), bs)
            for bs in self.bs_dict.values()
        ]
        smallest = heapq.nsmallest(quantity, radii_with_bs, key=lambda x: x[0])
        nbs = [bs for _, bs in smallest]
        altbs = [bs for bs in self.bs_dict.values() if bs not in nbs]
        return nbs, altbs
            
    def get_radii(self, model):
        for bs in self.bs_dict.values():
            bs.distance = model.distance(bs, self, True)

    def receive_signal(self, host, port, ready_event, max_bs):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((host, port))
            server.listen()
            ready_event.set()

            received_count = 0
            while received_count < max_bs:
                conn, addr = server.accept()
                with conn:
                    data = conn.recv(4096)
                    bs_data = json.loads(data.decode("utf-8"))
                    self.bs_dict[(bs_data["identifier"])] = BaseStation(
                            identifier=bs_data["identifier"],
                            x=bs_data["x"],
                            y=bs_data["y"],
                            height=bs_data["height"],
                            frequency=bs_data["frequency"],
                            power=bs_data["power"],
                            gain=bs_data["gain"]
                        )
                    received_count += 1
    
    def recvall(self, sock, n):
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if packet == b'':
                return None
            if packet is None:
                return None
            data += packet
        return data

    def start(self, host, port):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            payload = json.dumps(self.to_dict()).encode("utf-8")
            size = len(payload)

            s.sendall(size.to_bytes(4, "big"))
            s.sendall(payload)

            size_data = self.recvall(s, 4)
            if size_data is None:
                raise RuntimeError("Server closed the connection without sending a response.")

            size = int.from_bytes(size_data, "big")

            data = self.recvall(s, size)
            if data is None:
                raise RuntimeError("Server closed the connection before sending all data.")

            self.rp_dict = json.loads(data)
            self.connect()
            self.x, self.y, self.fallback = self.get_position()
            return self.x, self.y, self.fallback
