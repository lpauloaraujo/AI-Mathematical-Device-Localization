import random

def tournament_selection(population, tournament_size=5):
    candidates = random.sample(population, tournament_size)

    return min(candidates, key=lambda chromossome: chromossome.fitness)

def select_parents(population, tournament_size=3):
    parent1 = tournament_selection(population, tournament_size)
    parent2 = tournament_selection(population, tournament_size)

    while parent1 == parent2:
        parent2 = tournament_selection(population, tournament_size)

    return parent1, parent2