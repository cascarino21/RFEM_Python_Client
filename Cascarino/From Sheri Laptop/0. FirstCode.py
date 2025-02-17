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
from RFEM.enums import *
from RFEM.initModel import *
from RFEM.BasicObjects.node import Node
from RFEM.BasicObjects.member import Member
from RFEM.BasicObjects.section import Section
from RFEM.BasicObjects.material import Material
from RFEM.TypesForNodes.nodalSupport import *
from RFEM.Loads.nodalLoad import *
from RFEM.LoadCasesAndCombinations.loadCase import *
from RFEM.LoadCasesAndCombinations.staticAnalysisSettings import *

# Step 1.1: Get Inputs
l = float(input("Length of cantilever in m: "))
f = float(input("Force in kN: "))

# Step 2: Model Initiation
Model(True, 'mymodel')
#Model(False)
Model.clientModel.service.begin_modification()

# Step 3: Nodes
Node(1,0,0,0)
Node(2,l,0,0)

# Step 5: Material
Material(1, 'S235')

# Step 4: Section
Section(1, 'IPE 200')

# Step 6: Beam
Member(1, 1, 2, 0.0, 1, 1)

# Step 7: Support Conditions
NodalSupport(1, '1', NodalSupportType.FIXED)

# Step 8: Load Case
LoadCase(1, 'LC1', [False])

# Step 9: Adding a Point Load
NodalLoad(1, 1, '2', NodalLoadDirection.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W, f*1000)
# Pre-defined = Z-Direction

# Step 10: Analysis Settings
StaticAnalysisSettings(1, 'Th. I. O', )

# Step 11: Running Analysis
Calculate_all()

#Step 12: Save and End Modification
Model.clientModel.service.finish_modification()