import math
import trilateration.geometry

def radical_axis(x1, y1, r1, x2, y2, r2):

    A = 2 * (x2 - x1)
    B = 2 * (y2 - y1)

    C = (
        x1**2 + y1**2 - r1**2
        - x2**2 - y2**2 + r2**2
    )

    return A, B, C

def line_intersection(A1, B1, C1, A2, B2, C2):

    det = A1 * B2 - A2 * B1

    if math.isclose(det, 0.0, abs_tol=1e-9):
        return None

    x = (B1 * C2 - B2 * C1) / det
    y = (C1 * A2 - C2 * A1) / det

    return (x, y)

def radical_center(bs_list):

    if len(bs_list) < 3:
        return None

    ref_lat = bs_list[0].y

    bs_km = []

    for bs in bs_list[:3]:

        x_km, y_km = trilateration.geometry.to_km_coords(bs)

        bs_km.append(
            (x_km, y_km, bs.distance)
        )

    x1, y1, r1 = bs_km[0]
    x2, y2, r2 = bs_km[1]
    x3, y3, r3 = bs_km[2]

    A1, B1, C1 = radical_axis(
        x1, y1, r1,
        x2, y2, r2
    )

    A2, B2, C2 = radical_axis(
        x1, y1, r1,
        x3, y3, r3
    )

    intersection = line_intersection(
        A1, B1, C1,
        A2, B2, C2
    )

    if intersection is None:
        return None

    x, y = intersection

    return (x, y)