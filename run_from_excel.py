import numpy as np
import matplotlib.pyplot as plt
import case as case
import Toolbox as tb
import pandas as pd
import openpyxl as pyx

case_data = pd.DataFrame(
    pd.read_excel('Project_Economics_Controller.xlsx', 
    sheet_name = 'Data_DO_NOT_EDIT',
    header = 0).T,
    index = 0)

print(case_data)

print(case_data.major)