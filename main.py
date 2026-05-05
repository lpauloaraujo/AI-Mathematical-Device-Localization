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


def estimate_user_position(user, model, mean, std, times):
    user.model = model

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

    return (user.x, user.y)


def get_user_estimate_position(user, base_stations, model, mean, std, times):
    complete_user = build_user_from_bs_signals(base_stations, user)
    user_estimate_position = estimate_user_position(complete_user, model, mean, std, times)


    return (user_estimate_position, user.connected_bs if user.connected_bs else None)

def format_float(x):
    return f"{x:.10f}" if x is not None else ""

def main(mean, std, noise_times):
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
            "Erro (metros)", "fallback"
        ])

        for user in users:

            real_X, real_Y = user.x, user.y

            estimated_position, connected_bs = get_user_estimate_position(
                user, base_stations, model, mean, std, noise_times
            )

            est_X, est_Y = estimated_position

            sorted_bs = sorted(
                user.trilateration_bs,
                key=lambda bs: user.rp_dict.get(bs.identifier, 0), 
                reverse=True
            )

            error_metros = distance_between_points(real_X, real_Y, est_X, est_Y) * 1000

            writer.writerow([
                real_X, real_Y,
                sorted_bs[0].identifier, user.rp_dict.get(sorted_bs[0].identifier, 0),
                sorted_bs[1].identifier, format_float(user.rp_dict.get(sorted_bs[1].identifier, 0)),
                sorted_bs[2].identifier, format_float(user.rp_dict.get(sorted_bs[2].identifier, 0)),
                format_float(est_X), format_float(est_Y),
                error_metros, user.fallback
            ])

    print(f"Resultados salvos em {table_path}")

if __name__ == "__main__":
    main(0, 6, 5)  

#fazer tabela mostrando em médio o erro para cada valor de desvio padrão
#fazer vários testes com diferentes valores de desvio padrão e comparar os resultados 