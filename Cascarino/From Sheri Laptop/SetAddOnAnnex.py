import os
import sys
baseName = os.path.basename(__file__)
dirName = os.path.dirname(__file__)
sys.path.append(dirName+ r'/../..')

from RFEM.enums import *
from RFEM.initModel import Model, SetAddonStatus

def SetStandards(steelStandard: str = 'SANS 10162 | 2011-05', loadStandard: str = 'SANS 10160 | 2019'):

    with open(dirName+r"./standard.js", "w") as std:

        std.write("general.current_standard_for_steel_design = '{}'".format(steelStandard))

    Model.clientModel.service.run_script(dirName+r"./standard.js")

    os.remove(dirName+r"./standard.js")

    with open(dirName+r"./standard.js", "w") as std:

        std.write("general.current_standard_for_load_wizard = '{}'".format(loadStandard))

    Model.clientModel.service.run_script(dirName+r"./standard.js")

    os.remove(dirName+r"./standard.js")

Model(True,'Demo')
SetAddonStatus(Model.clientModel, AddOn.steel_design_active)

SetStandards()

# Load Wizard: SANS 10160 | 2019
# Steel Design: SANS 10162 | 2011-05