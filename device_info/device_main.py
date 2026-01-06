import data
import socket
import pickle

from device_info.domain.base_station import BaseStation
from device_info.domain.user import User

from pos_info.models.okomura_hata import OkomuraHata

class Device:
    def __init__(self, host, port, user, model):
        self.host = host
        self.port = port
        self.user = user
        self.model = model

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

    def start(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))

            payload = pickle.dumps(self.user)
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

            self.user.rp_list = pickle.loads(data)
            self.user.connect()
            print("Connected Base Station: ", self.user.connected_bs.identifier)
            print("Connected Base Station's neighbours: ", [bs.identifier for bs in self.user.connected_bs.get_neighbours(self.user.bs_list)])
            self.user.x, self.user.y = self.user.get_position()

        print(f"User's Updated Position: {self.user.x, self.user.y}")
