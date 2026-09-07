import math

def to_km_coords(bs, ref_lat):
    lat_rad = math.radians(ref_lat)

    x = bs.x * 111 * math.cos(lat_rad)
    y = bs.y * 111

    return x, y

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