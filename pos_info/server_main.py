import socket
import pickle

class ReceivedPowerServer:

    def __init__(self, host, port, model):
        self.host = host
        self.port = port    
        self.model = model

    def recvall(self, conn, n):
        data = b''
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if packet == b'':
                return None
            if packet is None:
                return None
            data += packet
        return data

    def start(self, ready_event=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()

            if ready_event:
                ready_event.set()

            print("Received Power Server waiting for connections...")

            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")

                while True:
                    size_data = self.recvall(conn, 4)
                    if size_data is None:
                        print("Connection closed by the client.")
                        break

                    size = int.from_bytes(size_data, 'big')
                    data = self.recvall(conn, size)
                    if data is None:
                        print("Client disconnected during transmission.")
                        break

                    user = pickle.loads(data)

                    rp_list = [self.model.received_power(bs, user, True) for bs in user.bs_list]

                    response = pickle.dumps(rp_list)
                    conn.sendall(len(response).to_bytes(4, 'big'))
                    conn.sendall(response)

                print("Received Power Server terminated.")
