import tkinter as tk
from tkinter import ttk
import pandas as pd

class HelloView(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.inputCaseNames = ['p10', 'p50', 'p90', 'pfail', 'pbase']
        self.inputParameters = ['major', 'months', 'incremental', 'WI', 'NRI', 'LOSS', 'p_s', 'Decline_type', 'qi', 'Di_sec',
            'b', 'Dterm_sec', 'peak', 'shrink', 'ngl_yield', 'oil_yield', 'fixed_cost', 'var_gas_cost', 'var_oil_cost',
            'overhead', 'adval_rate', 'sev_rate']
        #self.inputParametersTable = pd.DataFrame(data = None, columns = self.inputCaseNames, index = self.inputParameters)
        self.inputParametersTable = [[None] * 5] * 15

        self.dropDownInputs = ['major', 'incremental', 'LOSS', 'Decline_type']
        self.dropDownOptions = {
            'major':            ['Oil', 'Gas'],
            'incremental':      ['Incremental', 'Non-Incremental'],
            'LOSS':             ['LOSS NO', 'LOSS BFIT', 'LOSS OK'],
            'Decline_type':     ['Exponential', 'Hyperbolic', 'Modified Arps', 'Incline > Decline', 'No Rate']
            }

        for i in range(5):
            tableLabel = ttk.Label(self, text = self.inputCaseNames[i])
            tableLabel.grid(row = 0, column = i + 1)

        for j in range(15):
            tableLabel = ttk.Label(self, text = self.inputParameters[j])
            tableLabel.grid(row = j + 1, column = 0)

        for i in range(5):
            for j in range(15):
                if self.inputParameters[j] in self.dropDownInputs:
                    tableEntry = ttk.Combobox(self, textvariable = self.inputParametersTable[j][i],
                        values = self.dropDownOptions[self.inputParameters[j]])
                    tableEntry.grid(row = j + 1, column = i + 1, sticky = tk.W)
                else:
                    tableEntry = ttk.Entry(self, textvariable = self.inputParametersTable[j][i])
                    tableEntry.grid(row = j + 1, column = i + 1, sticky = tk.W)

        self.name = tk.StringVar()
        self.hello_string = tk.StringVar()
        self.hello_string.set("params here")
        
    def on_change(self):
        if self.name.get().strip():
            self.hello_string.set("Hello " + self.name.get())
        else:
            self.hello_string.set("Hello World")
    
class MyApplication(tk.Tk):
    """Hello World Main Application"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("test")
        self.geometry('1800x600')
        self.resizable(width = True, height = True)
        HelloView(self).grid(sticky = (tk.E + tk.W + tk.N + tk.S))
        self.columnconfigure(0, weight = 1)
    
if __name__ == '__main__':
    app = MyApplication()
    app.mainloop()