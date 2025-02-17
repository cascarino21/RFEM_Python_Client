#Set Correct Working Directory
import os
import sys
import pandas as pd # type: ignore
baseName = os.path.basename(__file__)
dirName = os.path.dirname(__file__)
print('basename:    ', baseName)
print('dirname:     ', dirName)
sys.path.append(dirName + r'/../..')
# print(sys.path)

#Step 0: Acquire information (can be in excel)
# data = pd.read_excel('')

# Step 1: Importing Libraries
#Importing other Libraries


#Importing RFEM Libraries
from RFEM.enums import *
from RFEM.initModel import *
from RFEM.BasicObjects.node import Node
from RFEM.BasicObjects.member import Member
from RFEM.BasicObjects.section import Section
from RFEM.BasicObjects.material import Material
from RFEM.TypesForNodes.nodalSupport import *
from RFEM import baseData

# Loads and Load combinations
from RFEM.Loads.nodalLoad import *
from RFEM.Loads.memberLoad import *
from RFEM.LoadCasesAndCombinations.loadCase import *
from RFEM.LoadCasesAndCombinations.loadCombination import *
from RFEM.LoadCasesAndCombinations.staticAnalysisSettings import *
from RFEM.LoadCasesAndCombinations.designSituation import *

# Steel Design
from RFEM.SteelDesign.steelUltimateConfigurations import *
from RFEM.TypesForSteelDesign.steelBoundaryConditions import *
from RFEM.TypesForSteelDesign.steelEffectiveLengths import *

# Results
from RFEM.Results.designOverview import GetDesignOverview, GetPartialDesignOverview
from RFEM.Results.resultTables import *

# Load Wizard: SANS 10160 | 2019
# Steel Design: SANS 10162 | 2011-05
# Step 1.1: Get Inputs
# length = float(input("Building length (in m): "))
# width = float(input("Building width (in m): "))
length = 10
width = 20
frameSpacing = 10
purlinSpacing = 2.5

numSpans = int(length/frameSpacing)
spanLength = frameSpacing

# Step 2: Model Initiation
Model(True, '2D purlin')
#Model(False)
Model.clientModel.service.begin_modification()
SetAddonStatus(Model.clientModel, AddOn.steel_design_active)

def SetStandards(steelStandard: str = 'SANS 10162 | 2011-05', loadStandard: str = 'SANS 10160 | 2019'):

    with open(dirName+r"./standard.js", "w") as std:

        std.write("general.current_standard_for_steel_design = '{}'".format(steelStandard))

    Model.clientModel.service.run_script(dirName+r"./standard.js")

    os.remove(dirName+r"./standard.js")

    with open(dirName+r"./standard.js", "w") as std:

        std.write("general.current_standard_for_load_wizard = '{}'".format(loadStandard))

    Model.clientModel.service.run_script(dirName+r"./standard.js")

    os.remove(dirName+r"./standard.js")

#Step 1 of ... to keep to European Standards
SetStandards()

# Step 3: Nodes
for i in range(numSpans+1):
    Node(i+1, i*spanLength, 0,0)

# Step 5: Material
Material(1, 'S355JR')

# Step 4: Section
# Column Section (Need to learn how to automate this, ask for input)
Section(1, 'IPE 300')

#Beam Section 
Section(2, 'IPE 200')


# Step 6: Members
# Member('number', 'StartNodeMo', 'EndNodeNo',  'rotationAngle', 'startSectionNo', 'endSectionNo', 'StartHingeNo', 
# 'EndHingeNo', 'line', 'comment',  )
for i in range(numSpans):
    Member(i+1, i+1, i+2, 0.0, 1, 1)
# Member(1, 1, 1*numSpans+1, 0.0, 1,1)

# Step 7: Support Conditions
supports = ""
for i in range(numSpans+1):
    supports = supports+str(i+1)+" "

NodalSupport(1, supports, support = [inf, inf, inf, inf, 0, inf], )

# Step 8.0: Set up SA regulations
dictSARegs = {
    "current_standard_for_combination_wizard": 6331,
    "activate_combination_wizard_and_classification": True,
    "activate_combination_wizard": False,
    "result_combinations_active": False,
    "result_combinations_parentheses_active": False,
    "result_combinations_consider_sub_results": False,
    "combination_name_according_to_action_category": False
}

# Step 2 of ... to change to European
LoadCasesAndCombinations(dictSARegs)

# Step 8: Load Cases, Standard
# LoadCase(1, 'Self-weight', [True,0,0,1])
# LoadCase(2, 'Variable Load - Roof', [False])
# LoadCase(3, 'Wind Downward', [False])
# LoadCase(4, 'Wind Uplift', [False])

# Action Categories, SANS
LoadCase(1, 'Self-weight', [True,0,0,1], ActionCategoryType.ACTION_CATEGORY_SELF_WEIGHT_G)
LoadCase(2, 'Variable Load - Roof', [False], ActionCategoryType.ACTION_CATEGORY_IMPOSED_LOADS_INACCESSIBLE_ROOFS_Q_H)
LoadCase(3, 'Wind X', [False], ActionCategoryType.ACTION_CATEGORY_WIND_QW)
LoadCase(4, 'Wind -X', [False], ActionCategoryType.ACTION_CATEGORY_WIND_QW)


# # Step 9: Adding Loads
# #Tributary Area
# spanLeft = 2;
# spanRight = 2;

# Roof Live Loads
MemberLoad(1, 2, '1', MemberLoadDirection.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE, 2000.0)

# Wind Downward
MemberLoad(1, 3, '1', MemberLoadDirection.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE, 1500.0)

# Wind Uplift
MemberLoad(1, 4, '1', MemberLoadDirection.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE, -1500.0)

# Step 10: Analysis Settings
StaticAnalysisSettings(1, 'Geometrically linear', StaticAnalysisType.GEOMETRICALLY_LINEAR)
StaticAnalysisSettings(2, 'Second-order (P-Δ) | Picard | 100 | 1', StaticAnalysisType.SECOND_ORDER_P_DELTA)
StaticAnalysisSettings(3, 'Large deformations | Newton-Raphson | 100 | 1', StaticAnalysisType.LARGE_DEFORMATIONS)

# Step 11: Design Situations and Load Combinations 
# DesignSituation(1, design_situation_type= DesignSituationType.DESIGN_SITUATION_TYPE_STR_PERMANENT_AND_TRANSIENT_SANS, active=True)
# DesignSituation(2, design_situation_type=DesignSituationType.DESIGN_SITUATION_TYPE_REVERSIBLE_SANS,active=True)
# DesignSituation(3, design_situation_type=DesignSituationType.DESIGN_SITUATION_TYPE_IRREVERSIBLE_SANS, active=True)

# LoadCombination(1, AnalysisType.ANALYSIS_TYPE_STATIC, name='LC1', static_analysis_settings=2, combination_items=[[1.20, 1, 0, False], [1.50, 2, 0, True]], design_situation=1)
# LoadCombination(2, AnalysisType.ANALYSIS_TYPE_STATIC, name='LC2', static_analysis_settings=2, combination_items=[[1.20, 1, 0, False], [1.50, 3, 0, True]], design_situation=1)
# LoadCombination(3, AnalysisType.ANALYSIS_TYPE_STATIC, name='LC3', static_analysis_settings=2, combination_items=[[0.90, 1, 0, False], [1.50, 4, 0, True]], design_situation=1)

LoadCombination(1, AnalysisType.ANALYSIS_TYPE_STATIC, name='LC1', static_analysis_settings=2, combination_items=[[1.20, 1, 0, False], [1.50, 2, 0, True]])
LoadCombination(2, AnalysisType.ANALYSIS_TYPE_STATIC, name='LC2', static_analysis_settings=2, combination_items=[[1.20, 1, 0, False], [1.50, 3, 0, True]])
LoadCombination(3, AnalysisType.ANALYSIS_TYPE_STATIC, name='LC3', static_analysis_settings=2, combination_items=[[0.90, 1, 0, False], [1.50, 4, 0, True]])

# Step 12: Set Boundary Conditions / Effective Lengths
# SteelBoundaryConditions(1, 'Standard', '1')
SteelEffectiveLengths(no=1, members= '1', flexural_buckling_about_y=True, flexural_buckling_about_z=True, \
    torsional_buckling=True, lateral_torsional_buckling=True, principal_section_axes=True, \
    geometric_section_axes=False, name='Test', \
    nodal_supports=[
        [SteelEffectiveLengthsSupportType.SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION, True, 0.0, \
        SteelEffectiveLengthsEccentricityType.ECCENTRICITY_TYPE_NONE, 0.0, 0.0, 0.0, 0.0, \
        SteelEffectiveLengthsSupportTypeInY.SUPPORT_STATUS_YES, SteelEffectiveLengthsRestraintTypeAboutX.SUPPORT_STATUS_YES, \
        SteelEffectiveLengthsRestraintTypeAboutZ.SUPPORT_STATUS_NO, SteelEffectiveLengthsRestraintTypeWarping.SUPPORT_STATUS_NO, "1"],
        [SteelEffectiveLengthsSupportType.SUPPORT_TYPE_FIXED_IN_Z_Y_AND_TORSION, True, 0.0, \
        SteelEffectiveLengthsEccentricityType.ECCENTRICITY_TYPE_NONE, 0.0, 0.0, 0.0, 0.0, \
        SteelEffectiveLengthsSupportTypeInY.SUPPORT_STATUS_YES, SteelEffectiveLengthsRestraintTypeAboutX.SUPPORT_STATUS_YES, \
        SteelEffectiveLengthsRestraintTypeAboutZ.SUPPORT_STATUS_NO, SteelEffectiveLengthsRestraintTypeWarping.SUPPORT_STATUS_NO, "2"]
                        ], \
    factors=[[1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], intermediate_nodes= False, different_properties= True, \
    factors_definition_absolute = False, import_from_stability_analysis_enabled = False, \
    determination_of_mcr = SteelEffectiveLengthsDeterminationMcrSANS.DETERMINATION_M_CR_SANS_EIGENVALUE)

SteelDesignUltimateConfigurations(1, 'ULS1', 'All')

# # Step 13: Running Analysis
# Calculate_all()

# Not working
# # Step xx: Get Internal Forces
# internalForces = ResultTables.MembersInternalForces(CaseObjectType.E_OBJECT_TYPE_LOAD_CASE, 1)
# # print(internalForces)
# resultList = ConvertResultsToListOfDct(internalForces, False)
# # print(resultList)

# Step 14: Getting Design overview
# designOverview = GetDesignOverview()
# print(designOverview)

#Step 15: Save and End Modification
Model.clientModel.service.finish_modification()