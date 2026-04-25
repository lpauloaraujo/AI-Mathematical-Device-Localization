import math
from itertools import combinations

def to_km_coords(bs, ref_lat):
    lat_rad = math.radians(ref_lat)

    x = bs.x * 111 * math.cos(lat_rad)
    y = bs.y * 111

    return x, y

#Testar em algum site que converte latitute e longitude em KM
def km_to_latlon(x, y, ref_lat):
    lat = y / 111
    lon = x / (111 * math.cos(math.radians(ref_lat)))
    return lon, lat

def distance_km(bs, md):
    lat_avg = math.radians((bs.y + md.y) / 2)

    dx = (bs.x - md.x) * 111 * math.cos(lat_avg)
    dy = (bs.y - md.y) * 111

    return math.hypot(dx, dy)

def distance_between_points(lat1, lon1, lat2, lon2):
    lat_avg = math.radians((lat1 + lat2) / 2)

    dx = (lon1 - lon2) * 111 * math.cos(lat_avg)
    dy = (lat1 - lat2) * 111

    return math.hypot(dx, dy)

def intersection_exists(r1, r2, d):
    sum_radii = r1 + r2
    diff_radii = abs(r1 - r2)

    if d > sum_radii and not math.isclose(d, sum_radii, rel_tol=1e-3, abs_tol=1e-3):
        return False
    
    if d < diff_radii and not math.isclose(d, diff_radii, rel_tol=1e-3, abs_tol=1e-3):
        return False
    
    if math.isclose(d, 0.0, rel_tol=1e-3, abs_tol=1e-3) and math.isclose(r1, r2, rel_tol=1e-3, abs_tol=1e-3):
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


def trilateration(bs_list, altbs):

    if len(bs_list) < 3:
        return None

    ref_lat = bs_list[0].y

    def build_km_list(bs_source):
        bs_km_local = []
        for bs in bs_source:
            x_km, y_km = to_km_coords(bs, ref_lat)
            bs_km_local.append((bs.identifier, x_km, y_km, bs.distance))
        return bs_km_local

    def get_intersections(bs_km_local):
        points = []
        for (id1, x0, y0, r0), (id2, x1, y1, r1) in combinations(bs_km_local, 2):
            pts = two_circles_intersection(x0, y0, r0, x1, y1, r1)
            points.extend(pts)
        return points
    
    bs_km = build_km_list(bs_list)
    all_points = get_intersections(bs_km)
    
    if not all_points and altbs:
        print("Fallback: substituindo estações por reservas...")

        n = len(bs_list)

        for k in range(1, min(n, len(altbs)) + 1):

            for remove_idx in combinations(range(n), k):

                remaining = [bs_list[i] for i in range(n) if i not in remove_idx]

                for replacement in combinations(altbs, k):

                    new_bs = remaining + list(replacement)

                    bs_km_alt = build_km_list(new_bs)
                    all_points = get_intersections(bs_km_alt)

                    if all_points:
                        print(f"Interseção encontrada substituindo {k} estação(ões)")
                        break

                if all_points:
                    break
            if all_points:
                break

    if not all_points:
        x_avg = sum(p[1] for p in bs_km) / len(bs_km)
        y_avg = sum(p[2] for p in bs_km) / len(bs_km)
        lon, lat = km_to_latlon(x_avg, y_avg, ref_lat)
        return (lon, lat, True)

    counted_points = []

    for p in all_points:
        found = False

        for item in counted_points:
            if close_points(p, item[0]):
                item[1] += 1
                found = True
                break

        if not found:
            counted_points.append([p, 1])

    best_point, _ = max(counted_points, key=lambda x: x[1])

    lon, lat = km_to_latlon(best_point[0], best_point[1], ref_lat)

    return (lon, lat, False)