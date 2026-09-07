import os
import re
from domain.base_station import BaseStation
from domain.user import User
from domain.user import User

def txtmap(filename):
    bss = []
    users = []

    reading_bs = False
    reading_users = False

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            if line == "=== BASE STATIONS ===":
                reading_bs = True
                reading_users = False
                continue

            if line == "=== USERS ===":
                reading_bs = False
                reading_users = True
                continue

            if not line:
                continue

            if reading_bs:
                left, right = line.split(":")
                identifier = left.split()[1]

                parts = right.split(",")

                x = float(parts[0].split("=")[1])
                y = float(parts[1].split("=")[1])

                bss.append(
                    BaseStation(
                        identifier=identifier,
                        x=x,
                        y=y,
                        height=30,
                        gain=15,
                        frequency=900,
                        power=40
                    )
                )

            elif reading_users:
                parts = line.split(",")

                x = float(parts[0].split("=")[1])
                y = float(parts[1].split("=")[1])

                users.append(
                    User(
                        x=x,
                        y=y,
                        height=1.5,
                        gain=0
                    )
                )

    return bss, users

def txtmap_users(path):

    users = []

    with open(path, "r") as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            match = re.match(
                r"USER \d+: x=(\d+), y=(\d+)",
                line
            )

            if not match:
                continue

            x, y = match.groups()

            user = User(
                x=int(x),
                y=int(y),
                height=1.5,
                gain=0
            )

            user.bs_dict = {}
            user.pl_dict = {}
            user.rp_dict = {}
            user.noise_dict = {}

            users.append(user)

    return users

def save_ga_info(path, user, real_X, real_Y):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "a") as file:
        values = [real_X, real_Y]

        for bs in sorted(user.bs_dict.values(), key=lambda bs: bs.identifier):
            values.extend([
                bs.x,
                bs.y,
                user.rp_dict[bs.identifier]
                #bs.distance * 1000
            ])

        values.append(user.case)

        file.write(";".join(map(str, values)) + "\n")
