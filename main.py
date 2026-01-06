from utils.jsonmap import jsonmap

bs_list = jsonmap("bs", "data/bs.json")
user = jsonmap("user", "data/mobile.json")

import threading
import time

host = "localhost"
port = 9090

ready = threading.Event()

user_thread = threading.Thread(
        target=user.receive_signal,
        args=(host, port, ready, 3),
        daemon=True
    )

user_thread.start()

ready.wait()

time.sleep(0.1)

threads = []
for bs in bs_list:
    t = threading.Thread(
        target=bs.send_signal,
        args=(host, port)
    )
    t.start()
    threads.append(t)

for t in threads:
        t.join()

time.sleep(0.5)

user_thread.join(timeout=1)

from device_info.device_main import Device
from pos_info.server_main import ReceivedPowerServer
from pos_info.models.okomura_hata import OkomuraHata
import threading

model = OkomuraHata()

HOST = '127.0.0.2'
PORT = 65470

device = Device(host, 65470, user, model)
rp_server = ReceivedPowerServer(host, 65470, model)

rp_server_ready = threading.Event()

rp_server_thread = threading.Thread(target=rp_server.start, args=(rp_server_ready,))
device_thread = threading.Thread(target=device.start)

rp_server_thread.start()
rp_server_ready.wait()
device_thread.start()
