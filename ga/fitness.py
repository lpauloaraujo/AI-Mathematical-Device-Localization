import math

def fitness(chromossome, measurements):
    error = 0

    for bs in measurements:
        d = math.hypot(
            chromossome.x - bs.x,
            chromossome.y - bs.y
        )

        error += (d - bs.distance) ** 2

    return error