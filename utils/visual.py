# The purpose of this code is to help create examples for trilateration
# by generating images of cases where it is possible to analyze whether the circles intersect.
# The result of the example below can be seen in the image circles.png.

import matplotlib.pyplot as plt

def draw_circles(xs, ys, raios):

    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')

    for x, y, r in zip(xs, ys, raios):
        circ = plt.Circle((x, y), r, fill=False, edgecolor='blue', linewidth=2)
        ax.add_patch(circ)
        ax.plot(x, y, 'ro')  

    margem = max(raios) + 2
    ax.set_xlim(min(xs) - margem, max(xs) + margem)
    ax.set_ylim(min(ys) - margem, max(ys) + margem)

    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_title('Circles on the Plane')
    ax.grid(True)
    plt.savefig("circles.png")

xs = [23, 23, 1, 22]
ys = [17, 41, 15, 17]
radii = [1, 1, 1, 1]
draw_circles(xs, ys, radii)
