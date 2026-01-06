# This code implements all the mathematical functions required for the trilateration process.

import math
from itertools import combinations

def intersection_exists(first_radius, second_radius, circuferences_distance):
    sum_radii = first_radius + second_radius
    diff_radii = abs(first_radius - second_radius)

    if circuferences_distance > sum_radii and not math.isclose(circuferences_distance, sum_radii, rel_tol=1e-9, abs_tol=1e-9):
        return False
    
    if circuferences_distance < diff_radii and not math.isclose(circuferences_distance, diff_radii, rel_tol=1e-9, abs_tol=1e-9):
        return False
    
    if math.isclose(circuferences_distance, 0.0, rel_tol=1e-9, abs_tol=1e-9) and math.isclose(first_radius, second_radius, rel_tol=1e-9, abs_tol=1e-9):
        return False

    return True


def two_circles_intersection(x0, y0, first_radius, x1, y1, second_radius):
    import math

    circuferences_distance = math.hypot(x1 - x0, y1 - y0)

    if intersection_exists(first_radius, second_radius, circuferences_distance):
        a = (first_radius**2 - second_radius**2 + circuferences_distance**2) / (2 * circuferences_distance)
        h = math.sqrt(max(0, first_radius**2 - a**2))  

        x3 = x0 + a * (x1 - x0) / circuferences_distance
        y3 = y0 + a * (y1 - y0) / circuferences_distance

        rx = -(y1 - y0) * (h / circuferences_distance)
        ry =  (x1 - x0) * (h / circuferences_distance)

        p1 = (round(x3 + rx, 10), round(y3 + ry, 10))
        p2 = (round(x3 - rx, 10), round(y3 - ry, 10))

        if h == 0:
            return [p1]
        else:
            return [p1, p2]
        
    return []


def close_points(p1, p2, tol=1e-6):
    return math.isclose(p1[0], p2[0], abs_tol=tol) and math.isclose(p1[1], p2[1], abs_tol=tol)

#aqqui
def trilateration(bs_list):

    bs_pairs = list(combinations(bs_list, 2))
    all_points = []
    for pair in bs_pairs:
        intersection_points = two_circles_intersection(pair[0].x, pair[0].y, pair[0].distance, pair[1].x, pair[1].y, pair[1].distance)
        if len(intersection_points) > 0:
            all_points.extend(intersection_points)

    if not all_points:
        return None

    counted_points = []

    for p in all_points:
        found = False

        for item in counted_points:
            rep_point, count = item

            if close_points(p, rep_point):
                item[1] += 1
                found = True
                break

        if not found:
            counted_points.append([p, 1])

    best_point, _ = max(counted_points, key=lambda x: x[1])

    return best_point
    
