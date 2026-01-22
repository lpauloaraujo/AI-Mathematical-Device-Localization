import socket
import json
from domain.user import User
from domain.base_station import BaseStation

class ReceivedPowerServer:

    def __init__(self, model):  
        self.model = model

    def recvall(self, conn, n):
        data = b''
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def start(self, host, port, ready_event=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen()

            if ready_event:
                ready_event.set()

            print("[RP_SERVER] Received Power Server waiting for connections...")
            print()

            conn, addr = s.accept()
            with conn:
                print(f"[RP_SERVER] Connected by {addr}")
                print()

                while True:
                    size_data = self.recvall(conn, 4)
                    if size_data is None:
                        print("[RP_SERVER] Connection closed by the client.")
                        print()
                        break

                    size = int.from_bytes(size_data, "big")

                    data = self.recvall(conn, size)
                    if data is None:
                        print("[RP_SERVER] Client disconnected during transmission.")
                        print()
                        break

                    user_data = json.loads(data.decode("utf-8"))

                    user = User(
                        x=user_data.get("x"),
                        y=user_data.get("y"),
                        height=user_data["height"],
                        gain=user_data["gain"]
                    )

                    user.bs_dict = {
                        bs_data["identifier"]: BaseStation.from_dict(bs_data)
                        for bs_data in user_data["bs_dict"].values()
                    }

                    rp_dict = {
                        bs.identifier: self.model.received_power(bs, user, True)
                        for bs in user.bs_dict.values()
                    }

                    response = json.dumps(rp_dict).encode("utf-8")
                    conn.sendall(len(response).to_bytes(4, "big"))
                    conn.sendall(response)

                print("[RP_SERVER] Received Power Server terminated.")
                print()
