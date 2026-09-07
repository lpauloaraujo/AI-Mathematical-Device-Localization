import random

from ga.ga_classes import Chromossome

AREA_WIDTH = 1000
AREA_HEIGHT = 1000

def arithmetic_crossover(parent1, parent2):
    alpha = random.random()

    child1 = Chromossome(
        x=alpha * parent1.x + (1 - alpha) * parent2.x,
        y=alpha * parent1.y + (1 - alpha) * parent2.y
    )

    child2 = Chromossome(
        x=(1 - alpha) * parent1.x + alpha * parent2.x,
        y=(1 - alpha) * parent1.y + alpha * parent2.y
    )

    return child1, child2

import random

def gaussian_mutation(chromossome, mutation_rate=0.1, sigma=20):
    if random.random() < mutation_rate:
        chromossome.x += random.gauss(0, sigma)
        chromossome.y += random.gauss(0, sigma)
        
        chromossome.x = max(0, min(AREA_WIDTH, chromossome.x))
        chromossome.y = max(0, min(AREA_HEIGHT, chromossome.y))

    return chromossome