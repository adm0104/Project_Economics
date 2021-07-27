import numpy as np
import matplotlib.pyplot as plt
import case as case
import Toolbox as tb
import pandas as pd
import openpyxl as pyx

case_data = pd.read_excel('Project_Economics_Controller.xlsx', 
    sheet_name = 'Data_DO_NOT_EDIT',
    index_col = 0)

print(case_data)