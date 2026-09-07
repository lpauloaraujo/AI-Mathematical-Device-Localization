# The purpose of this code is to help create examples for trilateration
# by generating images of cases where it is possible to analyze whether the circles intersect.
# The result of the example below can be seen in the image circles.png.

import matplotlib.pyplot as plt

def draw_circles(xs, ys, raios, mean, std, user_x=None, user_y=None, estimated_x=None, estimated_y=None, ta=False):

    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')

    for x, y, r in zip(xs, ys, raios):
        circ = plt.Circle((x, y), r, fill=False, edgecolor='blue', linewidth=2)
        ax.add_patch(circ)
        ax.plot(x, y, 'ro')  

    # posição real do usuário
    if user_x is not None and user_y is not None:
        ax.plot(
            user_x,
            user_y,
            'go',
            markersize=10,
            label="Real User"
        )

    # posição estimada
    if estimated_x is not None and estimated_y is not None:
        ax.plot(
            estimated_x,
            estimated_y,
            'kx',
            markersize=10,
            markeredgewidth=2,
            label="Estimated User"
        )

    margem = max(raios) + 2

    # inclui usuário real e estimado no limite do gráfico
    all_x = xs.copy()
    all_y = ys.copy()

    if user_x is not None and user_y is not None:
        all_x.append(user_x)
        all_y.append(user_y)

    if estimated_x is not None and estimated_y is not None:
        all_x.append(estimated_x)
        all_y.append(estimated_y)

    ax.set_xlim(min(all_x) - margem, max(all_x) + margem)
    ax.set_ylim(min(all_y) - margem, max(all_y) + margem)

    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_title('Circles on the Plane')
    ax.grid(True)
    ax.legend()

    if ta:
        plt.savefig(f"circles_{mean}_{std}_ta.png")
    else:
        plt.savefig(f"circles_{mean}_{std}_rssi.png")
    plt.close()

if __name__ == "__main__":
    xs = [23, 23, 1, 22]
    ys = [17, 41, 15, 17]
    radii = [1, 1, 1, 1]
    draw_circles(xs, ys, radii)
