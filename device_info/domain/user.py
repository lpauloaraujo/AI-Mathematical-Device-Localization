from pos_info.trilateration.geometry import trilateration
import heapq
import json
import socket
from device_info.domain.base_station import BaseStation
from pos_info.models.okomura_hata import OkomuraHata

class User:
    def __init__(self, height, gain, model=OkomuraHata(), x=None, y=None, n_bs=3, bs_list=[None] * 3):
        self.x = x
        self.y = y
        self.height = height
        self.gain = gain
        self.model = model
        self.bs_list = [None] * n_bs
        self.pl_list = [None] * n_bs
        self.rp_list = [None] * n_bs
        self.connected_bs = None

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "height": self.height,
            "gain": self.gain,
            "bs_list": [bs.to_dict() for bs in self.bs_list],
            "pl_list": self.pl_list,
            "rp_list": self.rp_list
        }
    
    def from_dict(data):
        return User(
            x=data.get("x"),
            y=data.get("y"),
            height=data["height"],
            gain=data["gain"],
            bs_list=[BaseStation.from_dict(bs_data) for bs_data in data.get("bs_list", [])]
        )

    def get_position(self):
        self.get_radii(self.model)
        nbs = self.nearest_base_stations(3, self.model)
        new_x, new_y = trilateration(nbs)
        return (new_x, new_y)
    
    def connect(self):
        if self.connected_bs is None:
            strongest_received_power_bs = self.rp_list.index(max(self.rp_list))
            self.connected_bs = self.bs_list[strongest_received_power_bs]
        else:
            if len(self.connected_bs.neigh_bs) == 0:
                self.connected_bs.neigh_bs.find_neighbours(self.bs_list)
            best_bs = None
            best_bs_rp = float('-inf')
            for bs in self.connected_bs.neigh_bs.get_neighbours(self.bs_list):
                rp = self.rp_list[bs.identifier]
                if rp > best_bs_rp:
                    best_bs = bs
                    best_bs_rp = rp
            self.connected_bs = best_bs

    def nearest_base_stations(self, quantity, model):
        radii_with_bs = [
            (model.distance(bs, self, True), bs)
            for bs in self.bs_list
        ]
        
        smallest = heapq.nsmallest(quantity, radii_with_bs, key=lambda x: x[0])
        
        return [bs for _, bs in smallest]
            
    def get_radii(self, model):
        for i in range(len(self.bs_list)):
            self.bs_list[i].distance = model.distance(self.bs_list[i], self, True)

    def receive_signal(self, host, port, ready_event, max_bs):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((host, port))
            server.listen()

            print("[USER] Server ready.")
            ready_event.set()

            received_count = 0
            while received_count < max_bs:
                conn, addr = server.accept()
                with conn:
                    data = conn.recv(4096)
                    bs_data = json.loads(data.decode("utf-8"))
                    print("[USER] Received Signal:", bs_data)
                    self.bs_list[int(bs_data["identifier"])] = BaseStation(
                            identifier=bs_data["identifier"],
                            x=bs_data["x"],
                            y=bs_data["y"],
                            height=bs_data["height"],
                            frequency=bs_data["frequency"],
                            power=bs_data["power"],
                            gain=bs_data["gain"]
                        )
                    received_count += 1
