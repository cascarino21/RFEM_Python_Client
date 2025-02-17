import time
import json
import math, random
import pprint

import RFEM
from RFEM.BasicObjects.section import Section
from RFEM.Results.designOverview import *
from RFEM.Results.resultTables import ResultTables, ConvertResultsToListOfDct

sectionList = ['HEB 100', 'HEB 120','HEB 140', 'HEB 160',  'HEB 180', 'HEB 200', 'HEB 220']

column_list = ['UC 152x152x23', 'UC 152x152x30' , 'UC 152x152x37' ,
              'UC 203x203x46', 'UC 203x203x52' , 'UC 203x203x60' , 'UC 203x203x71' , 'UC 203x203x86' ,
              'UC 254x254x73', 'UC 254x254x89' , 'UC 254x254x107', 'UC 254x254x132', 'UC 254x254x167',
              'UC 305x305x97', 'UC 305x305x118', 'UC 305x305x137', 'UC 305x305x158', 'UC 305x305x198', 'UC 305x305x240' ]
beam_list = ['UB 203x133x25', 'UB 203x133x30',
            'UB 254x146x31', 'UB 254x146x37', 'UB 254x146x43' ,
            'UB 305x102x25', 'UB 305x102x28', 'UB 305x102x33' ,
            'UB 305x165x40', 'UB 305x165x46', 'UB 305x165x54' ,
            'UB 356x171x45', 'UB 356x171x51', 'UB 356x171x57' , 'UB 356x171x67' ,
            'UB 406x140x39', 'UB 406x140x46',
            'UB 406x178x54', 'UB 406x178x60', 'UB 406x178x67' , 'UB 406x178x74' ,
            'UB 457x191x67', 'UB 457x191x74', 'UB 457x191x82' , 'UB 457x191x89' , 'UB 457x191x98',
            'UB 533x210x82', 'UB 533x210x92', 'UB 533x210x101', 'UB 533x210x109', 'UB 533x210x122']

chord_list = ['CHS 48.4x2.5','CHS 48.4x3','CHS 48.4x3.5','CHS 48.4x4',
              'CHS 60.3x2.5','CHS 60.3x3','CHS 60.3x3.5','CHS 60.3x4','CHS 60.3x4.5',
              'CHS 63.5x2.5','CHS 63.5x3','CHS 63.5x3.5','CHS 63.5x4','CHS 63.5x4.5',
              'CHS 76.2x2.5','CHS 76.2x3','CHS 76.2x3.5','CHS 76.2x4','CHS 76.2x4.5','CHS 76.2x5','CHS 76.2x6',
              'CHS 88.9x2.5','CHS 88.9x3','CHS 88.9x3.5','CHS 88.9x4','CHS 88.9x4.5','CHS 88.9x5','CHS 88.9x6',
              'CHS 101.6x2.5','CHS 101.6x3','CHS 101.6x3.5','CHS 101.6x4','CHS 101.6x4.5','CHS 101.6x5','CHS 101.6x6']

reducedColumnList = ['UC 152x152x23', 'UC 203x203x52', 'UC 254x254x89', 'UC 305x305x137']
reducedBeamList = ['UB 203x133x25', 'UB 305x165x40', 'UB 356x171x51', 'UB 406x178x67', 'UB 457x191x89', 'UB 533x210x122']

def connect_to_RFEM():
    model = RFEM.initModel.Model(False, model_name="Model - Truss.rf6")
    print("Connected!")

def create_full_population(section1List, section2List):
    population = []
    for i in range(len(section1List)):
        for j in range(len(section2List)):
            population.append([i, j])
    return population

# Later on I can modify this to take any number of sections as inputs
def create_random_population(section_1_list: list, section_2_list: list, section_3_list: list, percentage: int):
    n_section_1 = int((percentage/100) * len(section_1_list))
    n_section_2 = int((percentage/100) * len(section_2_list))
    n_section_3 = int((percentage/100) * len(section_3_list))
    n = n_section_1 * n_section_2 - n_section_3

    # For first test -------------
    # n = 5
    # ----------------------------

    print(n)
    population = []
    for _ in range(n):
        population.append([random_section(section_1_list), random_section(section_2_list), random_section(section_3_list)])

    return population

def random_section(section_list):
    n = len(section_list)
    return random.randint(0,n-1)


def change_sections(sectionList: list, section_number: int):
    for section in sectionList:
        Section(no=section_number, name=section)

def get_results() -> list:
    RFEM.initModel.Calculate_all()
    # Get design ratios
    return ResultTables.SteelDesignDesignRatiosMembersBySection(True)

def results_to_file(results) -> None:
    with open('Cascarino\\test.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=3)


# GA
def genetic_algotithm(population):
    count = 1
    results = []
    for genome in population:
        print(f"Check genome #{count}")
        begin = time.time()
        # Update the sections
        column = column_list[genome[0]]
        beam = beam_list[genome[1]]
        chord = chord_list[genome[2]]
        Section(no= 1, name=column, material_no=1, comment='Columns')
        Section(no= 2, name=beam, material_no=1, comment= 'Beams')
        Section(no= 3, name=chord, material_no=1, comment= 'Chord')
        results.append(get_results())

        elapsed = time.time() - begin
        print(f"Genome #{count} took {round(elapsed,1)} seconds")
        count = count +1

    results_to_file(results)
    # memberList = []
    # memberCount = -1
    # UCs = []
    # for data in results:
    #     for item in data:
    #         if isinstance(item['description'], str):
    #             memberList.append(item)
    #             memberCount = memberCount+1
    #             UCs.append([])
    #         else:
    #             UCs[memberCount].append(round(item['design_ratio'],2))

    #     for member in memberList:
    #         print(member)

    #     for UC in UCs:
    #         print(max(UC))

# def get_results_from_file():
#     with open('results.txt') as file:
#         results = file.read()

#     print(type(results))

#     dict = json.loads(results)
#     print(dict)
#     print(type(dict))

# Running code and test code

population = create_random_population(section_1_list=column_list , section_2_list= beam_list, section_3_list=chord_list, percentage=25)

connect_to_RFEM()
genetic_algotithm(population=population)

# get_results_from_file()