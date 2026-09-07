import threading

from domain.base_station import BaseStation
from domain.user import User
from rp_server import ReceivedPowerServer
from models.okomura_hata import OkomuraHata
from utils.visual import draw_circles

user = User(x=750, y=460, height=1.5, gain=0)

bs_list = []

bs_list.append(BaseStation(x=946, y=80, identifier="1", height=30, gain=15, frequency=900, power=20))
bs_list.append(BaseStation(x=423, y=324, identifier="2", height=30, gain=15, frequency=900, power=20))
bs_list.append(BaseStation(x=174, y=585, identifier="3", height=30, gain=15, frequency=900, power=20))
bs_list.append(BaseStation(x=991, y=597, identifier="4", height=30, gain=15, frequency=900, power=20))

user.noise_dict = {
    str(identifier): 0
    for identifier in range(1, 4)
}

HOST = "localhost"
PORT = 9090

def build_user_from_bs_signals(base_stations, user):
    ready = threading.Event()

    user_thread = threading.Thread(
        target=user.receive_signal,
        args=(HOST, PORT, ready, 4)
    )
    user_thread.start()

    ready.wait()

    threads = []

    for bs in base_stations:
        t = threading.Thread(
            target=bs.send_signal,
            args=(HOST, PORT)
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    user_thread.join()

    return user

def estimate_user_position(user, model, mean, std, times, solution):
    user.model = model
    user.solution = solution

    rp_server = ReceivedPowerServer(model, mean, std, times)

    rp_server_ready = threading.Event()

    rp_server_thread = threading.Thread(
        target=rp_server.start,
        args=(HOST, PORT, rp_server_ready)
    )

    device_thread = threading.Thread(
        target=user.start,
        args=(HOST, PORT)
    )

    rp_server_thread.start()

    rp_server_ready.wait()

    device_thread.start()

    device_thread.join()
    rp_server_thread.join()

    return (user.x, user.y, user.case)


result = build_user_from_bs_signals(bs_list, user)

model = OkomuraHata()
tuple = estimate_user_position(user, model=model, mean=0, std=0, times=0, solution=0)

draw_circles(
    xs=[bs.x for bs in bs_list],
    ys=[bs.y for bs in bs_list],
    raios=[bs.distance * 1000 for bs in user.bs_dict.values()]
)

