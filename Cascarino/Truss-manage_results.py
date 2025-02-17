import json, pprint
import matplotlib.pyplot as plt
import numpy as np
import math

def get_results_from_text(path) -> str:
    f = open(path, "r")
    return f.read()

def convert_text_to_dict(results: str) -> dict:
    return json.loads(results)

def get_results_from_json(path):
    with open(path) as file:
        return json.load(file)

def filter_results(results) -> list:
    for dataset in results:
        for check in dataset:
            # to complete
            break
    return []

def find_max_design_ratios(data: list) -> list:
    filtered_results = []
    for data_set, i in zip(data, range(len(data))):
        filtered_results.append([])
        section_count = -1
        for design_check in data_set:
            description = design_check['description']
            if isinstance(description, str):
                section_count = section_count + 1
                section_name = description.split(" | ")[0]
                filtered_results[i].append([section_name, float(section_count)+1, 0.0 ])
            else:
                design_ratio = design_check['design_ratio']
                if isinstance(design_ratio, str):
                    if design_ratio == "Non-designable":
                        print(f"Note that {section_name} is Class 4 and Non-designable for a specific case")
                else:
                    filtered_results[i][section_count][2] = max(filtered_results[i][section_count][2], round(design_ratio,2))
    return filtered_results

# Main Code
results = get_results_from_json("Cascarino\\larger_results.json")
sections_with_max_ratios = find_max_design_ratios(results)

section_1_names = []
section_1_masses = []
section_1_design_ratios = []

section_2_names = []
section_2_masses = []
section_2_design_ratios = []

section_3_names = []
section_3_masses = []
section_3_design_ratios = []


for result_set, i in zip(sections_with_max_ratios, range(len(sections_with_max_ratios))):
    for section in result_set:
        if section[1] == 1.0:
            section_1_names.append(section[0])
            section_1_masses.append(float((section_1_names[i].split("x"))[2]))
            section_1_design_ratios.append(section[2])
        if section[1] == 2.0:
            section_2_names.append(section[0])
            section_2_masses.append(float((section_2_names[i].split("x"))[2]))
            section_2_design_ratios.append(section[2])
        if section[1] == 3.0:
            section_3_names.append(section[0])
            #use better variables
            temp = (section_3_names[i].split(" "))[1]
            temp2 = temp.split("x")
            dia = float(temp2[0])
            t = float(temp2[1])
            area = math.pi*(dia**2-(dia-2*t)**2)/4
            section_3_masses.append(area*7850/1000/1000)
            section_3_design_ratios.append(section[2])

# plt.scatter(section_1_masses, section_1_design_ratios)
# plt.show()

# print(section_1_names)
# print(section_1_masses)

# print(section_2_names)
# print(section_2_masses)

fig, axs = plt.subplots(1,3, sharey='row')
ax1,ax2,ax3 = axs

fig.suptitle('Mass vs design ratios')

ax1.scatter(section_1_masses, section_1_design_ratios)
ax2.scatter(section_2_masses, section_2_design_ratios)
ax3.scatter(section_3_masses, section_3_design_ratios)

ax1.set_title('Section 1')
ax1.set_xlabel('Mass')
ax1.set_ylabel('Design Ratios')
ax1.set_yticks([0.25, 0.50,0.75, 1.00, 1.25, 1.50, 1.75, 2.00])

# Removes duplicates, problematic for example 203x133x25 = 305x165x25
# ax1.set_xticks(list(dict.fromkeys(section_1_masses)), list(dict.fromkeys(section_1_names)), rotation='vertical')

ax1.set_xticks(section_1_masses, section_1_names, rotation='vertical')
ax1.grid()

ax2.set_title('Section 2')
ax2.set_xlabel('Mass')
ax2.set_xticks(section_2_masses, section_2_names, rotation='vertical')
ax2.grid()

ax3.set_title('Section 3')
ax3.set_xlabel('Mass')
ax3.set_xticks(section_3_masses, section_3_names, rotation='vertical')
ax3.grid()

plt.show()