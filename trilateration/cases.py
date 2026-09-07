from math import radians, sin, cos, sqrt, atan2

def identify_case(internal_spheres, intersecction_number, max_multiplicity):
    if internal_spheres == 0 and intersecction_number == 1:
        return "0"
    elif internal_spheres == 0 and intersecction_number == 6:
        return "1"
    elif internal_spheres == 1 and intersecction_number == 4:
        return "2"
    elif internal_spheres == 2 and intersecction_number == 2:
        return "3"
    elif internal_spheres == 2 and intersecction_number == 0:
        return "4"
    elif internal_spheres == 0 and intersecction_number == 4:
        if max_multiplicity == 3:
            return "0"
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
    elif internal_spheres == 0 and intersecction_number == 3:
        return "11"
    elif internal_spheres == 0 and intersecction_number == 5:
        return "12"
    elif internal_spheres == 1 and intersecction_number == 3:
        return "13"
    elif internal_spheres == 1 and intersecction_number == 5:
        return "14"
