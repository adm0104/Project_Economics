import sys
import numpy as np
import pandas as pd
import econ_engine as econ
import os
from layout_colorwidget import Color
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import(
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QMainWindow,
    QWidget,
    QPushButton,
    QComboBox
)
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot

pars = pd.read_excel(
    os.path.dirname(__file__) + '\\Project_Economics_Controller.xlsm', 
    sheet_name = 'Data_DO_NOT_EDIT',
    header = 0,
    index_col = 0
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('EightyTwenty')
                        
        mainLayout = QGridLayout()
        topLeftLayout = QVBoxLayout()
        topLeftTopLayout = QHBoxLayout()

        runButton = QPushButton("Run Economics")
        runButton.clicked.connect(self.run_economics)

        self.declinePlot = pg.PlotWidget()
        self.declinePlot.setLogMode(x = False, y = True)
        self.declinePlot.addLegend(offset = [-10, 10])

        self.paramRowHeaders = [
            'CAPEX',
            'Decline Type',
            'Initial Rate, mcfd',
            'Initial Decline Rate, %/yr',
            'b-factor',
            'Terminal Decline Rate, %/yr',
            'Peak Rate',
            'Shrink',
            'NGL Yield',
            'Oil Yield',
            'Fixed Cost',
            'Variable Gas Cost',
            'Variable Oil Cost',
            'Overhead'
        ]
        self.caseColHeaders = [
            'p10',
            'p50',
            'p90',
            'pfail',
            'pbase'
        ]
        self.runSettings = [
            'Major Phase',
            'Months',
            'Incremental Run?',
            'Working Interest',
            'Net Revenue Interest',
            'LOSS Function',
            'Probability of Success',
            'Ad Valorem Tax Rate',
            'Severance Tax Rate'
        ]

        # Generate input table
        self.inputTable = QTableWidget(len(self.paramRowHeaders), len(self.caseColHeaders))
        self.inputTable.setVerticalHeaderLabels(self.paramRowHeaders)
        self.inputTable.setHorizontalHeaderLabels(self.caseColHeaders)

        # Populate case-by-case input table with necessary drop-down menus
        self.dropDownParams = {
            'Decline Type': ['Exponential', 'Hyperbolic', 'Modified Arps', 'CBM Dewatering/Incline', 'No Rate'],
        }
        self.dropDownInputs = {}
        for i in self.dropDownParams:
            self.dropDownInputs.update({i: []})
            for j in range(len(self.caseColHeaders)):
                self.dropDownInputs[i].append(QComboBox())
                self.dropDownInputs[i][j].addItems(self.dropDownParams[i])
                self.inputTable.setCellWidget(self.paramRowHeaders.index(i), j, self.dropDownInputs[i][j])
        
        # Global input table
        self.settingsInputTable = QTableWidget(len(self.runSettings), 1)
        self.settingsInputTable.setVerticalHeaderLabels(self.runSettings)
        self.settingsInputTable.setHorizontalHeaderLabels(['Settings'])

        # Populate case-by-case input table with necessary drop-down menus
        self.dropDownSettings = {
            'Major Phase': ['Gas', 'Oil'],
            'Incremental Run?': ['Incremental', 'Non-Incremental'],
            'LOSS Function': ['BFIT', 'NO', 'OK']
        }
        self.dropDownSettingsInputs = []
        for i, j in enumerate(self.dropDownSettings):
            self.dropDownSettingsInputs.append(QComboBox())
            self.dropDownSettingsInputs[i].addItems(self.dropDownSettings[j])
            self.settingsInputTable.setCellWidget(self.runSettings.index(j), 0, self.dropDownSettingsInputs[i])


        self.econResultsTable = QTableWidget(5, 5)
        self.declineCalcTable = QTableWidget(5, 5)

        mainLayout.addWidget(self.declinePlot, 0, 1)

        topLeftTopLayout.addWidget(self.settingsInputTable)
        topLeftTopLayout.addWidget(self.inputTable)
        topLeftTopLayout.setStretch(0, 2)
        topLeftTopLayout.setStretch(1, 5)

        topLeftLayout.addLayout(topLeftTopLayout)
        topLeftLayout.addWidget(runButton)
        mainLayout.addLayout(topLeftLayout, 0, 0)

        mainLayout.addWidget(self.econResultsTable, 1, 0)
        

        mainLayout.addWidget(self.declineCalcTable, 1, 1)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

        # To-do: Modernize color scheme on graph
        self.redpen = pg.mkPen((255, 0, 0), width = 3)
        self.greenpen = pg.mkPen((0, 255, 0), width = 3)
        self.bluepen = pg.mkPen((0, 0, 255), width = 3)
        self.yellowpen = pg.mkPen((255, 255, 0), width = 3)
        self.purplepen = pg.mkPen((255, 0, 255), width = 3)
        self.orangepen = pg.mkPen((0, 255, 255), width = 3)


        # Pre-populate with default values as placeholders
        self.defaultParams = {
            'CAPEX': ['200', '200', '200', '200', '200'],
            'Decline Type': 'Modified Arps',
            'Initial Rate, mcfd': ['1000', '800', '500', '80', '100'],
            'Initial Decline Rate, %/yr': ['0.25', '0.25', '0.25', '0.05', '0.05'],
            'b-factor': ['2', '2', '2', '0', '0'],
            'Terminal Decline Rate, %/yr': ['0.05', '0.05', '0.05', '0.05', '0.05'],
            'Peak Rate': ['800', '800', '800', '800', '800'],
            'Shrink': ['0.9', '0.9', '0.9', '0.9', '0.9'],
            'NGL Yield': ['40', '40', '40', '40', '40'],
            'Oil Yield': ['5', '5', '5', '5', '5'],
            'Fixed Cost': ['200', '200', '200', '200', '200'],
            'Variable Gas Cost': ['0.5', '0.5', '0.5', '0.5', '0.5'],
            'Variable Oil Cost': ['3', '3', '3', '3', '3',],
            'Overhead': ['300', '300', '300', '300', '300',]
        }

        for i, j in enumerate(self.paramRowHeaders):
            if j in self.dropDownParams:
                next
            else:
                for k in range(len(self.caseColHeaders)):
                    self.inputTable.setItem(i, k, QTableWidgetItem(self.defaultParams[j][k]))

        self.defaultSettings = {
            'Major Phase': 'Gas',
            'Months': '600',
            'Incremental Run?': 'Incremental',
            'Working Interest': '1',
            'Net Revenue Interest': '0.875',
            'LOSS Function': 'BFIT',
            'Probability of Success': '0.9',
            'Ad Valorem Tax Rate': '0.067',
            'Severance Tax Rate': '0.02'
        }

        for i, j in enumerate(self.runSettings):
            if j in self.dropDownSettings:
                next
            else:
                self.settingsInputTable.setItem(i, 0, QTableWidgetItem(self.defaultSettings[j]))
    
    def run_economics(self):
        # To-do: Add lines to delete old data, remove their plots from the graph
        #self.tableData = [[None] * self.inputTable.rowCount()] * self.inputTable.columnCount()

        params = pd.DataFrame(
            index = self.paramRowHeaders,
            columns = self.caseColHeaders,
        )

        for i, j in enumerate(self.paramRowHeaders):
            if j in self.dropDownParams:
                for k in range(len(self.caseColHeaders)):
                    params[self.caseColHeaders[k]][self.paramRowHeaders[i]] = self.dropDownInputs[j][k].currentText()
            else:
                for k in range(len(self.caseColHeaders)):
                    params[self.caseColHeaders[k]][self.paramRowHeaders[i]] = float(self.inputTable.item(i, k).text())

        params = params.set_index(pd.Index([
            'capex',
            'Decline_type',
            'qi',
            'Di_sec',
            'b',
            'Dterm_sec',
            'peak',
            'shrink',
            'ngl_yield',
            'oil_yield',
            'fixed_cost',
            'var_gas_cost',
            'var_oil_cost',
            'overhead'
        ]))

        runSettingsFrame = pd.DataFrame(
            index = self.runSettings,
            columns = ['settings']
        )

        counter = 0
        for i, j in enumerate(self.runSettings):
            if j in self.dropDownSettings:
                runSettingsFrame['settings'][j] = self.dropDownSettingsInputs[counter].currentText()
                counter += 1
            else:
                runSettingsFrame['settings'][j] = float(self.settingsInputTable.item(i, 0).text())
        
        runSettingsFrame = runSettingsFrame.set_index(pd.Index([
            'major',
            'months',
            'incremental',
            'WI',
            'NRI',
            'LOSS',
            'p_s',
            'adval_rate',
            'sev_rate'
        ]))

        print(params)
        print(runSettingsFrame)
        print(runSettingsFrame.settings.months)

        pmean, p10, p50, p90, pfail, pbase = econ.run_econs(params, runSettingsFrame)
        self.declinePlot.plot(pmean.t[pmean.gross_gas_rate > 0], pmean.gross_gas_rate[pmean.gross_gas_rate > 0], name = 'pmean', pen = self.redpen)
        self.declinePlot.plot(p10.t[p10.gross_gas_rate > 0], p10.gross_gas_rate[p10.gross_gas_rate > 0], name = 'p10', pen = self.greenpen)
        self.declinePlot.plot(p50.t[p50.gross_gas_rate > 0], p50.gross_gas_rate[p50.gross_gas_rate > 0], name = 'p50', pen = self.bluepen)
        self.declinePlot.plot(p90.t[p90.gross_gas_rate > 0], p90.gross_gas_rate[p90.gross_gas_rate > 0], name = 'p90', pen = self.yellowpen)
        self.declinePlot.plot(pbase.t[pbase.gross_gas_rate > 0], pbase.gross_gas_rate[pbase.gross_gas_rate > 0], name = 'pbase', pen = self.purplepen)
        self.declinePlot.plot(pfail.t[pfail.gross_gas_rate > 0], pfail.gross_gas_rate[pfail.gross_gas_rate > 0], name = 'pfail', pen = self.orangepen)



app = QApplication(sys.argv)

darkPalette = app.palette()
darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
darkPalette.setColor(QPalette.WindowText, Qt.white)
darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
darkPalette.setColor(QPalette.ToolTipBase, Qt.white)
darkPalette.setColor(QPalette.ToolTipText, Qt.white)
darkPalette.setColor(QPalette.Text, Qt.white)
darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
darkPalette.setColor(QPalette.ButtonText, Qt.white)
darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
darkPalette.setColor(QPalette.BrightText, Qt.red)
darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
darkPalette.setColor(QPalette.HighlightedText, Qt.white)
darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

app.setPalette(darkPalette)

app.setStyle('Fusion')
window = MainWindow()
window.resize(1920,1080)
window.show()

app.exec_()