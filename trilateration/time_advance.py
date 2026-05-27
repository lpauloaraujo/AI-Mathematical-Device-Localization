import trilateration.geometry
import random

SPEED_OF_LIGHT = 299_792_458

def meters_per_ta(scs_khz):
    Tc = 1 / (480000 * 4096)

    mu_map = {
        15: 0,
        30: 1,
        60: 2,
        120: 3,
        240: 4
    }

    mu = mu_map.get(scs_khz)

    if mu is None:
        raise ValueError("Invalid SCS")

    ta_time = (16 * 64 * Tc) / (2 ** mu)

    distance = (SPEED_OF_LIGHT * ta_time) / 2

    return distance


def calculate_ta_distance(ta, scs_khz):
    step = meters_per_ta(scs_khz)
    return ta * step

def simulate_ta(
    lat1,
    lon1,
    lat2,
    lon2,
    identifier,
    possible_scs=(15, 30, 60),
    distance_error_std=20
):

    real_distance = trilateration.geometry.distance_between_points(
        lat1,
        lon1,
        lat2,
        lon2
    )

    scs = random.choice(possible_scs)

    error = random.gauss(0, distance_error_std)

    measured_distance = max(0, real_distance + error)

    step = meters_per_ta(scs)

    ta = round(measured_distance / step)

    return ta, scs, identifier
