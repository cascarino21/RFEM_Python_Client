import random as rd
import math
from typing import List

from numpy import random
import matplotlib.pyplot as plt

# Parameters
population_size = 10
generations = 5
applied_moment = 140

Diams = [6, 8, 10, 12, 16, 20, 25, 32, 40]
Spacing = [75, 100, 125, 150, 175, 200, 225, 250]

def generate_genome() :
    return [rd.randint(0,len(Diams)-1), rd.randint(0,len(Spacing)-1)]

def initialize_population(population_size: int) :
    return [generate_genome() for _ in range(population_size)]

def calc_capacity(genome) -> List:
    concrete_cube_strength: int = 20
    cover: int = 30
    width: int = 1000
    height: int = 200
    diam: int = Diams[genome[0]]
    spacing: int = Spacing[genome[1]]
    number_bars: float = round(width/spacing,2)
    d: float = height - cover - diam/2
    area_steel: float = (1000/spacing)*math.pi*diam*diam/4
    N_s: float = area_steel*435
    x_u: float = N_s / (width*concrete_cube_strength*0.75)
    z: float = d - 7/18*x_u
    bending_capacity = N_s*z*10**(-6)
    return [diam, spacing, height, round(area_steel), round(bending_capacity,2)]

def get_min_areas(areas, utilizations) -> float:
    min_area_all = min(areas)
    min_area_feas = max(areas)
    for area, util in zip(areas, utilizations):
        if util <= 1 & area < min_area_feas:
            min_area_feas = area
    return min_area_all, min_area_feas

def penalised_objective(area, utilization, min_area_all, min_area_feas) -> float:
    if utilization <=1:
        return area
    return area + (min_area_feas-min_area_all)*(utilization)

def fitness_function(min_area, max_area, area) -> float:
    fitness = min_area + max_area - area
    return fitness

def determine_cog(population, fitnesses) -> tuple:
    sigma_x, sigma, cog = [], [], []
    num_parameters = len(population[0])
    for _ in range(num_parameters):
        sigma_x.append(0)
        sigma.append(0)

    for genome, fitness in zip(population, fitnesses):
        for i in range(num_parameters):
            sigma_x[i] = sigma_x[i] + fitness*genome[i]
            sigma[i] = sigma[i] + fitness

    for sigma_x_i, sigma_i in zip(sigma_x, sigma):
        cog.append(sigma_x_i/sigma_i)
    return cog

def generate_new_point(cog, generation, data, alpha = 1.0):
    new_point = []
    for cog_i,list in zip(cog,data):
        temp = int(round(cog_i + alpha*random.normal(0, 1)*len(list)/generation, 0))
        new_point.append(min(max(temp, 0), len(list)-1))
    return new_point

# Main Algorithm
population = initialize_population(population_size=population_size)

applied_moment_input = int(input("Applied moment (in kNm):"))

for generation in range(1, generations):

    data = [calc_capacity(genome) for genome in population]
    diams = []
    spacings = []
    heights = []
    areas = []
    capacities = []
    utilizations = []

    for item in data:
        diams.append(item[0])
        spacings.append(item[1])
        heights.append(item[2])
        areas.append(item[3])
        capacities.append(item[4])
        utilizations.append(applied_moment_input/item[4])

    # Penalizing objectives
    min_area_all, min_area_feas = get_min_areas(areas=areas, utilizations=utilizations)
    areas = [penalised_objective(area, util, min_area_all=min_area_all, min_area_feas=min_area_feas) for area, util in zip(areas, utilizations)]

    max_area = max(areas)
    min_area = min(areas)

    fitnesses = [fitness_function(min_area=min_area, max_area=max_area, area=area) for area in areas]

    # Determine center of gravity
    cog = determine_cog(population, fitnesses)

    sortedPopulation = [genome for _,genome in sorted(zip(fitnesses,population), reverse=True)]
    sortedUtilization = [utilization for _,utilization in sorted(zip(fitnesses,utilizations), reverse=True)]
    sortedAreas = [area for _,area in sorted(zip(fitnesses,areas), reverse=True)]

    # # Debugging code ----------------------

    for pop, util, area, fit, diam, spac in zip(population, utilizations, areas, fitnesses, diams, spacings):
        print(f"Pop: {pop}: Ø{diam}-{spac}, UC: {round(util,2)}, area: {round(area,2)}, fitness: {round(fit,2)}")
    print("\n")
    # --------------------------------------

    new_population = sortedPopulation[0:1]

    for _ in range(population_size-1):
        new_population.append(generate_new_point(cog = cog, generation=generation, data=[Diams, Spacing]))
    population = new_population
    diams = [point[0] for point in new_population]
    spacings = [point[1] for point in new_population]

    plt.scatter(diams, spacings)

    # plot best point and cog
    plt.scatter(cog[0], cog[1])
    plt.scatter(population[0][0], population[0][1])

    ax = plt.gca()
    ax.set_xlim(0,len(Diams))
    ax.set_ylim(0,len(Spacing))
    plt.show()

    # Print best fitness in this generation
    best_fitness = max(fitnesses)
    print(f"Generation {generation}, with: Ø{Diams[sortedPopulation[0][0]]}-{Spacing[sortedPopulation[0][1]]} Reinf. area: {round(sortedAreas[0],2)}, UC: {round(sortedUtilization[0],2)}, Fitness: {round(best_fitness,2)}")


