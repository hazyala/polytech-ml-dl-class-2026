"""Genetic algorithm starter example using a binary chromosome."""

import random


Chromosome = list[int]


def fitness(chromosome: Chromosome) -> int:
    return sum(chromosome)


def make_chromosome(size: int) -> Chromosome:
    return [random.randint(0, 1) for _ in range(size)]


def select(population: list[Chromosome]) -> Chromosome:
    a, b = random.sample(population, 2)
    return a if fitness(a) >= fitness(b) else b


def crossover(a: Chromosome, b: Chromosome) -> tuple[Chromosome, Chromosome]:
    point = random.randint(1, len(a) - 1)
    return a[:point] + b[point:], b[:point] + a[point:]


def mutate(chromosome: Chromosome, rate: float = 0.02) -> Chromosome:
    return [1 - bit if random.random() < rate else bit for bit in chromosome]


def run(generations: int = 30, population_size: int = 20, chromosome_size: int = 16) -> Chromosome:
    population = [make_chromosome(chromosome_size) for _ in range(population_size)]

    for generation in range(generations):
        next_population: list[Chromosome] = []
        while len(next_population) < population_size:
            child_a, child_b = crossover(select(population), select(population))
            next_population.extend([mutate(child_a), mutate(child_b)])
        population = sorted(next_population, key=fitness, reverse=True)[:population_size]
        print(f"generation={generation:02d} best={fitness(population[0])} {population[0]}")

    return population[0]


if __name__ == "__main__":
    random.seed(42)
    run()

