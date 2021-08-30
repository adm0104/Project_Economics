import numpy as np
import pandas as pd
import Toolbox as tb

class case:
    def __init__(self, params):
        # Builds case time series table as a Pandas Dataframe, stored as an object property
        # Saves case parameters (non-time-series data) in a Pandas Dataframe, stored as an object property
        # Saves all timesteps from time series as dt property for use in decline calculations
        #
        # *** Inputs ***
        # months:           # of months in run                          (months)
        # WI:               Working Interest                            (fraction)
        # NRI:              Net Revenue Interest                        (fraction)
        #
        # *** Generated Object Properties ***
        # dt:               each instantaneous timestep in the run      (days)
        # timeSeries:       dataframe in which full run will be stored  (dataframe)
        #   tStart:         entry time for each month                   (days)
        #   tEnd:           ending time for each month                  (days)
        #   tMid:           mid-point time for each month               (days)
        # daysInMonth:      constant # of days per month                (days)
        #   **Note** daysInMonth should be 30.4375 to match Aries results
        # params:           dataframe in which parameters are stored    (dataframe)
        #   months:         # of months in run                          (months)
        #   WI:             Working Interest                            (fraction)
        #   NRI:            Net Revenue Interest                        (fraction)

        self.name = params[0]['casename']
        self.params = params
        self.params.columns = [self.name]
        self.months = self.params[self.name]['months']
        
        self.daysInMonth = 30.4375
        self.daysInYear = self.daysInMonth * 12

        self.timeSeries = pd.DataFrame(
            columns = [
                'tStart', 'tMid', 'tEnd', 'qStart', 'qEnd', 'Volume', 'grossGas', 'averageMonthlyGasRate',
                'grossOil', 'grossNGL', 'grossBOE', 'grossMCFE', 'netGas', 'netOil', 'netNGL', 'netBOE', 'netMCFE',
                'gasPriceBase', 'gasPriceRealized', 'oilPriceBase', 'oilPriceRealized', 'nglPriceRealized',
                'netGasRevenue', 'netOilRevenue', 'netNglRevenue', 'netTotalRevenue', 'fixedCost', 'variableCost',
                'overhead', 'severanceTax', 'adValoremTax', 'totalExpense', 'grossCapex', 'netCapex', 'netCapexDiscounted',
                'netPV0', 'netPV10', 'cumNetPV0', 'cumNetPV10'
            ],
            index = [
                np.arange(self.months)
            ]
        )
        
        self.dt = np.linspace(0, self.months, self.months + 1) * self.daysInMonth
        self.timeSeries['tStart'] = self.dt[:-1]
        self.timeSeries['tEnd'] = self.dt[1:]
        self.timeSeries['tMid'] = self.timeSeries['tEnd'] - self.daysInMonth / 2

    def decline(self):

        Decline_type = self.params[self.name]['Decline_type']
        qi = self.params[self.name]['qi']
        Di_sec = self.params[self.name]['Di_sec']
        Dterm_sec = self.params[self.name]['Dterm_sec']
        b = self.params[self.name]['b']
        peak = self.params[self.name]['peak']

        if Decline_type == 'Exponential' or Decline_type == 1:
            Di = -np.log(1 - Di_sec)
            q = qi * np.exp(-Di * self.dt * (1 / self.daysInYear))
            self.timeSeries['qStart'] = q[:-1]
            self.timeSeries['qEnd'] = q[1:]
            self.timeSeries['Volume'] = (self.timeSeries['qStart'] - self.timeSeries['qEnd']) / Di * self.daysInYear

        elif Decline_type == 'Hyperbolic' or  Decline_type == 2:
            Di = ((1 - Di_sec) ** (-b) - 1) / b
            q = qi * (1 + b * Di * self.dt * (1 / self.daysInYear)) ** (-1 / b)
            self.timeSeries['qStart'] = q[:-1]
            self.timeSeries['qEnd'] = q[1:]
            De = Di / (1 + b * Di * self.dt[:-1] / self.daysInYear)
            if b == 1:
                self.timeSeries['Volume'] = (self.timeSeries['qStart'] / De) * np.log(self.timeSeries['qStart'] / self.timeSeries['qEnd']) * self.daysInYear
            else:
                self.timeSeries['Volume'] = (self.timeSeries['qStart'] ** b) * (self.timeSeries['qStart'] ** (1 - b) - self.timeSeries['qEnd'] ** (1 - b)) / ((1 - b) * De) * self.daysInYear

        elif Decline_type == 'Harmonic' or Decline_type == 3:
            Di = Di_sec / (1 - Di_sec)
            q = qi / (1 + Di * self.dt / self.daysInYear)
            self.timeSeries['qStart'] = q[:-1]
            self.timeSeries['qEnd'] = q[1:]
            De = Di / (1 + Di * self.dt[:-1] / self.daysInYear)
            self.timeSeries['Volume'] = (self.timeSeries['qStart'] / De) * np.log(self.timeSeries['qStart'] / self.timeSeries['qEnd']) * self.daysInYear

        elif Decline_type == 'Modified Arps' or Decline_type == 4:
            Di = ((1 - Di_sec) ** (-b) - 1) / b
            Dterm = -np.log(1 - Dterm_sec)
            tSwitch = (Di / Dterm - 1) / (b * Di) * self.daysInYear
            qSwitch = qi * (1 + b * Di * tSwitch * (1 / self.daysInYear)) ** (-1 / b)
            self.qSwitch = qSwitch
            self.tSwitch = tSwitch
            q = np.concatenate([
                qi * (1 + b * Di * self.dt[self.dt < tSwitch] * (1 / self.daysInYear)) ** (-1 / b),
                qSwitch * np.exp(-Dterm * (self.dt[self.dt >= tSwitch] - tSwitch) * (1 / self.daysInYear))
            ])
            self.timeSeries['qStart'] = q[:-1]
            self.timeSeries['qEnd'] = q[1:]
            De = Di / (1 + b * Di * self.dt[self.dt < tSwitch] / self.daysInYear)
            if b == 1:
                qStart = self.timeSeries['qStart'][self.timeSeries['tEnd'] < tSwitch]
                qEnd = self.timeSeries['qEnd'][self.timeSeries['tEnd'] < tSwitch]
                self.timeSeries.loc[self.timeSeries['tEnd'] < tSwitch, 'Volume'] = (qStart / De[:-1]) * np.log(qStart / qEnd) * self.daysInYear
                switchIndex = self.timeSeries.loc[(self.timeSeries['tEnd'] > tSwitch) & (self.timeSeries['tStart'] < tSwitch), 'Volume'].index[0][0]
                self.timeSeries.loc[switchIndex, 'Volume'] = (self.timeSeries['qStart'][switchIndex] * np.log(self.timeSeries['qStart'][switchIndex] / qSwitch) / De[-1] + (qSwitch - self.timeSeries['qEnd'][switchIndex]) / Dterm) * self.daysInYear
            else:
                qStart = self.timeSeries['qStart'][self.timeSeries['tEnd'] < tSwitch]
                qEnd = self.timeSeries['qEnd'][self.timeSeries['tEnd'] < tSwitch]
                self.timeSeries.loc[self.timeSeries['tEnd'] < tSwitch, 'Volume'] = (qStart ** b) * (qStart ** (1 - b) - qEnd ** (1 - b)) / ((1 - b) * De[:-1]) * self.daysInYear
                switchIndex = self.timeSeries.loc[(self.timeSeries['tEnd'] > tSwitch) & (self.timeSeries['tStart'] < tSwitch), 'Volume'].index[0][0]
                self.timeSeries.loc[switchIndex, 'Volume'] = ((self.timeSeries['qStart'][switchIndex] ** b) * (self.timeSeries['qStart'][switchIndex] ** (1 - b) - qSwitch ** (1 - b)) / ((1 - b) * De[-1]) + (qSwitch - self.timeSeries['qEnd'][switchIndex]) / Dterm) * self.daysInYear
            qStart = self.timeSeries['qStart'][self.timeSeries['tStart'] > tSwitch]
            qEnd = self.timeSeries['qEnd'][self.timeSeries['tStart'] > tSwitch]
            self.timeSeries.loc[self.timeSeries['tStart'] > tSwitch, 'Volume'] = (qStart - qEnd) / Dterm * self.daysInYear
            
        elif Decline_type == 5 or Decline_type == 'No Rate':
            self.timeSeries['qStart'] = 0
            self.timeSeries['qEnd'] = 0
            self.timeSeries['Volume'] = 0

        elif Decline_type == 'CBM Dewatering/Incline' or Decline_type == 6:
            peak = int(peak)
            tPeak = peak * self.daysInMonth
            Di = -np.log(1 - Di_sec)
            Dterm = -np.log(1 - Dterm_sec)
            qPeak = qi * np.exp(-Di * self.timeSeries['tStart'][peak] * (1 / self.daysInYear))
            q = np.concatenate([
                qi * np.exp(-Di * self.dt[self.dt < tPeak] * (1 / self.daysInYear)),
                qPeak * np.exp(-Dterm * (self.dt[self.dt >= tPeak] - tPeak) * (1 / self.daysInYear))
            ])
            self.timeSeries['qStart'] = q[:-1]
            self.timeSeries['qEnd'] = q[1:]
            De = np.concatenate([
                np.ones(peak) * Di,
                np.ones(self.months - peak) * Dterm
            ])
            self.timeSeries['Volume'] = (self.timeSeries['qStart'] - self.timeSeries['qEnd']) / De * self.daysInYear

    def production(self):
        
        self.timeSeries['grossGas'] = self.timeSeries['Volume']
        self.timeSeries['averageMonthlyGasRate'] = self.timeSeries['Volume'] / self.daysInMonth
        self.timeSeries['grossOil'] = self.timeSeries['grossGas'] * self.params[self.name]['oilYield'] / 1000
        self.timeSeries['grossNGL'] = self.timeSeries['grossGas'] * self.params[self.name]['nglYield'] / 1000
        self.timeSeries['grossBOE'] = self.timeSeries['grossGas'] / 6 + self.timeSeries['grossOil'] + self.timeSeries['grossNGL']
        self.timeSeries['grossMCFE'] = self.timeSeries['grossBOE'] * 6
        self.timeSeries['netGas'] = self.timeSeries['grossGas'] * self.params[self.name]['shrink'] * self.params[self.name]['NRI']
        self.timeSeries['netOil'] = self.timeSeries['grossOil'] * self.params[self.name]['NRI']
        self.timeSeries['netNGL'] = self.timeSeries['grossNGL'] * self.params[self.name]['NRI']
        self.timeSeries['netBOE'] = self.timeSeries['netGas'] / 6 + self.timeSeries['netOil'] + self.timeSeries['netNGL']
        self.timeSeries['netMCFE'] = self.timeSeries['netBOE'] * 6
        
    def pricing(self,type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff):
        if type == "flat":
            self.timeSeries['gasPriceBase'] = np.ones(self.months) * gas_price
            self.timeSeries['gasPriceRealized'] = self.timeSeries['gasPriceBase'] + gas_diff
            self.timeSeries['oilPriceBase'] = np.ones(self.months) * oil_price
            self.timeSeries['oilPriceRealized'] = self.timeSeries['oilPriceBase'] + oil_diff
            self.timeSeries['nglPriceRealized'] = self.timeSeries['oilPriceBase'] * ngl_diff
    
    def revenue(self):
        self.timeSeries['netGasRevenue'] = self.timeSeries['netGas'] * self.timeSeries['gasPriceRealized']
        self.timeSeries['netOilRevenue'] = self.timeSeries['netOil'] * self.timeSeries['oilPriceRealized']
        self.timeSeries['netNglRevenue'] = self.timeSeries['netNGL'] * self.timeSeries['nglPriceRealized']
        self.timeSeries['netTotalRevenue'] = self.timeSeries['netGasRevenue'] + self.timeSeries['netOilRevenue'] + self.timeSeries['netNglRevenue']

    def expenses(self):
        self.timeSeries['fixedCost'] = self.params[self.name]['fixedCost'] * self.params[self.name]['WI']
        self.timeSeries['variableCost'] = (self.timeSeries['grossGas'] * self.params[self.name]['shrink'] * self.params[self.name]['varGasCost']\
            + self.timeSeries['grossOil'] * self.params[self.name]['varOilCost']) * self.params[self.name]['WI']
        self.timeSeries['overhead'] = np.ones(self.months) * self.params[self.name]['overhead'] * self.params[self.name]['WI']
        self.timeSeries['severanceTax'] = self.params[self.name]['severanceTax'] * self.timeSeries['netTotalRevenue']
        self.timeSeries['adValoremTax'] = self.params[self.name]['adValoremTax'] * (self.timeSeries['netTotalRevenue'] - self.timeSeries['severanceTax'])
        self.timeSeries['totalExpense'] = self.timeSeries['fixedCost'] + self.timeSeries['variableCost'] + self.timeSeries['overhead']\
            + self.timeSeries['adValoremTax'] + self.timeSeries['severanceTax']
    
    def capex(self):                            
        self.timeSeries['grossCapex'] = 0
        self.timeSeries['netCapex'] = 0
        self.timeSeries['netCapexDiscounted'] = 0
        self.timeSeries.loc[0, 'grossCapex'] = self.params[self.name]['firstMonthCapex']
        self.timeSeries.loc[0, 'netCapex'] = self.params[self.name]['firstMonthCapex'] * self.params[self.name]['NRI']
        self.timeSeries.loc[0, 'netCapexDiscounted'] = self.params[self.name]['firstMonthCapex'] * self.params[self.name]['NRI']

    def swansons_mean(self, p10, p50, p90, pfail, p_s):
        # Calculate production for a "mean" case (non-incremental)
        # Replaces production, pricing, revenue, expenses, and capex class methods
        # Production Section
        self.timeSeries['grossGas'] = p_s * (0.3 * p10.grossGas + 0.4 * p50.grossGas + 0.3 * p90.grossGas) + (1-p_s) * pfail.grossGas
        self.q = p_s * (0.3 * p10.q + 0.4 * p50.q + 0.3 * p90.q) + (1-p_s) * pfail.q
        self.grossGas = self.timeSeries['grossGas']
        self.averageMonthlyRate = self.timeSeries['grossGas'] / 30.4375
        self.timeSeries['grossOil'] = p_s * (0.3 * p10.gross_oil + 0.4 * p50.gross_oil + 0.3 * p90.gross_oil) + (1-p_s) * pfail.gross_oil
        self.timeSeries['grossNGL'] = p_s * (0.3 * p10.gross_ngl + 0.4 * p50.gross_ngl + 0.3 * p90.gross_ngl) + (1-p_s) * pfail.gross_ngl
        self.timeSeries['grossBOE'] = self.timeSeries['grossGas'] / 6 + self.timeSeries['grossOil'] + self.timeSeries['grossNGL']
        self.gross_mcfe = self.timeSeries['grossBOE'] * 6
        self.timeSeries['netGas'] = p_s * (0.3 * p10.net_gas + 0.4 * p50.net_gas + 0.3 * p90.net_gas) + (1-p_s) * pfail.net_gas
        self.timeSeries['netOil'] = p_s * (0.3 * p10.net_oil + 0.4 * p50.net_oil + 0.3 * p90.net_oil) + (1-p_s) * pfail.net_oil
        self.timeSeries['netNGL'] = p_s * (0.3 * p10.net_ngl + 0.4 * p50.net_ngl + 0.3 * p90.net_ngl) + (1-p_s) * pfail.net_ngl
        self.timeSeries['netBOE'] = self.timeSeries['netGas'] / 6 + self.timeSeries['netOil'] + self.timeSeries['netNGL']
        self.timeSeries['netMCFE'] = self.timeSeries['netBOE'] * 6
        self.params[self.name]['shrink'] = np.sum(self.timeSeries['netGas']) / (np.sum(self.grossGas) * self.params['NRI'])

        # Pricing Section
        self.timeSeries['gasPriceBase'] = p50.gas_price_base
        self.timeSeries['oilPriceBase'] = p50.oil_price_base
        self.timeSeries['gasPriceRealized'] = p50.gas_price_real
        self.timeSeries['oilPriceRealized'] = p50.oil_price_real
        self.timeSeries['nglPriceRealized'] = p50.ngl_price_real

        # Revenue Section
        self.timeSeries['netGasRevenue'] = self.timeSeries['netGas'] * self.timeSeries['gasPriceRealized']
        self.timeSeries['netOilRevenue'] = self.timeSeries['netOil'] * self.timeSeries['oilPriceRealized']
        self.timeSeries['netNglRevenue'] = self.timeSeries['netNGL'] * self.timeSeries['nglPriceRealized']
        self.timeSeries['netTotalRevenue'] = self.timeSeries['netGasRevenue'] + self.timeSeries['netOilRevenue'] + self.timeSeries['netNglRevenue']

        # Expenses Section
        self.timeSeries['fixedCost'] = p_s * (0.3 * p10.self.params['fixedCost'] + 0.4 * p50.self.params['fixedCost'] + 0.3 * p90.self.params['fixedCost']) + (1-p_s) * pfail.self.params['fixedCost']
        # self.timeSeries['variableCost'] = (self.grossGas * self.params[self.name]['shrink'] * p50.var_gas_rate + self.timeSeries['grossOil'] * p50.var_oil_rate) * self.params['WI']
        self.timeSeries['variableCost'] = p_s * (0.3 * p10.var_cost + 0.4 * p50.var_cost + 0.3 * p90.var_cost) + (1-p_s) * pfail.var_cost
        self.timeSeries['overhead'] = p_s * (0.3 * p10.overhead + 0.4 * p50.overhead + 0.3 * p90.overhead) + (1-p_s) * pfail.overhead
        self.timeSeries['severanceTax'] = p50.sev_rate * self.timeSeries['netTotalRevenue']
        self.timeSeries['adValoremTax'] = p50.adval_rate * (self.timeSeries['netTotalRevenue'] - self.timeSeries['severanceTax'])
        self.timeSeries['totalExpense'] = self.timeSeries['fixedCost'] + self.timeSeries['variableCost'] + self.timeSeries['overhead'] + self.timeSeries['adValoremTax'] + self.timeSeries['severanceTax']

        # Capex Section
        self.gross_capex = p_s * (0.3 * p10.gross_capex + 0.4 * p50.gross_capex + 0.3 * p90.gross_capex) + (1-p_s) * pfail.gross_capex
        self.net_capex = p_s * (0.3 * p10.net_capex + 0.4 * p50.net_capex + 0.3 * p90.net_capex) + (1-p_s) * pfail.net_capex
        self.net_capex_disc = np.zeros(self.months)
        for i in range(self.months):
            self.net_capex_disc[i] = self.net_capex[i] / (1+0.1)**((self.timeSeries['tMid'][i] - 30.4375 / 2) / self.daysInYear)
    def swansons_mean_inc(self, p10, p50, p90, pfail, pbase, p_s):
        # Calculate production for a "mean" case (incremental)
        # Replaces "production" and "expenses" class methods
        # Calculate production for a "mean" case (non-incremental)
        # Replaces production, pricing, revenue, expenses, and capex class methods
        # Production Section
        self.timeSeries['grossGas'] = p_s * (0.3 * p10.grossGas + 0.4 * p50.grossGas + 0.3 * p90.grossGas) + (1-p_s) * pfail.grossGas - pbase.grossGas
        self.q = p_s * (0.3 * p10.q + 0.4 * p50.q + 0.3 * p90.q) + (1-p_s) * pfail.q - pbase.q
        self.grossGas = self.timeSeries['grossGas']
        self.averageMonthlyRate = self.timeSeries['grossGas'] / 30.4375
        self.timeSeries['grossOil'] = p_s * (0.3 * p10.gross_oil + 0.4 * p50.gross_oil + 0.3 * p90.gross_oil) + (1-p_s) * pfail.gross_oil - pbase.gross_oil
        self.timeSeries['grossNGL'] = p_s * (0.3 * p10.gross_ngl + 0.4 * p50.gross_ngl + 0.3 * p90.gross_ngl) + (1-p_s) * pfail.gross_ngl - pbase.gross_ngl
        self.timeSeries['grossBOE'] = self.timeSeries['grossGas'] / 6 + self.timeSeries['grossOil'] + self.timeSeries['grossNGL']
        self.gross_mcfe = self.timeSeries['grossBOE'] * 6
        self.timeSeries['netGas'] = p_s * (0.3 * p10.net_gas + 0.4 * p50.net_gas + 0.3 * p90.net_gas) + (1-p_s) * pfail.net_gas - pbase.net_gas
        self.timeSeries['netOil'] = p_s * (0.3 * p10.net_oil + 0.4 * p50.net_oil + 0.3 * p90.net_oil) + (1-p_s) * pfail.net_oil - pbase.net_oil
        self.timeSeries['netNGL'] = p_s * (0.3 * p10.net_ngl + 0.4 * p50.net_ngl + 0.3 * p90.net_ngl) + (1-p_s) * pfail.net_ngl - pbase.net_ngl
        self.timeSeries['netBOE'] = self.timeSeries['netGas'] / 6 + self.timeSeries['netOil'] + self.timeSeries['netNGL']
        self.timeSeries['netMCFE'] = self.timeSeries['netBOE'] * 6
        self.params[self.name]['shrink'] = np.sum(self.timeSeries['netGas']) / (np.sum(self.grossGas) * self.params['NRI'])

        # Pricing Section
        self.timeSeries['gasPriceBase'] = p50.gas_price_base
        self.timeSeries['oilPriceBase'] = p50.oil_price_base
        self.timeSeries['gasPriceRealized'] = p50.gas_price_real
        self.timeSeries['oilPriceRealized'] = p50.oil_price_real
        self.timeSeries['nglPriceRealized'] = p50.ngl_price_real

        # Revenue Section
        self.timeSeries['netGasRevenue'] = self.timeSeries['netGas'] * self.timeSeries['gasPriceRealized']
        self.timeSeries['netOilRevenue'] = self.timeSeries['netOil'] * self.timeSeries['oilPriceRealized']
        self.timeSeries['netNglRevenue'] = self.timeSeries['netNGL'] * self.timeSeries['nglPriceRealized']
        self.timeSeries['netTotalRevenue'] = self.timeSeries['netGasRevenue'] + self.timeSeries['netOilRevenue'] + self.timeSeries['netNglRevenue']

        # Expenses Section
        self.timeSeries['fixedCost'] = p_s * (0.3 * p10.self.params['fixedCost'] + 0.4 * p50.self.params['fixedCost'] + 0.3 * p90.self.params['fixedCost']) + (1-p_s) * pfail.self.params['fixedCost'] - pbase.self.params['fixedCost']
        # self.timeSeries['variableCost'] = (self.grossGas * self.params[self.name]['shrink'] * p50.var_gas_rate + self.timeSeries['grossOil'] * p50.var_oil_rate) * self.params['WI']
        self.timeSeries['variableCost'] = p_s * (0.3 * p10.var_cost + 0.4 * p50.var_cost + 0.3 * p90.var_cost) + (1-p_s) * pfail.var_cost - pbase.var_cost
        self.timeSeries['overhead'] = p_s * (0.3 * p10.overhead + 0.4 * p50.overhead + 0.3 * p90.overhead) + (1-p_s) * pfail.overhead - pbase.overhead
        self.timeSeries['severanceTax'] = p50.sev_rate * self.timeSeries['netTotalRevenue']
        self.timeSeries['adValoremTax'] = p50.adval_rate * (self.timeSeries['netTotalRevenue'] - self.timeSeries['severanceTax'])
        self.timeSeries['totalExpense'] = self.timeSeries['fixedCost'] + self.timeSeries['variableCost'] + self.timeSeries['overhead'] + self.timeSeries['adValoremTax'] + self.timeSeries['severanceTax']

        # Capex Section
        self.gross_capex = p_s * (0.3 * p10.gross_capex + 0.4 * p50.gross_capex + 0.3 * p90.gross_capex) + (1-p_s) * pfail.gross_capex - pbase.gross_capex
        self.net_capex = p_s * (0.3 * p10.net_capex + 0.4 * p50.net_capex + 0.3 * p90.net_capex) + (1-p_s) * pfail.net_capex - pbase.net_capex
        self.net_capex_disc = np.zeros(self.months)
        for i in range(self.months):
            self.net_capex_disc[i] = self.net_capex[i] / (1+0.1)**((self.timeSeries['tMid'][i] - 30.4375 / 2) / self.daysInYear)
    def incrementalize(self, pbase):
        # Calculate production for a "mean" case (incremental)
        # Replaces "production" and "expenses" class methods
        # Calculate production for a "mean" case (non-incremental)
        # Replaces production, pricing, revenue, expenses, and capex class methods
        # Production Section
        self.timeSeries['grossGas'] = self.timeSeries['grossGas'] - pbase.grossGas
        self.q = self.q - pbase.q
        self.grossGas = self.timeSeries['grossGas']
        # self.averageMonthlyRate = self.timeSeries['grossGas'] / 30.4375
        self.timeSeries['grossOil'] = self.timeSeries['grossOil'] - pbase.gross_oil
        self.timeSeries['grossNGL'] = self.timeSeries['grossNGL'] - pbase.gross_ngl
        self.timeSeries['grossBOE'] = self.timeSeries['grossGas'] / 6 + self.timeSeries['grossOil'] + self.timeSeries['grossNGL']
        self.gross_mcfe = self.timeSeries['grossBOE'] * 6
        self.timeSeries['netGas'] = self.timeSeries['netGas'] - pbase.net_gas
        self.timeSeries['netOil'] = self.timeSeries['netOil'] - pbase.net_oil
        self.timeSeries['netNGL'] = self.timeSeries['netNGL'] - pbase.net_ngl
        self.timeSeries['netBOE'] = self.timeSeries['netGas'] / 6 + self.timeSeries['netOil'] + self.timeSeries['netNGL']
        self.timeSeries['netMCFE'] = self.timeSeries['netBOE'] * 6

        # Revenue Section
        self.timeSeries['netGasRevenue'] = self.timeSeries['netGas'] * self.timeSeries['gasPriceRealized']
        self.timeSeries['netOilRevenue'] = self.timeSeries['netOil'] * self.timeSeries['oilPriceRealized']
        self.timeSeries['netNglRevenue'] = self.timeSeries['netNGL'] * self.timeSeries['nglPriceRealized']
        self.timeSeries['netTotalRevenue'] = self.timeSeries['netGasRevenue'] + self.timeSeries['netOilRevenue'] + self.timeSeries['netNglRevenue']

        # Expenses Section
        self.timeSeries['fixedCost'] = self.timeSeries['fixedCost'] - pbase.self.params['fixedCost']
        self.timeSeries['variableCost'] = self.timeSeries['variableCost'] - pbase.var_cost
        self.timeSeries['overhead'] = self.timeSeries['overhead'] - pbase.overhead
        self.timeSeries['severanceTax'] = self.sev_rate * self.timeSeries['netTotalRevenue']
        self.timeSeries['adValoremTax'] = self.adval_rate * (self.timeSeries['netTotalRevenue'] - self.timeSeries['severanceTax'])
        self.timeSeries['totalExpense'] = self.timeSeries['fixedCost'] + self.timeSeries['variableCost'] + self.timeSeries['overhead'] + self.timeSeries['adValoremTax'] + self.timeSeries['severanceTax']

        # Capex Section
        self.gross_capex = self.gross_capex - pbase.gross_capex
        self.net_capex = self.net_capex - pbase.net_capex
        self.net_capex_disc = np.zeros(self.months)
        for i in range(self.months):
            self.net_capex_disc[i] = self.net_capex[i] / (1+0.1)**((self.timeSeries['tMid'][i] - 30.4375 / 2) / self.daysInYear)
        self.cash_flow()
        self.life(self.LOSS)
        self.metrics()
    def cashFlow(self):
        self.timeSeries['netPV0'] = self.timeSeries['netTotalRevenue'] - self.timeSeries['netCapex'] - self.timeSeries['totalExpense']
        self.timeSeries['cumNetPV0'] = self.timeSeries.netPV0.cumsum()
        self.timeSeries['netPV10'] = self.timeSeries['netPV0'] / 1.1 ** (self.timeSeries['tStart'] / self.daysInYear)
        self.timeSeries['cumNetPV10'] = self.timeSeries.netPV10.cumsum()

    def life(self):
        if self.params[self.name]['lossFunction'] == "NO":
            self.timeSeries.loc[self.timeSeries['netPV0'] + self.timeSeries['netCapex'] + self.timeSeries['overhead'] < 0] = np.nan
        elif self.params[self.name]['lossFunction'] == "BFIT":
            self.timeSeries.loc[self.timeSeries['netPV0'] + self.timeSeries['netCapex'] < 0] = np.nan
        elif self.params[self.name]['lossFunction'] == "OK":
            None

    def metrics(self):
        self.GROSS_CAPEX = int(round(np.sum(self.gross_capex) / 1000, 2))
        self.NET_CAPEX = int(round(np.sum(self.net_capex) / 1000, 2))
        self.NET_CAPEX_DISC = np.sum(self.net_capex_disc)
        self.PV0 = int(round(np.sum(self.ncf_pv0) / 1000, 2))
        self.PV10 = int(round(np.sum(self.ncf_pv10) / 1000, 2))
        self.netGasSales = np.sum(self.timeSeries['netGas'])
        self.NET_MBOE = int(round(np.sum(self.timeSeries['netBOE']) / 1000, 2))
        self.NET_MMCFE = int(round(np.sum(self.timeSeries['netMCFE']) / 1000, 2))
        self.netBOED = int(round(self.timeSeries['netBOE'][0] / 30.4375, 2))
        self.netMCFED = int(round(self.timeSeries['netMCFE'][0] / 30.4375, 2))
        self.grossGas = round(np.sum(self.grossGas) / 1000000, 2)
        self.grossGas_BOE = round(np.sum(self.grossGas) / 6, 2)
        self.timeSeries['grossNGL'] = round(np.sum(self.timeSeries['grossNGL']))
        self.timeSeries['grossOil'] = round(np.sum(self.timeSeries['grossOil']))
        self.netGasRevenue = round(np.sum(self.timeSeries['netGasRevenue']))
        self.netOilRevenue = round(np.sum(self.timeSeries['netOilRevenue']))
        self.netNGLRevenue = round(np.sum(self.timeSeries['netNglRevenue']))
        if self.NET_CAPEX == 0 or self.grossGas == 0:
            self.PVR0 = 0
            self.PVR10 = 0
        else:
            self.PVR0 = self.PV0 / self.NET_CAPEX + 1
            self.PVR10 = np.sum(self.ncf_pv10) / self.NET_CAPEX_DISC + 1
    def getMetricsDict(self):
        self.metricsDict = {
            'Incremental EUR (Bcf)': str(round(self.grossGas, 2)),
            'Gross CAPEX ($M)': str(round(self.GROSS_CAPEX, 2)),
            'Net CAPEX ($M)': str(round(self.NET_CAPEX)),
            'Net Res. (Mboe)': str(round(self.NET_MBOE)),
            'Net Res. (MMcfe)': str(round(self.NET_MMCFE)),
            'Net IP30 (Boe/d)': str(round(self.netBOED)),
            'Net IP30 (Mcfe/d)': str(round(self.netMCFED)),
            'PV-10 ($M)': str(round(self.PV10)),
            'Payout (Months)': str(self.payout),
            'PVR-10': str(round(self.PVR10, 1))
        }
        return self.metricsDict
    def make_run_table(self):
        self.col_titles = "Time (Days),Gross Gas (Mcf),Gross Oil (Bbl),Gross NGL (Bbl),Net Gas (Mcf),Net Oil (Mcf),Net NGL (Mcf),Base Gas Price ($/Mcf),Base Oil Price ($/Bbl),Realized Gas Price ($/Mcf),Realized Oil Price ($/Mcf,Realized NGL Price ($/Bbl),Gas Revenue ($),Oil Revenue ($),NGL Revenue ($),Total Net Revenue ($),Severance Tax ($),Ad Valorem Tax ($),Total Expenses ($),Net CAPEX ($),Net PV0 ($),Cum PV0 ($),Net PV10 ($),Cum PV10 ($)"
        table = np.column_stack((self.timeSeries['tMid'],self.grossGas,self.timeSeries['grossOil'],self.timeSeries['grossNGL'],self.timeSeries['netGas'],self.timeSeries['netOil'],self.timeSeries['netNGL'],
        self.timeSeries['gasPriceBase'],self.timeSeries['oilPriceBase'],self.timeSeries['gasPriceRealized'],self.timeSeries['oilPriceRealized'],self.timeSeries['nglPriceRealized'],self.timeSeries['netGasRevenue'],
        self.timeSeries['netOilRevenue'],self.timeSeries['netNglRevenue'],self.timeSeries['netTotalRevenue'],self.timeSeries['severanceTax'],self.timeSeries['adValoremTax'],self.timeSeries['totalExpense'],self.net_capex,self.ncf_pv0,
        self.ccf_pv0,self.ncf_pv10,self.ccf_pv10))

        return table