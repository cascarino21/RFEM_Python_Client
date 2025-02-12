import time
import json

import RFEM
from RFEM.BasicObjects.section import Section
from RFEM.Results.designOverview import *
from RFEM.Results.resultTables import ResultTables, ConvertResultsToListOfDct

sectionList = ['HEB 100', 'HEB 120','HEB 140', 'HEB 160',  'HEB 180', 'HEB 200', 'HEB 220']

columnList = ['UC 152x152x23', 'UC 152x152x30' , 'UC 152x152x37' ,
              'UC 203x203x46', 'UC 203x203x52' , 'UC 203x203x60' , 'UC 203x203x71' , 'UC 203x203x86' ,
              'UC 254x254x73', 'UC 254x254x89' , 'UC 254x254x107', 'UC 254x254x132', 'UC 254x254x167',
              'UC 305x305x97', 'UC 305x305x118', 'UC 305x305x137', 'UC 305x305x158', 'UC 305x305x198', 'UC 305x305x240' ]
beamList = ['UB 203x133x25', 'UB 203x133x30', 
            'UB 254x146x31', 'UB 254x146x37', 'UB 254x146x43' , 
            'UB 305x102x25', 'UB 305x102x28', 'UB 305x102x33' , 
            'UB 305x165x40', 'UB 305x165x46', 'UB 305x165x54' , 
            'UB 356x171x45', 'UB 356x171x51', 'UB 356x171x57' , 'UB 356x171x67' ,
            'UB 406x140x39', 'UB 406x140x46',
            'UB 406x178x54', 'UB 406x178x60', 'UB 406x178x67' , 'UB 406x178x74' ,
            'UB 457x191x67', 'UB 457x191x74', 'UB 457x191x82' , 'UB 457x191x89' , 'UB 457x191x98',
            'UB 533x210x82', 'UB 533x210x92', 'UB 533x210x101', 'UB 533x210x109', 'UB 533x210x122'] 

reducedColumnList = ['UC 152x152x23', 'UC 203x203x52', 'UC 254x254x89', 'UC 305x305x137']
reducedBeamList = ['UB 203x133x25', 'UB 305x165x40', 'UB 356x171x51', 'UB 406x178x67', 'UB 457x191x89', 'UB 533x210x122']

def connect_to_RFEM():
    model = RFEM.initModel.Model(False, model_name="Model.rf6")
    print("Connected!")

def create_full_population(section1List, section2List):
    population = []
    for i in range(len(section1List)):
        for j in range(len(section2List)):
            population.append([i, j])
    return population


def change_sections(sectionList: list, section_number: int):
    for section in sectionList:
        Section(no=section_number, name=section)

# GA
def genetic_algotithm(population):
    count = 1
    results = []
    for genome in population:
        print(f"Check genome #{count}")
        begin = time.time()
        # Update the sections
        column = columnList[genome[0]]
        beam = beamList[genome[1]]
        Section(no= 1, name=column, material_no=1, comment='Columns')
        Section(no= 2, name=beam, material_no=1, comment= 'Beams')

        # Calculate model
        RFEM.initModel.Calculate_all()

        # Get design ratios
        results.append(ResultTables.SteelDesignDesignRatiosMembersBySection(True))
        elapsed = time.time() - begin
        print(f"Genome #{count} took {round(elapsed,1)} seconds")
        count = count +1

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

def get_results_from_file():
    with open('results.txt') as file:
        results = file.read()
    
    print(type(results))

    dict = json.loads(results)
    print(dict)
    print(type(dict))

# Running code and test code
# change_sections(sectionList=columnList, section_number=1)
# population = create_full_population(reducedColumnList, reducedBeamList)
# print(population)

get_results_from_file()