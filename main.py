import csv
import math
import threading
import time
from utils.jsonmap import jsonmap
from rp_server import ReceivedPowerServer
from models.okomura_hata import OkomuraHata
from trilateration.geometry import distance_between_points

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

    device_thread.join()
    rp_server_thread.join()

    return (user.x, user.y)


def get_user_estimate_position(user, base_stations, model):
    complete_user = build_user_from_bs_signals(base_stations, user)
    user_estimate_position = estimate_user_position(complete_user, model)


    return (user_estimate_position, user.connected_bs if user.connected_bs else None)

def format_float(x):
    return f"{x:.10f}" if x is not None else ""

def main():
    model = OkomuraHata()
    base_stations = jsonmap("bs", "data/generated_bs.json")
    users = jsonmap("user", "data/generated_users.json")

    table_path = "data/trilateration_results_table.csv"

    with open(table_path, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=";")

        writer.writerow([
            "lat real", "long real",
            "server", "rssi",
            "Neighbor 1", "rssi",
            "Neighbor 2", "rssi",
            "lat calc", "long calc",
            "Erro (%)", "fallback"
        ])

        for user in users:

            real_X, real_Y = user.x, user.y

            estimated_position, connected_bs = get_user_estimate_position(
                user, base_stations, model
            )

            est_X, est_Y = estimated_position

            sorted_bs = sorted(
                user.rp_dict.items(),
                key=lambda x: x[1], 
                reverse=True
            )

            server_id = connected_bs.identifier if connected_bs else None
            server_rssi = user.rp_dict[server_id]

            neighbors = [
                (bs_id, rssi)
                for bs_id, rssi in sorted_bs
                if bs_id != server_id
            ][:3]

            while len(neighbors) < 3:
                neighbors.append((None, None))

            if est_X is None or est_Y is None:
                error_percent = None
            else:
                error_km = distance_between_points(real_X, real_Y, est_X, est_Y)

                MAX_ERROR_KM = 1  
                error_percent = (error_km / MAX_ERROR_KM) * 100

            writer.writerow([
                real_X, real_Y,
                server_id, server_rssi,
                neighbors[0][0], format_float(neighbors[0][1]),
                neighbors[1][0], format_float(neighbors[1][1]),
                format_float(est_X), format_float(est_Y),
                format_float(error_percent), user.fallback
            ])

    print(f"Resultados salvos em {table_path}")

if __name__ == "__main__":
    main()