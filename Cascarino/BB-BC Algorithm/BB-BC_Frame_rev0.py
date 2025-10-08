import random as rd

import time
import pprint
import openpyxl

from numpy import random
import matplotlib.pyplot as plt

import RFEM
from RFEM.enums import ObjectTypes
from RFEM.initModel import Model
from RFEM.BasicObjects.section import Section
from RFEM.BasicObjects.member import Member
from RFEM.Results.designOverview import *
from RFEM.Results.resultTables import ResultTables, ConvertResultsToListOfDct
from RFEM.Tools.GetObjectNumbersByType import GetObjectNumbersByType
from RFEM.Tools.centreOfGravityAndObjectInfo import ObjectsInfo

def get_section_data(order_of_data):
    # Location of modified section data file
    # Note that the naming of the profile needs to match that in RFEM
    path = "C:\\Users\\casca\\Desktop\Development\\RFEM_Python_Client\\Reference\Steel Profiles\\steel-profiles-south-africa.xlsx"

    wb_obj = openpyxl.load_workbook(path, data_only=True)
    sheet_obj = wb_obj.active

    # IPE and UBs
    # Position of data for IPEs and UBs in excel sheet
    start_row = 11
    end_row = 63

    I_section_data = []
    for i in range(start_row, end_row+1):
        cell_obj = sheet_obj.cell(row=i, column=5)
        if cell_obj.value != None:

            I_section_data.append({
                "name" : cell_obj.value,
                "mass" : float(sheet_obj.cell(row=i, column=6).value)
            })
    I_section_data = sorted(I_section_data, key= lambda d: d['mass'])

    # UCs
    # Position of data for UCs in excel sheet
    start_row = 80
    end_row = 101

    H_section_data = []
    for i in range(start_row, end_row+1):
        cell_obj = sheet_obj.cell(row=i, column=5)
        if cell_obj.value != None:

            H_section_data.append({
                "name" : cell_obj.value,
                "mass" : float(sheet_obj.cell(row=i, column=6).value)
            })
    H_section_data = sorted(H_section_data, key= lambda d: d['mass'])

    # CHSs
    # Position of data for CHSs in excel sheet
    start_row = 244
    end_row = 367

    # start_row = 277
    # end_row = 331

    CHS_section_data = []
    for i in range(start_row, end_row+1):
        cell_obj = sheet_obj.cell(row=i, column=5)
        if cell_obj.value != None:

            CHS_section_data.append({
                "name" : cell_obj.value,
                "mass" : round(float(sheet_obj.cell(row=i, column=6).value), 2)
            })
    CHS_section_data = sorted(CHS_section_data, key= lambda d: d['mass'])

    section_data = []
    for item in order_of_data:
        match item:
            case 'I-Sections':
                section_data.append(I_section_data)
            case 'H-Sections':
                section_data.append(H_section_data)
            case 'CHS':
                section_data.append(CHS_section_data)

    return section_data

def calculate_weights(genome: list, section_lib: list[list], length_per_sections: list[float], output_required: bool = True):
    weight  = 0
    for gene, length, sections in zip(genome, length_per_sections, section_lib):
            section_mass = sections[gene]["mass"]

            # Here I could add a check to see if this value is already greater than the total weight of the current optimum solution and I could potentially remove this item from the potential sections
            weight = weight + length * section_mass

    if output_required:
        print(f"Genome: {genome} Total Weight = {round(weight,2)} ")
    return round(weight,2)

def generate_genome(section_data: {list[list]}):
    return [rd.randint(0,len(section_list)-1) for section_list in section_data]

def initialize_population(population_size: int, section_data: list[list]):
    return [generate_genome(section_data) for _ in range(population_size)]

# -- Functions related to RFEM --
def connect_to_RFEM(file_name):
    model = RFEM.initModel.Model(False, model_name=file_name)
    print("Connected!")

def get_results() -> list:
    RFEM.initModel.Calculate_all()
    return ResultTables.SteelDesignDesignRatiosMembersBySection(True)

def run_structural_analysis(genome: list[int], section_lib: list[list]):
    print(f"Check genome: {genome}", end="...   ")
    begin = time.time()

    # Update the sections
    for gene, i, sections in zip(genome, range(len(genome)), section_lib):
        section_name = sections[gene]["name"]
        Section(no= i+1, name=section_name, material_no=1)

    RFEM.initModel.Calculate_all()
    elapsed = time.time() - begin
    print(f"...calculation took {round(elapsed,1)} seconds")
    return ResultTables.SteelDesignDesignRatiosMembersBySection(True)

def get_RFEM_geometry():
    # Check how this works for a section list with a blank in between
    # Might need to modify this using max(list_of_sections)
    list_of_members = GetObjectNumbersByType(ObjectTypes.E_OBJECT_TYPE_MEMBER)
    sections_in_model = GetObjectNumbersByType(ObjectTypes.E_OBJECT_TYPE_SECTION)

    # Set total length for each section to 0
    lengths = [0.0 for _ in range(len(sections_in_model))]

    for member in list_of_members:
        member_dict = Model.clientModel.service.get_member(member)
        lengths[member_dict["section_start"]-1] = lengths[member_dict["section_start"]-1] + member_dict["length"]

    return sections_in_model, lengths

def change_sections(sectionList: list, section_number: int):
    for section in sectionList:
        Section(no=section_number, name=section)

# End of functions related to RFEM --------------------------

def find_max_design_ratios(data: list) -> list:
    max_design_ratios = []
    for data_set, i in zip(data, range(len(data))):
        max_design_ratios.append([])
        section_count = -1
        for design_check in data_set:
            description = design_check['description']
            if isinstance(description, str):
                section_count = section_count + 1
                section_name = description.split(" | ")[0]
                max_design_ratios[i].append([section_name, float(section_count)+1, 0.0 ])
            else:
                design_ratio = design_check['design_ratio']
                if isinstance(design_ratio, str):
                    if design_ratio == "Non-designable":
                        print(f"Note that {section_name} is Class 4 and Non-designable for a specific case")
                else:
                    max_design_ratios[i][section_count][2] = max(max_design_ratios[i][section_count][2], round(design_ratio,2))
    return max_design_ratios

def get_min_weights(weights, max_design_ratios) -> float:
    min_weight_all = min(weights)
    min_weight_feas = max(weights)

    for weight, max_design_ratio in zip(weights, max_design_ratios):
        max_design_ratio_solution = 0
        for design_ratio in max_design_ratio:
            max_design_ratio_solution = max(max_design_ratio_solution, design_ratio[2])

        if ((max_design_ratio_solution <= 1.00) & (weight < min_weight_feas)):
            min_weight_feas = weight

    return min_weight_all, min_weight_feas

def penalised_objective(weight, max_design_ratios, min_weight_all, min_weight_feas) -> float:
    multiplier = 1
    feasible = True
    for design_ratio in max_design_ratios:
        if design_ratio[2] >1:
            multiplier = (multiplier + design_ratio[2])
            feasible = False
    if feasible:
        penalised_weight = weight
    else:
        penalised_weight = weight + (min_weight_feas-min_weight_all)*(multiplier)
    return penalised_weight

def fitness_function(min_weight, max_weight, penalised_weight) -> float:
    fitness = min_weight + max_weight - penalised_weight
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

def generate_new_point(cog, generation, section_data, alpha = 1.0, best_weight = 10000):
    new_point = []
    for cog_i,list in zip(cog,section_data):
        temp = int(round(cog_i + alpha*random.normal(0, 1)*len(list)/generation, 0))
        new_point.append(min(max(temp, 0), len(list)-1))
    return new_point

# Main Algorithm

# Need to later get user input to confirm the order of the section data in the list
# Test 1:
# section_data = get_section_data(['H-Sections', 'I-Sections'])

# Benchmarking Problem 1:
section_data = get_section_data(['CHS', 'CHS', 'CHS', 'CHS', 'CHS'])
# section_data = get_section_data(['CHS'])

connect_to_RFEM(file_name = "Benchmarking Problem 1")
sections_in_model, length_per_sections = get_RFEM_geometry()

# Parameters
population_size = 5
generations = 2
all_calculated = []
all_data = []
saved_iterations = 0

# Create population
population = initialize_population(population_size=population_size, section_data=section_data)

gens_without_improvement = 0
temp_optimimum = []

# Algorithm
for generation in range(1, generations):

    generation_data = []
    print(f"\nBeginning Calculation Generation: {generation}")
    for genome in population:
        # Check if the current arrangement has already been calculated to save computational time
        if genome in all_calculated:
            print(f"Genome {genome} already calculated")
            pos = all_calculated.index(genome)
            generation_data.append(all_data[pos])
            saved_iterations = saved_iterations + 1
        else:
            data = run_structural_analysis(genome = genome, section_lib=section_data)
            generation_data.append(data)
            all_data.append(data)
            all_calculated.append(genome)
    pprint.pprint(generation_data)

    max_design_ratios = []
    max_design_ratios = find_max_design_ratios(data=generation_data)
    pprint.pprint(max_design_ratios)

    weights = [calculate_weights(genome, section_data, length_per_sections, output_required=False) for genome in population]

    # Penalizing objectives
    min_weight_all, min_weight_feas = get_min_weights(weights=weights, max_design_ratios=max_design_ratios)
    penalised_weights = [penalised_objective(weight, max_design_ratio, min_weight_all=min_weight_all, min_weight_feas=min_weight_feas) for weight, max_design_ratio in zip(weights, max_design_ratios)]

    # Calculating weights of all
    max_weight = max(penalised_weights)
    min_weight = min(penalised_weights)

    fitnesses = [fitness_function(min_weight=min_weight, max_weight=max_weight, penalised_weight=penalised_weight) for penalised_weight in penalised_weights]

    # Determine center of gravity
    cog = determine_cog(population, fitnesses)

    sortedPopulation = [genome for _,genome in sorted(zip(fitnesses,population), reverse=True)]
    sortedPenalizedWeights = [weight for _,weight in sorted(zip(fitnesses,penalised_weights), reverse=True)]
    sortedWeights = [weight for _,weight in sorted(zip(fitnesses,weights), reverse=True)]

    # Debugging code ----------------------
    print("\nResults:")
    for genome, max_design_ratio, weight, penalised_weight, fit in zip(population, max_design_ratios, weights, penalised_weights, fitnesses):
        print(f"Genome: {genome}: || Design Ratios: {max_design_ratio}, || Weight: {round(weight,2)} || Penalized Weight: {round(penalised_weight,2)} || Fitness: {round(fit,2)}")
    # --------------------------------------
    # Checking if there is a change in the best solution from previous
    if sortedPopulation[0] == temp_optimimum:
        gens_without_improvement = gens_without_improvement + 1
    else:
        gens_without_improvement = 0
        temp_optimimum = sortedPopulation[0]

    # [0:1] only takes first value but it saves it as an array
    new_population = sortedPopulation[0:1]
    for _ in range(population_size-1):
        while True:
            temp_point = generate_new_point(cog=sortedPopulation[0], generation=generation, section_data=section_data)
            temp_weight = calculate_weights(temp_point, section_data, length_per_sections, output_required=False)
            if temp_weight < sortedPenalizedWeights[0]:
                break
        new_population.append(temp_point)
    population = new_population
    section_1, section_2 = [],[]
    for point in population:
        section_1.append(point[0])
        section_2.append(point[1])

    # plt.scatter(section_1, section_2)

    # # plot best point and cog
    # plt.scatter(cog[0], cog[1])
    # plt.scatter(population[0][0], population[0][1])

    # ax = plt.gca()
    # ax.set_xlim(-0.5,len(sorted_section_data[0])+0.5)
    # ax.set_ylim(-0.5,len(sorted_section_data[1])+0.5)
    # plt.show()

    # Print best fitness in this generation
    best_fitness = max(fitnesses)
    print(f"Generation {generation}, Best: {sortedPopulation[0]}, Weight: {round(sortedPenalizedWeights[0],2)}, Fitness: {round(best_fitness,2)}, Gens without improvement: {gens_without_improvement} ")

    if gens_without_improvement == 5:
        break

print(f"Number of analyses saved = {saved_iterations}")
