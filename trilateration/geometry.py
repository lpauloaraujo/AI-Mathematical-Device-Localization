import math
from itertools import combinations
import random

from trilateration.radical_axis import radical_center
from trilateration.time_advance import calculate_ta_distance
from trilateration.cases import identify_case
from utils.solmap import solution_map

def to_km_coords(bs):
    x_km = bs.x / 1000
    y_km = bs.y / 1000
    return x_km, y_km

def distance_between_points(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def distance_km(bs, md):
    dx = (bs.x - md.x) / 1000
    dy = (bs.y - md.y) / 1000
    return math.hypot(dx, dy)

def intersection_exists(r1, r2, d):
    sum_radii = r1 + r2
    diff_radii = abs(r1 - r2)

    if d > sum_radii and not math.isclose(d, sum_radii, rel_tol=1e-6, abs_tol=1e-6):
        return False
    
    if d < diff_radii and not math.isclose(d, diff_radii, rel_tol=1e-6, abs_tol=1e-6):
        return False
    
    if math.isclose(d, 0.0, rel_tol=1e-6, abs_tol=1e-6) and math.isclose(r1, r2, rel_tol=1e-6, abs_tol=1e-6):
        return False

    return True


def two_circles_intersection(x0, y0, r0, x1, y1, r1):
    d = math.hypot(x1 - x0, y1 - y0)

    if d == 0:
        return []

    if not intersection_exists(r0, r1, d):
        return []

    a = (r0**2 - r1**2 + d**2) / (2 * d)
    h = math.sqrt(max(0, r0**2 - a**2))

    x2 = x0 + a * (x1 - x0) / d
    y2 = y0 + a * (y1 - y0) / d

    rx = -(y1 - y0) * (h / d)
    ry =  (x1 - x0) * (h / d)

    p1 = (x2 + rx, y2 + ry)
    p2 = (x2 - rx, y2 - ry)

    if h == 0:
        return [p1]
    else:
        return [p1, p2]


def close_points(p1, p2, tol=1e-3):  
    return math.isclose(p1[0], p2[0], abs_tol=tol) and math.isclose(p1[1], p2[1], abs_tol=tol)

def calibrate_distances_by_ta(tasc, bs_list, altbs):

    ta_distance_km = (
        calculate_ta_distance(tasc[0], tasc[1]) / 1000
    )

    reference_bs = None

    for bs in bs_list:
        if bs.identifier == tasc[2]:
            reference_bs = bs
            break

    if reference_bs is None:
        for alt_bs in altbs:
            if alt_bs.identifier == tasc[2]:
                reference_bs = alt_bs
                break

    if reference_bs is None:
        raise ValueError(
            f"Base station {tasc[2]} não encontrada."
        )

    delta_km = (
        ta_distance_km
        - reference_bs.distance
    )

    calibrated_distances = {}

    for bs in bs_list:
        calibrated_distances[bs.identifier] = (
            bs.distance + delta_km
        )

    for alt_bs in altbs:
        calibrated_distances[alt_bs.identifier] = (
            alt_bs.distance + delta_km
        )

    return calibrated_distances

def clamp(point):
    x, y = point

    x = max(0.0, min(x, 1.0))
    y = max(0.0, min(y, 1.0))

    return (x, y)

def get_closest_point_by_quantity(all_points):
    counted_points = []

    AREA_WIDTH_KM = 1.0
    AREA_HEIGHT_KM = 1.0

    for p in all_points:

        x, y = p

        if x < 0 or x > AREA_WIDTH_KM or y < 0 or y > AREA_HEIGHT_KM:

            continue

        found = False

        for item in counted_points:
            if close_points(p, item[0]):
                item[1] += 1
                found = True
                break

        if not found:
            counted_points.append([p, 1])

    if counted_points:
        best_point, _ = max(counted_points, key=lambda item: item[1])
        return best_point

    closest = min(
        all_points,
        key=lambda p: (
            max(0, -p[0], p[0] - AREA_WIDTH_KM) ** 2
            + max(0, -p[1], p[1] - AREA_HEIGHT_KM) ** 2
        )
    )

    return clamp(closest)

def get_closest_point_by_avg(all_points):
    x_avg = sum(p[0] for p in all_points) / len(all_points)
    y_avg = sum(p[1] for p in all_points) / len(all_points)
    return (x_avg, y_avg)

def trilateration(bs_list, altbs, tasc, solution):

    if len(bs_list) < 3:
        return None

    ref_lat = bs_list[0].y

    def build_km_list(bs_source):
        bs_km_local = []
        for bs in bs_source:
            x_km = bs.x / 1000
            y_km = bs.y / 1000
            bs_km_local.append((bs.identifier, x_km, y_km, bs.distance))
        return bs_km_local

    def get_intersections(bs_km_local):
        points = []
        for (id1, x0, y0, r0), (id2, x1, y1, r1) in combinations(bs_km_local, 2):
            pts = two_circles_intersection(x0, y0, r0, x1, y1, r1)
            points.extend(pts)
        return points
    
    bs_km = build_km_list(bs_list)

    internal_spheres = count_containments_bs(bs_list)

    intersection_number, max_multiplicity = count_intersections(bs_km)

    case_id = identify_case(
        internal_spheres,
        intersection_number,
        max_multiplicity
    )

    trilateration_method, choice_method = solution_map(solution)

    if trilateration_method == 0:
        all_points = get_intersections(bs_km)
    elif trilateration_method == 1:
        ta_distances_dict = calibrate_distances_by_ta(tasc, bs_list, altbs)
        
        ta_km = []
        for bs in bs_list:
            if bs.identifier in ta_distances_dict:
                x_km = bs.x / 1000
                y_km = bs.y / 1000
                ta_km.append((bs.identifier, x_km, y_km, ta_distances_dict[bs.identifier]))
                
        all_points = get_intersections(ta_km)
    
    new_bs = bs_list

    if not all_points and altbs:

        n = len(bs_list)

        for k in range(1, min(n, len(altbs)) + 1):

            for remove_idx in combinations(range(n), k):

                remaining = [bs_list[i] for i in range(n) if i not in remove_idx]

                for replacement in combinations(altbs, k):
    
                    new_bs = remaining + list(replacement)

                    bs_km_alt = build_km_list(new_bs)
                    all_points = get_intersections(bs_km_alt)

                    if all_points:
                        break

                if all_points:
                    break
            if all_points:
                break

    if not all_points:
        rc = radical_center(new_bs)

        if rc is not None:
            x, y = rc
            return (x, y, True, new_bs, case_id)
        else:
            x_avg = sum(p[1] for p in bs_km) / len(bs_km)
            y_avg = sum(p[2] for p in bs_km) / len(bs_km)
        return (x_avg, y_avg, True, new_bs, case_id)
#    
    if choice_method == 0:
        best_point = get_closest_point_by_avg(all_points)
    elif choice_method == 1:
        best_point = random.choice(all_points)
    elif choice_method == 2:
        x, y = radical_center(new_bs)
        return (x, y, False, new_bs, case_id)
    elif choice_method == 3:
        best_point = get_closest_point_by_quantity(all_points)

    return (best_point[0] * 1000, best_point[1] * 1000, False, new_bs, case_id)

def count_intersections(bs_km):

    all_points = []

    for (_, x0, y0, r0), (_, x1, y1, r1) in combinations(bs_km, 2):

        pts = two_circles_intersection(
            x0, y0, r0,
            x1, y1, r1
        )

        all_points.extend(pts)

    counted_points = []

    for p in all_points:

        found = False

        for item in counted_points:

            if close_points(p, item["point"]):
                item["count"] += 1
                found = True
                break

        if not found:
            counted_points.append({
                "point": p,
                "count": 1
            })

    intersection_number = len(counted_points)

    max_multiplicity = max(
        (item["count"] for item in counted_points),
        default=0
    )

    return intersection_number, max_multiplicity

def count_containments_bs(bs_list):
    count = 0

    for bs1, bs2 in combinations(bs_list, 2):

        d = distance_between_points(
            bs1.x, bs1.y,
            bs2.x, bs2.y
        )

        if d/1000 + bs1.distance < bs2.distance:
            count += 1

        elif d/1000 + bs2.distance < bs1.distance:
            count += 1

    return count

def build_ta_km_list(bs_source, ta_map, ref_lat):

    ta_dict = {
        identifier: (ta, scs)
        for ta, scs, identifier in ta_map
    }

    bs_km_local = []

    for bs in bs_source:

        if bs.identifier not in ta_dict:
            continue

        x_km, y_km = to_km_coords(bs)

        ta, scs = ta_dict[bs.identifier]

        radius_km = calculate_ta_distance(ta, scs) / 1000

        bs.ta_distance = radius_km

        bs_km_local.append(
            (bs.identifier, x_km, y_km, radius_km)
        )

    return bs_km_local