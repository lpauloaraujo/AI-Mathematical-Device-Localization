import os
import re

from domain.base_station import BaseStation
from utils.jsonmap import jsonmap
from utils.txtmap import txtmap_users


def run_experiment(timestamp):

    experiment_folder = os.path.join(
        "data",
        "info",
        f"experiment_{timestamp}"
    )

    users = txtmap_users(
    os.path.join(
        experiment_folder,
        "users.txt"
        )
    )

    bs_file = os.path.join(
        experiment_folder,
        "base_stations.txt"
    )

    with open(bs_file, "r") as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            scenario, data = line.split(": ", 1)

            numbers = list(map(
                int,
                re.findall(r"=(\d+)", data)
            ))

            base_stations = [
                BaseStation(identifier="1", x=numbers[0], y=numbers[1], height=30, frequency=900, power=20, gain=15),
                BaseStation(identifier="2", x=numbers[2], y=numbers[3], height=30, frequency=900, power=20, gain=15),
                BaseStation(identifier="3", x=numbers[4], y=numbers[5], height=30, frequency=900, power=20, gain=15),
            ]

            yield scenario, base_stations, users