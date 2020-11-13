import numpy as np

class case:
    def __init__(self,dt,WI,NRI):
        self.dt = dt
        self.t = (np.linspace(1,np.size(dt)-1,np.size(dt)-1)-0.5)*30.4375
        self.periods = np.size(self.t)
        self.WI = WI
        self.NRI = NRI
    def decline(self,Decline_type,qi,Di_sec,Dterm_sec,b):
        num_entry = np.size(self.dt)
        num_center = num_entry - 1
        self.q = np.zeros(num_entry)
        self.Qp = np.zeros(num_center)
        if Decline_type == 1:
            ##  1 - Exponential Decline
            Di = -np.log(1-Di_sec)                                                          # Initial decline rate      (Nominal /yr)
            self.q = qi * np.exp(-Di*self.dt * (1/365.25))                                  # Monthly starting rate     (Mcf/d)
            for i in range(num_center):
                self.Qp[i] = (self.q[i]-self.q[i+1]) / Di * 365.25                          # Monthly cumulative        (Mcf)
        elif Decline_type == 2:
            ##  2 - Hyperbolic Decline
            if b > 1: print("*** WARNING - B-FACTOR OVER 1 YIELDS NON-CONVERGENT SOLUTION - CONSIDER MODIFIED HYPERBOLIC ***")
            Di = ((1-Di_sec)**(-b)-1)/b                                                     # Initial decline rate      (Nominal /yr)
            self.q = qi * (1+b*Di*self.dt*(1/365.25))**(-1/b)                               # Monthly starting rate     (Mcf/d)
            if b == 1:
                for i in range(num_center):
                    Dtemp = Di / (1+b*Di*self.dt[i]/365.25)
                    self.Qp[i] = (self.q[i]/Dtemp)*np.log(self.q[i]/self.q[i+1]) * 365.25   # Monthly cumulative        (Mcf)
            else:
                for i in range(num_center):
                    Dtemp = Di / (1+b*Di*self.dt[i]/365.25)
                    self.Qp[i] = (self.q[i]**b)*(self.q[i]**(1-b)-self.q[i+1]**(1-b)) / ((1-b)*Dtemp) * 365.25
        elif Decline_type == 3:
            ## 3 - Harmonic Decline
            Di = Di_sec / (1-Di_sec)                                                        # Initial decline rate      (Nominal /yr)
            self.q = qi / (1+Di*self.dt/365.25)                                             # Monthly starting rate     (Mcf/d)
            for i in range(num_center):
                Dtemp = Di / (1+Di*self.dt[i]/365.25)
                self.Qp[i] = (self.q[i]/Dtemp)*np.log(self.q[i]/self.q[i+1]) * 365.25       # Monthly cumulative        (Mcf)
        elif Decline_type == 4:
            ## 4 - Modified Hyperbolic Decline
            Di = ((1-Di_sec)**(-b)-1) / b                                                   # Initial decline rate      (Nominal /yr)
            Dterm = -np.log(1-Dterm_sec)                                                    # Terminal decline rate     (Nominal /yr)
            t_sw = (Di/Dterm-1) / (b*Di) * 365.25                                           # Hyp->Exp switch time      (days)
            q_sw = qi * (1+b*Di*t_sw*(1/365.25))**(-1/b)                                    # Rate at switch            (Mcf/d)
            sw_pre_ind = int(t_sw // 30.4375)                                               # dt index pre-switch       (no units)
            qi_hind = q_sw * np.exp(Dterm*t_sw*(1/365.25))                                  # Hindcast qi for exp.      (Mcf/d)
            for i in range(sw_pre_ind+1):
                self.q[i] = qi * (1+b*Di*self.dt[i]*(1/365.25))**(-1/b)                     # Hyperbolic leg rates      (Mcf/d)
            for i in range(sw_pre_ind+1,num_entry):
                self.q[i] = qi_hind * np.exp(-Dterm*self.dt[i]*(1/365.25))                  # Exponential leg rates     (Mcf/d)
            if b == 1:
                for i in range(sw_pre_ind):
                    Dtemp = Di / (1+b*Di*self.dt[i]/365.25)
                    self.Qp[i] = (self.q[i]/Dtemp)*np.log(self.q[i]/self.q[i+1]) * 365.25   # Monthly cumulative        (Mcf)
                Dtemp = Di / (1+b*Di*self.dt[i+1]/365.25)
                self.Qp[sw_pre_ind] = (self.q[i+1]*np.log(self.q[i+1]/q_sw)/Dtemp + (q_sw-self.q[i+2])/Dterm) * 365.25
                for i in range(sw_pre_ind+1,num_center):
                    self.Qp[i] = (self.q[i]-self.q[i+1])/Dterm * 365.25
            else:
                for i in range(sw_pre_ind):
                    Dtemp = Di / (1+b*Di*self.dt[i]/365.25)
                    self.Qp[i] = (self.q[i]**b)*(self.q[i]**(1-b)-self.q[i+1]**(1-b)) / ((1-b)*Dtemp) * 365.25
                Dtemp = Di / (1+b*Di*self.dt[i+1]/365.25)
                self.Qp[sw_pre_ind] = ((self.q[i+1]**b)*(self.q[i+1]**(1-b)-q_sw**(1-b)) / ((1-b)*Dtemp) + (q_sw-self.q[i+2])/Dterm) * 365.25
                for i in range(sw_pre_ind+1,num_center):
                    self.Qp[i] = (self.q[i]-self.q[i+1])/Dterm * 365.25
    def production(self,oil_yield,ngl_yield,shrink):
        self.shrink = shrink
        self.oil_yield = oil_yield
        self.ngl_yield = ngl_yield
        self.gross_gas = self.Qp
        self.gross_oil = self.Qp * self.oil_yield / 1000
        self.gross_ngl = self.Qp * self.ngl_yield / 1000
        self.gross_boe = self.Qp / 6 + self.gross_oil + self.gross_ngl
        self.gross_mcfe = self.gross_boe * 6
        self.net_gas = self.gross_gas * self.shrink * self.NRI
        self.net_oil = self.gross_oil * self.NRI
        self.net_ngl = self.gross_ngl * self.NRI
        self.net_boe = self.net_gas / 6 + self.net_oil + self.net_ngl
        self.net_mcfe = self.net_boe * 6
    def pricing(self,type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff):
        if type == "flat":
            self.gas_price_base = np.ones(self.periods) * gas_price
            self.gas_price_real = self.gas_price_base + gas_diff
            self.oil_price_base = np.ones(self.periods) * oil_price
            self.oil_price_real = self.oil_price_base + oil_diff
            self.ngl_price_real = self.oil_price_base * ngl_diff
        else:
            pass
    def revenue(self):
        self.rev_gas = self.net_gas * self.gas_price_real
        self.rev_oil = self.net_oil * self.oil_price_real
        self.rev_ngl = self.net_ngl * self.ngl_price_real
        self.rev_total = self.rev_gas + self.rev_oil + self.rev_ngl
    def expenses(self,fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate):
        self.fixed_cost = np.ones(self.periods) * fixed_cost * self.WI
        self.var_cost = (self.gross_gas * self.shrink * var_gas_cost + self.gross_oil * var_oil_cost) * self.WI
        self.overhead = np.ones(self.periods) * overhead * self.WI
        self.sev_tax = sev_rate * self.rev_total
        self.adval_tax = adval_rate * (self.rev_total - self.sev_tax)
        self.exp_total = self.fixed_cost + self.var_cost + self.overhead + self.adval_tax + self.sev_tax
    def capex(self,month,capex):                            
        self.gross_capex = np.zeros(self.periods)
        self.net_capex = np.zeros(self.periods)
        self.net_capex_disc = np.zeros(self.periods)
        j = 0
        for i in month:
            self.gross_capex[i] = capex[j]
            self.net_capex[i] = capex[j] * self.WI
            self.net_capex_disc[i] = capex[j] / (1+0.1)**(month[j] / 365.25)
            j += 1
    def cash_flow(self):
        self.ncf_pv0 = self.rev_total - self.net_capex - self.exp_total
        self.ccf_pv0 = np.zeros(self.periods)
        self.ccf_pv0[0] = self.ncf_pv0[0]
        self.ncf_pv10 = (self.rev_total - self.exp_total) / (1+0.1)**((self.t) / 365.25) - self.net_capex_disc
        self.ccf_pv10 = np.zeros(self.periods)
        self.ccf_pv10[0] = self.ncf_pv10[0]
        for i in range(1,self.periods):
            self.ccf_pv0[i] = self.ncf_pv0[i] + self.ccf_pv0[i-1]
            self.ccf_pv10[i] = self.ncf_pv10[i] + self.ccf_pv10[i-1]
    def life(self,LOSS):
        if LOSS == "NO":
            # Truncate when cash flow is negative, ignoring overhead
            life_ind = 0
            detect = self.rev_total[0] - self.fixed_cost[0] - self.var_cost[0] - self.sev_tax[0] - self.adval_tax[0]
            while detect > 0 and life_ind < self.periods-1:
                life_ind+=1
                detect = self.rev_total[life_ind] - self.fixed_cost[life_ind] - self.var_cost[life_ind] - self.sev_tax[life_ind] - self.adval_tax[life_ind]
            for i in range(life_ind,self.periods):
                self.gross_gas[i] = 0
                self.gross_oil[i] = 0
                self.gross_ngl[i] = 0
                self.gross_boe[i] = 0
                self.gross_mcfe[i] = 0
                self.net_gas[i] = 0
                self.net_oil[i] = 0
                self.net_ngl[i] = 0
                self.net_boe[i] = 0
                self.net_mcfe[i] = 0
                self.rev_gas[i] = 0
                self.rev_oil[i] = 0
                self.rev_ngl[i] = 0
                self.rev_total[i] = 0
                self.fixed_cost[i] = 0
                self.var_cost[i] = 0
                self.overhead[i] = 0
                self.sev_tax[i] = 0
                self.adval_tax[i] = 0
                self.exp_total[i] = 0
                self.ncf_pv0[i] = 0
                self.ccf_pv0[i] = 0
                self.ncf_pv10[i] = 0
                self.ccf_pv10[i] = 0
            self.EOL = self.t[life_ind]
        elif LOSS == "BFIT":
            # Truncate when cash flow is negative, including all expenses
            life_ind = 0
            detect = self.rev_total[0] - self.exp_total[0]
            while detect > 0 and life_ind < self.periods-1:
                life_ind+=1
                detect = self.rev_total[life_ind] - self.exp_total[life_ind]
            for i in range(life_ind,self.periods):
                self.gross_gas[i] = 0
                self.gross_oil[i] = 0
                self.gross_ngl[i] = 0
                self.gross_boe[i] = 0
                self.gross_mcfe[i] = 0
                self.net_gas[i] = 0
                self.net_oil[i] = 0
                self.net_ngl[i] = 0
                self.net_boe[i] = 0
                self.net_mcfe[i] = 0
                self.rev_gas[i] = 0
                self.rev_oil[i] = 0
                self.rev_ngl[i] = 0
                self.rev_total[i] = 0
                self.fixed_cost[i] = 0
                self.var_cost[i] = 0
                self.overhead[i] = 0
                self.sev_tax[i] = 0
                self.adval_tax[i] = 0
                self.exp_total[i] = 0
                self.ncf_pv0[i] = 0
                self.ccf_pv0[i] = 0
                self.ncf_pv10[i] = 0
                self.ccf_pv10[i] = 0
            self.EOL = self.t[life_ind]
        elif LOSS == "OK":
            # Allow loss - make no modifications to existing calculations
            self.EOL = max(self.t)
    def metrics(self):
        self.GROSS_CAPEX = np.sum(self.gross_capex)
        self.NET_CAPEX = np.sum(self.net_capex)
        self.NET_CAPEX_DISC = np.sum(self.net_capex_disc)
        self.PV0 = np.sum(self.ncf_pv0)
        self.PVR0 = self.PV0 / self.NET_CAPEX + 1
        self.PV10 = np.sum(self.ncf_pv10)
        self.PVR10 = self.PV10 / self.NET_CAPEX_DISC + 1
        self.NET_GAS_SALES = np.sum(self.net_gas)
    def make_run_table(self):
        self.col_titles = "Time (Days),Gross Gas (Mcf),Gross Oil (Bbl),Gross NGL (Bbl),Net Gas (Mcf),Net Oil (Mcf),Net NGL (Mcf),Base Gas Price ($/Mcf),Base Oil Price ($/Bbl),Realized Gas Price ($/Mcf),Realized Oil Price ($/Mcf,Realized NGL Price ($/Bbl),Gas Revenue ($),Oil Revenue ($),NGL Revenue ($),Total Net Revenue ($),Severance Tax ($),Ad Valorem Tax ($),Total Expenses ($),Net CAPEX ($),Net PV0 ($),Cum PV0 ($),Net PV10 ($),Cum PV10 ($)"
        table = np.column_stack((self.t,self.gross_gas,self.gross_oil,self.gross_ngl,self.net_gas,self.net_oil,self.net_ngl,
        self.gas_price_base,self.oil_price_base,self.gas_price_real,self.oil_price_real,self.ngl_price_real,self.rev_gas,
        self.rev_oil,self.rev_ngl,self.rev_total,self.sev_tax,self.adval_tax,self.exp_total,self.net_capex,self.ncf_pv0,
        self.ccf_pv0,self.ncf_pv10,self.ccf_pv10))

        return table