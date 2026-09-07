import random

from ga.ga_classes import Chromossome

AREA_WIDTH = 1000
AREA_HEIGHT = 1000


def generate_chromossomes(quantity, sample):
    chromossomes = []

    used_positions = set()
    bs_positions = {
        (bs.x, bs.y)
        for bs in sample.measurements
    }

    while len(chromossomes) < quantity:
        x = random.randint(0, AREA_WIDTH)
        y = random.randint(0, AREA_HEIGHT)

        position = (x, y)

        if position in used_positions:
            continue

        if position in bs_positions:
            continue

        used_positions.add(position)

        chromossomes.append(
            Chromossome(
                x=x,
                y=y
            )
        )

    return chromossomes