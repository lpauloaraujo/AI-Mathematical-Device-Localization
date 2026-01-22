from utils.jsonmap import jsonmap
from rp_server import ReceivedPowerServer
from models.okomura_hata import OkomuraHata
import threading

HOST = "localhost"
PORT = 9090

def build_user_from_bs_signals():
    bs_list = jsonmap("bs", "data/bs.json")
    user = jsonmap("user", "data/mobile.json")

    ready = threading.Event()

    user_thread = threading.Thread(
        target=user.receive_signal,
        args=(HOST, PORT, ready, 3),
        daemon=True
    )
    user_thread.start()

    ready.wait()

    threads = []
    for bs in bs_list:
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


def estimate_user_position(user, model):
    user.model = model

    rp_server = ReceivedPowerServer(model)

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

    rp_server_thread.join()
    device_thread.join()


def main():
    model = OkomuraHata()
    user = build_user_from_bs_signals()
    estimate_user_position(user, model)


if __name__ == "__main__":
    main()
