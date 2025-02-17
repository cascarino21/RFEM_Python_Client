#Set Correct Working Directory
import os
import sys
baseName = os.path.basename(__file__)
dirName = os.path.dirname(__file__)
print('basename:    ', baseName)
print('dirname:     ', dirName)
sys.path.append(dirName + r'/../..')
# print(sys.path)

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
from RFEM.Loads.nodalLoad import *
from RFEM.Loads.memberLoad import *
from RFEM.LoadCasesAndCombinations.loadCase import *
from RFEM.LoadCasesAndCombinations.staticAnalysisSettings import *
from RFEM import baseData

# Step 1.1: Get Inputs
# l = float(input("Length of cantilever in m: "))
# f = float(input("Force in kN: "))
length = 10
height = -6

# Step 2: Model Initiation
Model(True, '2D Portal')
#Model(False)
Model.clientModel.service.begin_modification()


# Step 3: Nodes
# Column Bases
Node(1, 0,0,0)
Node(2, length, 0,0)

#Column Tops
Node(3, 0, 0, height)
Node(4, length, 0, height)

#Apex
Node(5, length/2, 0, height)

# Step 5: Material
Material(1, 'S235')

# Step 4: Section
# Column Section (Need to learn how to automate this, ask for input)
Section(1, 'IPE 300')

#Beam Section 
Section(2, 'IPE 200')


# Step 6: Members
# Member('number', 'StartNodeMo', 'EndNodeNo',  'rotationAngle', 'startSectionNo', 'endSectionNo', 'StartHingeNo', 
# 'EndHingeNo', 'line', 'comment',  )
#Columns
Member(1, 1, 3, 0.0, 1, 1)
Member(2, 2, 4, 0.0, 1, 1)

#Beams
Member(3, 3,5, 0.0, 2, 2)
Member(4, 5,4, 0.0, 2, 2)

# Step 7: Support Conditions
NodalSupport(1, '1 2', NodalSupportType.HINGED)

# Step 8: Load Case
LoadCase(1, 'Self-weight', [True,0,0,1], ActionCategoryType.ACTION_CATEGORY_SELF_WEIGHT_G)
LoadCase(2, 'Variable Load - Roof', [False], ActionCategoryType.ACTION_CATEGORY_IMPOSED_LOADS_INACCESSIBLE_ROOFS_Q_H)
LoadCase(3, 'Wind X', [False], ActionCategoryType.ACTION_CATEGORY_WIND_QW)
LoadCase(4, 'Wind -X', [False], ActionCategoryType.ACTION_CATEGORY_WIND_QW)


# Step 9: Adding Loads
# Roof Live Loads
MemberLoad(1, 2, '3 4', MemberLoadDirection.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE, 2000)

# Wind X Loads
MemberLoad(1, 3, '1', MemberLoadDirection.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED, 1500)
MemberLoad(2, 3, '2', MemberLoadDirection.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED, 1500)
MemberLoad(3, 3, '3 4', MemberLoadDirection.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED, -1500)

# Wind -X Loads
MemberLoad(1, 4, '1', MemberLoadDirection.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED, -1500)
MemberLoad(2, 4, '2', MemberLoadDirection.LOAD_DIRECTION_GLOBAL_X_OR_USER_DEFINED_U_PROJECTED, -1500)
MemberLoad(3, 4, '3 4', MemberLoadDirection.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_PROJECTED, -1500)

# Step 10: Analysis Settings
# StaticAnalysisSettings(1, 'Th. I. O')

# Step 11: Running Analysis
# Calculate_all()

#Step 12: Save and End Modification
Model.clientModel.service.finish_modification()