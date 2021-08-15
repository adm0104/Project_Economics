import sys
import numpy as np
import pandas as pd
import econ_engine as econ
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
from pyqtgraph import PlotWidget
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as mplCanvas
matplotlib.use('Qt5Agg')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Name your app!
        self.setWindowTitle('EightyTwenty')

        # Define input table rows & headers
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

        # Define settings input table rows & headers
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
        
        # Generate settings input table
        self.settingsInputTable = QTableWidget(len(self.runSettings), 1)
        self.settingsInputTable.setVerticalHeaderLabels(self.runSettings)
        self.settingsInputTable.setHorizontalHeaderLabels(['Settings'])

        # Populate settings input table with necessary drop-down menus
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

        # Define results table rows & headers
        self.resultsHeaders = [
            'p10',
            'p50',
            'p90',
            'pfail',
            'pbase',
            'pmean'
        ]
        self.resultsMetrics = [
            'Incremental EUR (Bcf)',
            'Gross CAPEX ($M)',
            'Net CAPEX ($M)',
            'Net Res. (Mboe)',
            'Net Res. (MMcfe)',
            'Net IP30 (Boe/d)',
            'Net IP30 (Mcfe/d)',
            'PV-10 ($M)',
            'Payout (Months)',
            'PVR-10'
        ]

        # Generate results table widget
        self.econResultsTable = QTableWidget(len(self.resultsMetrics), len(self.resultsHeaders))
        self.econResultsTable.setVerticalHeaderLabels(self.resultsMetrics)
        self.econResultsTable.setHorizontalHeaderLabels(self.resultsHeaders)

        # Set up full-page layout
        mainLayout = QGridLayout()

        # Populate top-left quadrant of GUI: run button, settings, and parameter inputs
        topLeftLayout = QVBoxLayout()
        topLeftTopLayout = QHBoxLayout()
        runButton = QPushButton('Run Economics')
        runButton.clicked.connect(self.run_economics)
        topLeftLayout.addWidget(self.settingsInputTable)
        topLeftLayout.addWidget(runButton)
        topLeftTopLayout.addLayout(topLeftLayout)
        topLeftTopLayout.addWidget(self.inputTable)
        topLeftTopLayout.setStretch(0, 2)
        topLeftTopLayout.setStretch(1, 5)
        mainLayout.addLayout(topLeftTopLayout, 0, 0)

        # Populate top-right quadrant of GUI: decline plot
        self.declinePlot = pg.PlotWidget(title = 'Decline Plot', labels = {'left': 'Gross Gas Rate (Mcfd)', 'bottom': 'Time Elapsed (Months)'})
        self.declinePlot.setLogMode(x = False, y = True)
        self.declinePlot.addLegend(offset = [-10, 10])
        self.declinePlot.plottedAlready = False
        mainLayout.addWidget(self.declinePlot, 0, 1)

        # Populate bottom-left quadrant of GUI: results table
        mainLayout.addWidget(self.econResultsTable, 1, 0)
        
        # Populate bottom-right quadrant of GUI: cumulative cash flow plot, metrics
        bottomRightLayout = QVBoxLayout()
        self.bottomBottomRightLayout = QHBoxLayout()
        self.cumCashFlowPlot = pg.PlotWidget(title = 'Cumulative Cash Flow Plot', labels = {'left': 'Cumulative Cash Flow ($M)', 'bottom': 'Time Elapsed (Months)'})
        bottomRightLayout.addWidget(self.cumCashFlowPlot)
        self.cumCashFlowPlot.addLegend(offset = [10, 10])
        self.cumCashFlowPlot.plottedAlready = False
        self.mplFigure1 = plotCanvas(self)
        self.mplFigure2 = plotCanvas(self)
        self.mplFigure1.axes.pie(x = [1], colors = ['w'], labels = ['No run data'])
        self.mplFigure2.axes.pie(x = [1], colors = ['w'], labels = ['No run data'])
        self.mplFigure1.axes.set_title('Revenue Split by Product')
        self.mplFigure2.axes.set_title('Volume (BOE) Split by Product')
        self.bottomBottomRightLayout.addWidget(self.mplFigure1)
        self.bottomBottomRightLayout.addWidget(self.mplFigure2)
        bottomRightLayout.addLayout(self.bottomBottomRightLayout)
        mainLayout.addLayout(bottomRightLayout, 1, 1)

        mainLayout.setColumnStretch(0,1)
        mainLayout.setColumnStretch(1,1)
        mainLayout.setRowStretch(0,1)
        mainLayout.setRowStretch(1,1)

        # Set primary as central
        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

        # Define pens for plotting
        # To-do: Modernize color scheme on graph
        self.redPen = pg.mkPen((255, 0, 0), width = 3)
        self.dottedRedPen = pg.mkPen((255, 0, 0), width = 3, style = Qt.DashLine)
        self.greenPen = pg.mkPen((0, 255, 0), width = 3)
        self.bluePen = pg.mkPen((0, 0, 255), width = 3)
        self.yellowPen = pg.mkPen((255, 255, 0), width = 3)
        self.purplePen = pg.mkPen((255, 0, 255), width = 3)
        self.orangePen = pg.mkPen((0, 255, 255), width = 3)

        # Pre-populate with default values as placeholders
        self.defaultParams = {
            'CAPEX': ['200000', '200000', '200000', '200000', '200000'],
            'Decline Type': [2, 2, 2, 0, 0],
            'Initial Rate, mcfd': ['1000', '800', '500', '80', '100'],
            'Initial Decline Rate, %/yr': ['0.25', '0.25', '0.25', '0.05', '0.05'],
            'b-factor': ['2', '2', '2', '0', '0'],
            'Terminal Decline Rate, %/yr': ['0.05', '0.05', '0.05', '0.05', '0.05'],
            'Peak Rate': ['800', '800', '800', '800', '800'],
            'Shrink': ['0.9', '0.9', '0.9', '0.9', '0.9'],
            'NGL Yield': ['20', '20', '20', '20', '20'],
            'Oil Yield': ['5', '5', '5', '5', '5'],
            'Fixed Cost': ['1000', '1000', '1000', '1000', '1000'],
            'Variable Gas Cost': ['0.5', '0.5', '0.5', '0.5', '0.5'],
            'Variable Oil Cost': ['3', '3', '3', '3', '3',],
            'Overhead': ['300', '300', '300', '300', '300',]
        }

        for i, j in enumerate(self.paramRowHeaders):
            if j in self.dropDownParams:
                for k in range(len(self.caseColHeaders)):
                    self.dropDownInputs[j][k].setCurrentIndex(self.defaultParams['Decline Type'][k])
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
        
        
        pmean, p10, p50, p90, pfail, pbase = econ.run_econs(params, runSettingsFrame)

        # Populate Decline Plot with curves
        if self.declinePlot.plottedAlready:
            self.declinePlot.clear()
            self.declinePlot.plot(pmean.t[pmean.gross_gas_rate > 0], pmean.gross_gas_rate[pmean.gross_gas_rate > 0], name = 'pmean', pen = self.redPen)
            self.declinePlot.plot(p10.t[p10.gross_gas_rate > 0], p10.gross_gas_rate[p10.gross_gas_rate > 0], name = 'p10', pen = self.greenPen)
            self.declinePlot.plot(p50.t[p50.gross_gas_rate > 0], p50.gross_gas_rate[p50.gross_gas_rate > 0], name = 'p50', pen = self.bluePen)
            self.declinePlot.plot(p90.t[p90.gross_gas_rate > 0], p90.gross_gas_rate[p90.gross_gas_rate > 0], name = 'p90', pen = self.yellowPen)
            if runSettingsFrame['settings']['incremental'] == 'Incremental':
                self.declinePlot.plot(pbase.t[pbase.gross_gas_rate > 0], pbase.gross_gas_rate[pbase.gross_gas_rate > 0], name = 'pbase', pen = self.purplePen)
            self.declinePlot.plot(pfail.t[pfail.gross_gas_rate > 0], pfail.gross_gas_rate[pfail.gross_gas_rate > 0], name = 'pfail', pen = self.orangePen)
        else:
            self.declinePlot.plot(pmean.t[pmean.gross_gas_rate > 0], pmean.gross_gas_rate[pmean.gross_gas_rate > 0], name = 'pmean', pen = self.redPen)
            self.declinePlot.plot(p10.t[p10.gross_gas_rate > 0], p10.gross_gas_rate[p10.gross_gas_rate > 0], name = 'p10', pen = self.greenPen)
            self.declinePlot.plot(p50.t[p50.gross_gas_rate > 0], p50.gross_gas_rate[p50.gross_gas_rate > 0], name = 'p50', pen = self.bluePen)
            self.declinePlot.plot(p90.t[p90.gross_gas_rate > 0], p90.gross_gas_rate[p90.gross_gas_rate > 0], name = 'p90', pen = self.yellowPen)
            if runSettingsFrame['settings']['incremental'] == 'Incremental':
                self.declinePlot.plot(pbase.t[pbase.gross_gas_rate > 0], pbase.gross_gas_rate[pbase.gross_gas_rate > 0], name = 'pbase', pen = self.purplePen)
            self.declinePlot.plot(pfail.t[pfail.gross_gas_rate > 0], pfail.gross_gas_rate[pfail.gross_gas_rate > 0], name = 'pfail', pen = self.orangePen)
            self.declinePlot.plottedAlready = True

        # Prep pandas object resultTableFrame
        resultsTableFrame = pd.DataFrame([p10.getMetricsDict(), p50.getMetricsDict(), p90.getMetricsDict(),
            pfail.getMetricsDict(), pbase.getMetricsDict(), pmean.getMetricsDict()], index = ['p10', 'p50', 'p90', 'pfail', 'pbase', 'pmean'])
        resultsTableFrame = resultsTableFrame.T.fillna('NA')

        # Populate results table from resultsTableFrame (above)
        for i, k in enumerate(resultsTableFrame.index):
            for j, l in enumerate(resultsTableFrame.columns):
                self.econResultsTable.setItem(i, j, QTableWidgetItem(resultsTableFrame[l][k]))
        print(params['p50']['capex'])

        # Populate results plots (bottom right quadrant)
        # Statement below executes each button-press after the first
        if self.cumCashFlowPlot.plottedAlready:
            # Redraw cumulative cash flow plot
            self.cumCashFlowPlot.clear()
            self.cumCashFlowPlot.plot(pmean.t[pmean.gross_gas_rate > 0], pmean.ccf_pv0[pmean.gross_gas_rate > 0] / 1000, name = 'pmean PV0', pen = self.redPen)
            self.cumCashFlowPlot.plot(pmean.t[pmean.gross_gas_rate > 0], pmean.ccf_pv10[pmean.gross_gas_rate > 0] / 1000, name = 'pmean PV10', pen = self.dottedRedPen)
            
            # Redraw pie charts
            # To-do: update to use "in place redraw" instead of "clear and redraw"
            self.mplFigure1.axes.cla()
            self.mplFigure2.axes.cla()
            revPieData = [pmean.NET_GAS_REV, pmean.NET_NGL_REV, pmean.NET_OIL_REV]
            prodPieData = [pmean.GROSS_GAS_BOE, pmean.GROSS_NGL, pmean.GROSS_OIL]
            self.mplFigure1.axes.pie(x = revPieData, colors = ['r', 'orange', 'green'], labels = ['Gas', 'NGL', 'Oil'], autopct = '%.1f%%')
            self.mplFigure2.axes.pie(x = prodPieData, colors = ['r', 'orange', 'green'], labels = ['Gas', 'NGL', 'Oil'], autopct = '%.1f%%')
            self.mplFigure1.axes.set_title('Revenue Split by Product')
            self.mplFigure2.axes.set_title('Volume (BOE) Split by Product')
            self.mplFigure1.draw()
            self.mplFigure2.draw()
        # Statement below executes for the first button-press
        else:
            # Plot cumulative cash flow plot
            self.cumCashFlowPlot.plot(pmean.t[pmean.gross_gas_rate > 0], pmean.ccf_pv0[pmean.gross_gas_rate > 0] / 1000, name = 'pmean PV0', pen = self.redPen)
            self.cumCashFlowPlot.plot(pmean.t[pmean.gross_gas_rate > 0], pmean.ccf_pv10[pmean.gross_gas_rate > 0] / 1000, name = 'pmean PV10', pen = self.dottedRedPen)
            self.cumCashFlowPlot.plottedAlready = True

            # Plot pie charts
            self.mplFigure1.axes.cla()
            self.mplFigure2.axes.cla()
            revPieData = [pmean.NET_GAS_REV, pmean.NET_NGL_REV, pmean.NET_OIL_REV]
            prodPieData = [pmean.GROSS_GAS_BOE, pmean.GROSS_NGL, pmean.GROSS_OIL]
            self.mplFigure1.axes.pie(x = revPieData, colors = ['r', 'orange', 'green'], labels = ['Gas', 'NGL', 'Oil'], autopct = '%.1f%%')
            self.mplFigure2.axes.pie(x = prodPieData, colors = ['r', 'orange', 'green'], labels = ['Gas', 'NGL', 'Oil'], autopct = '%.1f%%')
            self.mplFigure1.axes.set_title('Revenue Split by Product')
            self.mplFigure2.axes.set_title('Volume (BOE) Split by Product')
            self.mplFigure1.draw()
            self.mplFigure2.draw()

# Matplotlib canvas class for QT integration
class plotCanvas(mplCanvas):
    def __init__(self, parent = None):
        matplotlib.rcParams['figure.facecolor'] = 'black'
        matplotlib.rcParams['text.color'] = 'white'
        matplotlib.rcParams['lines.linewidth'] = 3
        fig = plt.Figure()
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

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