import os
import threading
from rp_server import ReceivedPowerServer
from models.okomura_hata import OkomuraHata
from trilateration.geometry import distance_between_points
from collections import defaultdict

from utils.txtmap import save_ga_info
from utils.visual import draw_circles

HOST = "localhost"
PORT = 9090


def build_user_from_bs_signals(base_stations, user):
    ready = threading.Event()

    user_thread = threading.Thread(
        target=user.receive_signal,
        args=(HOST, PORT, ready, 3)
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


def estimate_user_position(user, model, solution):
    user.model = model
    user.solution = solution

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

    return (user.x, user.y, user.case)


def get_user_estimate_position(user, base_stations, model, solution):
    complete_user = build_user_from_bs_signals(base_stations, user)
    user_estimate_position = estimate_user_position(complete_user, model, solution)


    return (user_estimate_position, user.connected_bs if user.connected_bs else None)

def format_float(x):
    return f"{x:.10f}" if x is not None else ""

def main(base_stations, users, mean, std, noise_times, solution, timestamp):
    model = OkomuraHata()
    case_errors = defaultdict(list)
    null_cases = 0
    a = 0

    ga_file = os.path.join(
            "data",
            "ga",
            f"ga_info_{timestamp}_{mean}_{std}_{noise_times}.txt"
        )
    
    for i, user in enumerate(users, start=1):

        real_X, real_Y = user.x, user.y

        estimated_position, connected_bs = get_user_estimate_position(
            user, base_stations, model, solution
        )

        est_X, est_Y, case = estimated_position

        #if solution == 9:
            #print(f"User {i}: Real Position: ({format_float(real_X)}, {format_float(real_Y)}), "
            #      f"Estimated Position: ({format_float(est_X)}, {format_float(est_Y)}), "
            #      f"Case: {case}")

        if solution == 4:
            save_ga_info(ga_file, user, real_X, real_Y)

        error_metros = (
            distance_between_points(real_X, real_Y, est_X, est_Y)
        )

        if user.case is None:
            null_cases += 1
        else:
            case_errors[str(user.case)].append(error_metros)
        a += 1

        #ta_distance = [(bs.ta_distance) for bs in user.bs_dict.values()]
        #bs_distance = {"bs" + bs.identifier + "_distance": bs.distance * 1000 for bs in user.bs_dict.values()}
        #print("real_x:", real_X, "real_y:", real_Y, "est_x:", est_X, "est_y:", est_Y, "bs_distance:", bs_distance, "ta_distance:", ta_distance, "noise_dict:", user.noise_dict)
        #print("Error (meters):", error_metros)
        #draw_circles([bs.x for bs in user.bs_dict.values()], [bs.y for bs in user.bs_dict.values()], [bs.distance * 1000 for bs in user.bs_dict.values()], mean, std, user_x=real_X, user_y=real_Y, ta=False)
        #draw_circles([bs.x for bs in user.bs_dict.values()], [bs.y for bs in user.bs_dict.values()], [bs.ta_distance * 1000 for bs in user.bs_dict.values()], mean, std, user_x=real_X, user_y=real_Y, ta=True)

    return case_errors

if __name__ == "__main__":
    main(0, 6, 10, 0, 4)
