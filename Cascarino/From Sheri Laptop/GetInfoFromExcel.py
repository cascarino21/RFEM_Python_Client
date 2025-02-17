#Set Correct Working Directory
import os
import sys
import pandas as pd
baseName = os.path.basename(__file__)
dirName = os.path.dirname(__file__)
print('basename:    ', baseName)
print('dirname:     ', dirName)
sys.path.append(dirName + r'/../..')
# print(sys.path)


#Step 0: Importing Excel
data = pd.read_excel('Python Input.xlsx')

print(data)