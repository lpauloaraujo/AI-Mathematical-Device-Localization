from math import radians, sin, cos, sqrt, atan2

def identify_case(internal_spheres, intersecction_number):
    if internal_spheres == 0 and intersecction_number == 6:
        return "1"
    elif internal_spheres == 1 and intersecction_number == 4:
        return "2"
    elif internal_spheres == 2 and intersecction_number == 2:
        return "3"
    elif internal_spheres == 2 and intersecction_number == 0:
        return "4"
    elif internal_spheres == 0 and intersecction_number == 4:
        return "5"
    elif internal_spheres == 1 and intersecction_number == 2:
        return "6"
    elif internal_spheres == 3 and intersecction_number == 0:
        return "7"
    elif internal_spheres == 0 and intersecction_number == 2:
        return "8"
    elif internal_spheres == 1 and intersecction_number == 0:
        return "9"
    elif internal_spheres == 0 and intersecction_number == 0:
        return "10"
    
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def count_containments(c1, c2, c3):

    circles = [c1, c2, c3]
    count = 0

    for i in range(3):
        lat1, lon1, r1 = circles[i]

        for j in range(i + 1, 3):
            lat2, lon2, r2 = circles[j]

            d = haversine(lat1, lon1, lat2, lon2)

            if d + r1 <= r2:
                count += 1

            elif d + r2 <= r1:
                count += 1

    return count