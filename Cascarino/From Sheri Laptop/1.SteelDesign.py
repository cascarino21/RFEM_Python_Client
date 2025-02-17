# Add folder to where RFEM code is saved
import sys
sys.path.append(r'C:\Users\User\Desktop\Cascarino\Project Development\RFEM_Python_Client')

# Required to create and modify model
from RFEM.enums import *
from RFEM.initModel import *

# Geometry
from RFEM.BasicObjects.node import Node
from RFEM.BasicObjects.member import Member
from RFEM.TypesForNodes.nodalSupport import *
from RFEM.BasicObjects.section import Section
from RFEM.BasicObjects.material import Material

# Loads and Load combinations
from RFEM.Loads.memberLoad import MemberLoad
from RFEM.LoadCasesAndCombinations.loadCase import LoadCase
from RFEM.LoadCasesAndCombinations.loadCombination import LoadCombination
from RFEM.LoadCasesAndCombinations.staticAnalysisSettings import StaticAnalysisSettings

# Steel Design
from RFEM.SteelDesign.steelUltimateConfigurations import SteelDesignUltimateConfigurations
from RFEM.TypesForSteelDesign.steelBoundaryConditions import SteelBoundaryConditions

# Step 0: Input 
# Left blank for now to get the code to work

# Step 1: Create and /or open model
Model(True, 'Steel Design')
Model.clientModel.service.begin_modification()
SetAddonStatus(Model.clientModel, AddOn.steel_design_active)

# Step 2: Properties
Material(1, "S235")
Section(1, 'IPE 200', 1)

# Step 3: Nodes
Node(1, 0, 0, 0)
Node(2, 4, 0, 0)

# Step 4: Members (Beams, Columns)
Member(1, 1, 2, 0, 1, 1)

# Step 5: Supports (Nodal, Linear, Area)
NodalSupport(1, '1 2', NodalSupportType.HINGED)
NodalSupport(1, '1 2', [inf, inf, inf, inf, 0, inf] )

# Step 6: Loadcases
LoadCase(1, 'Self-Weight', [True, 0, 0 ,1])
LoadCase(2, 'Variable Load', [False])

# Step 7: Loads
MemberLoad(1, 1, '1', MemberLoadDirection.LOAD_DIRECTION_GLOBAL_Z_OR_USER_DEFINED_W_TRUE, 5000)

# Step 8:  Static Analysis Settings
StaticAnalysisSettings.GeometricallyLinear(1, 'Geometr. Linear')

# Step 8: Load Combination
LoadCombination(1, AnalysisType.ANALYSIS_TYPE_STATIC, name='LC1', static_analysis_settings=1, combination_items=[[1.20, 1, 0, False], [1.50, 2, 0, True]])

# Step 9: Set Boundary Conditions / Effective Lengths
SteelBoundaryConditions(1, 'Standard', '1')
SteelDesignUltimateConfigurations(1, 'ULS1', 'All')

# Step 11: Run Analysis
Calculate_all()

# Step 12: Save and end modification
Model.clientModel.service.finish_modification()