import sys
import os
import json
import random
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from domain.base_station import BaseStation
from domain.user import User

AREA_WIDTH = 1000 
AREA_HEIGHT = 1000  

MIN_DISTANCE = 300

def noise(mean=0, stddev=6, times=10, fixed_value=None):
    if fixed_value:
        return stddev
    total_noise = 0
    for _ in range(times):
        total_noise += random.gauss(mean, stddev)
    if times != 0:
        return total_noise/times
    else:
        return 0
        
def generate_bs(num_bs=3, users=None):
    if users is None:
        users = []
    bss = []
    while len(bss) < num_bs:
        x = random.randint(0, AREA_WIDTH)
        y = random.randint(0, AREA_HEIGHT)

        if all(((x - bs.x)**2 + (y - bs.y)**2)**0.5 >= MIN_DISTANCE for bs in bss):
            if any(x == user.x and y == user.y for user in users):
                continue
            bss.append(
                BaseStation(
                    identifier=str(len(bss) + 1),
                    x=x,
                    y=y,
                    height=30,
                    gain=15,
                    frequency=900,
                    power=20
                )
            )
    return bss

def generate_users(num_users=100000):
    users = []

    for _ in range(num_users):

        x = random.randint(0, AREA_WIDTH)
        y = random.randint(0, AREA_HEIGHT)

        user = User(
            x=x,
            y=y,
            height=1.5,
            gain=0,
        )

        users.append(user)

    return users

def apply_noise(users, mean, stddev, times, fixed_value=False, same_for_all_bs=False):

    for user in users:

        if same_for_all_bs:
            noise_value = noise(mean, stddev, times, fixed_value)
            user.noise_dict = {
                str(identifier): noise_value
                for identifier in range(1, 4)
            }
        else:

            user.noise_dict = {
                str(identifier): noise(mean, stddev, times, fixed_value)
                for identifier in range(1, 4)
            }

    return users

def save_bs_json(bss, filename='data/generated_bs.json'):
    with open(filename, 'w') as f:
        json.dump([bs.to_dict() for bs in bss], f, indent=4)

def save_users_json(users, filename='data/generated_users.json'):
    with open(filename, 'w') as f:
        json.dump([user.to_dict() for user in users], f, indent=4)

def save_bs_txt(bss, folder):
    with open(os.path.join(folder, "base_stations.txt"), "w") as f:
        for bs in bss:
            f.write(
                f"BS {bs.identifier}: "
                f"x={bs.x}, y={bs.y}\n"
            )

def save_users_txt(users, folder):
    with open(os.path.join(folder, "users.txt"), "w") as f:
        for i, user in enumerate(users, start=1):

            noise_info = ", ".join(
                f"noise_bs{bs_id}={noise}"
                for bs_id, noise in sorted(user.noise_dict.items(), key=lambda x: int(x[0]))
            )

            f.write(
                f"USER {i}: "
                f"x={user.x}, y={user.y}, {noise_info}\n"
            )

def append_scenario_bs_txt(bss, experiment_folder, scenario):
    filename = os.path.join(experiment_folder, "base_stations.txt")

    with open(filename, "a") as f:
        line = f"scenario_{scenario:03d}: "

        line += ", ".join(
            f"bs{bs.identifier}_x={bs.x}, bs{bs.identifier}_y={bs.y}"
            for bs in sorted(bss, key=lambda bs: int(bs.identifier))
        )

        f.write(line + "\n")

def save_info_txt(bss, users, timestamp=None):
    os.makedirs("data/info", exist_ok=True)

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
    filename = f"data/info/info_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write("=== BASE STATIONS ===\n")

        for bs in bss:
            f.write(
                f"BS {bs.identifier}: "
                f"x={bs.x}, y={bs.y}\n"
            )

        f.write("\n=== USERS ===\n")

        for i, user in enumerate(users, start=1):
            f.write(
                f"USER {i}: "
                f"x={user.x}, y={user.y}\n"
            )

    print(f"Informações salvas em {filename}")

def generate_experiment(num_scenarios=30, num_users=10000, mean=0, stddev=6, noise_times=10):

    timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S_%f")

    experiment_folder = os.path.join(
        "data",
        "info",
        f"experiment_{timestamp}"
    )

    os.makedirs(experiment_folder, exist_ok=True)

    users = generate_users(num_users)

    save_users_txt(users, experiment_folder)

    for scenario in range(1, num_scenarios + 1):

        bss = generate_bs(num_bs=3, users=users)

        append_scenario_bs_txt(
            bss,
            experiment_folder,
            scenario
        )

    return timestamp
