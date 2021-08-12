import numpy as np

class case:
    def __init__(self,dt,WI,NRI):
        self.dt = dt
        self.t = (np.linspace(1,np.size(dt)-1,np.size(dt)-1)-0.5)*30.4375
        self.periods = np.size(self.t)
        self.WI = WI
        self.NRI = NRI
    def decline(self,Decline_type,qi,Di_sec,Dterm_sec,b,peak):
        num_entry = np.size(self.dt)
        num_center = num_entry - 1
        self.q = np.zeros(num_entry)
        self.Qp = np.zeros(num_center)
        if Decline_type == 1 or Decline_type == 'Exponential':
            ##  1 - Exponential Decline
            Di = -np.log(1-Di_sec)                                                          # Initial decline rate      (Nominal /yr)
            self.q = qi * np.exp(-Di*self.dt * (1/365.25))                                  # Monthly starting rate     (Mcf/d)
            for i in range(num_center):
                self.Qp[i] = (self.q[i]-self.q[i+1]) / Di * 365.25                          # Monthly cumulative        (Mcf)
        elif Decline_type == 2 or Decline_type == 'Hyperbolic':
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
        elif Decline_type == 4 or Decline_type == 'Modified Arps':
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
        elif Decline_type == 5 or Decline_type == 'No Rate':
            pass
        elif Decline_type == 6 or Decline_type == 'CBM Dewatering/Incline':
            ##  6 - 2-Segment Exponential
            ##  Intended for use on Fruitland Coal wells with a dewatering period. "Peak" is the number of months to peak rate
            ##  and "Dterm" is simply the decline rate after peak rate is reached.
            Di = -np.log(1-Di_sec)                                                          # Initial decline rate      (Nominal /yr)
            Dterm = -np.log(1-Dterm_sec)
            qpeak = qi * np.exp(-Di*self.dt[peak] * (1/365.25))
            qi_hind = qpeak * np.exp(Dterm * self.dt[peak] * (1/365.25))
            for i in range(peak):
                self.q[i] = qi * np.exp(-Di*self.dt[i] * (1/365.25))                        # Monthly starting rate     (Mcf/d)
            for i in range(peak, num_center+1):
                self.q[i] = qi_hind * np.exp(-Dterm * self.dt[i] * (1/365.25))
            for i in range(peak):
                self.Qp[i] = (self.q[i]-self.q[i+1]) / Di * 365.25                          # Monthly cumulative        (Mcf)
            for i in range(peak, num_center):
                self.Qp[i] = (self.q[i]-self.q[i+1]) / Dterm * 365.25                          # Monthly cumulative        (Mcf)
    def production(self,oil_yield,ngl_yield,shrink):
        self.shrink = shrink
        self.oil_yield = oil_yield
        self.ngl_yield = ngl_yield
        self.gross_gas = self.Qp
        self.gross_gas_rate = self.Qp / 30.4375
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
        self.fixed_rate = fixed_cost
        self.var_gas_rate = var_gas_cost
        self.var_oil_rate = var_oil_cost
        self.overhead_rate = overhead
        self.adval_rate = adval_rate
        self.sev_rate = sev_rate
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
            self.net_capex_disc[i] = self.WI * capex[j] / (1+0.1)**((month[j]) / 12)
            j += 1
    def swansons_mean(self, p10, p50, p90, pfail, p_s):
        # Calculate production for a "mean" case (non-incremental)
        # Replaces production, pricing, revenue, expenses, and capex class methods
        # Production Section
        self.Qp = p_s * (0.3 * p10.gross_gas + 0.4 * p50.gross_gas + 0.3 * p90.gross_gas) + (1-p_s) * pfail.gross_gas
        self.q = p_s * (0.3 * p10.q + 0.4 * p50.q + 0.3 * p90.q) + (1-p_s) * pfail.q
        self.gross_gas = self.Qp
        self.gross_gas_rate = self.Qp / 30.4375
        self.gross_oil = p_s * (0.3 * p10.gross_oil + 0.4 * p50.gross_oil + 0.3 * p90.gross_oil) + (1-p_s) * pfail.gross_oil
        self.gross_ngl = p_s * (0.3 * p10.gross_ngl + 0.4 * p50.gross_ngl + 0.3 * p90.gross_ngl) + (1-p_s) * pfail.gross_ngl
        self.gross_boe = self.Qp / 6 + self.gross_oil + self.gross_ngl
        self.gross_mcfe = self.gross_boe * 6
        self.net_gas = p_s * (0.3 * p10.net_gas + 0.4 * p50.net_gas + 0.3 * p90.net_gas) + (1-p_s) * pfail.net_gas
        self.net_oil = p_s * (0.3 * p10.net_oil + 0.4 * p50.net_oil + 0.3 * p90.net_oil) + (1-p_s) * pfail.net_oil
        self.net_ngl = p_s * (0.3 * p10.net_ngl + 0.4 * p50.net_ngl + 0.3 * p90.net_ngl) + (1-p_s) * pfail.net_ngl
        self.net_boe = self.net_gas / 6 + self.net_oil + self.net_ngl
        self.net_mcfe = self.net_boe * 6
        self.shrink = np.sum(self.net_gas) / (np.sum(self.gross_gas) * self.NRI)

        # Pricing Section
        self.gas_price_base = p50.gas_price_base
        self.oil_price_base = p50.oil_price_base
        self.gas_price_real = p50.gas_price_real
        self.oil_price_real = p50.oil_price_real
        self.ngl_price_real = p50.ngl_price_real

        # Revenue Section
        self.rev_gas = self.net_gas * self.gas_price_real
        self.rev_oil = self.net_oil * self.oil_price_real
        self.rev_ngl = self.net_ngl * self.ngl_price_real
        self.rev_total = self.rev_gas + self.rev_oil + self.rev_ngl

        # Expenses Section
        self.fixed_cost = p_s * (0.3 * p10.fixed_cost + 0.4 * p50.fixed_cost + 0.3 * p90.fixed_cost) + (1-p_s) * pfail.fixed_cost
        # self.var_cost = (self.gross_gas * self.shrink * p50.var_gas_rate + self.gross_oil * p50.var_oil_rate) * self.WI
        self.var_cost = p_s * (0.3 * p10.var_cost + 0.4 * p50.var_cost + 0.3 * p90.var_cost) + (1-p_s) * pfail.var_cost
        self.overhead = p_s * (0.3 * p10.overhead + 0.4 * p50.overhead + 0.3 * p90.overhead) + (1-p_s) * pfail.overhead
        self.sev_tax = p50.sev_rate * self.rev_total
        self.adval_tax = p50.adval_rate * (self.rev_total - self.sev_tax)
        self.exp_total = self.fixed_cost + self.var_cost + self.overhead + self.adval_tax + self.sev_tax

        # Capex Section
        self.gross_capex = p_s * (0.3 * p10.gross_capex + 0.4 * p50.gross_capex + 0.3 * p90.gross_capex) + (1-p_s) * pfail.gross_capex
        self.net_capex = p_s * (0.3 * p10.net_capex + 0.4 * p50.net_capex + 0.3 * p90.net_capex) + (1-p_s) * pfail.net_capex
        self.net_capex_disc = np.zeros(self.periods)
        for i in range(self.periods):
            self.net_capex_disc[i] = self.net_capex[i] / (1+0.1)**((self.t[i] - 30.4375 / 2) / 365.25)
    def swansons_mean_inc(self, p10, p50, p90, pfail, pbase, p_s):
        # Calculate production for a "mean" case (incremental)
        # Replaces "production" and "expenses" class methods
        # Calculate production for a "mean" case (non-incremental)
        # Replaces production, pricing, revenue, expenses, and capex class methods
        # Production Section
        self.Qp = p_s * (0.3 * p10.gross_gas + 0.4 * p50.gross_gas + 0.3 * p90.gross_gas) + (1-p_s) * pfail.gross_gas - pbase.gross_gas
        self.q = p_s * (0.3 * p10.q + 0.4 * p50.q + 0.3 * p90.q) + (1-p_s) * pfail.q - pbase.q
        self.gross_gas = self.Qp
        self.gross_gas_rate = self.Qp / 30.4375
        self.gross_oil = p_s * (0.3 * p10.gross_oil + 0.4 * p50.gross_oil + 0.3 * p90.gross_oil) + (1-p_s) * pfail.gross_oil - pbase.gross_oil
        self.gross_ngl = p_s * (0.3 * p10.gross_ngl + 0.4 * p50.gross_ngl + 0.3 * p90.gross_ngl) + (1-p_s) * pfail.gross_ngl - pbase.gross_ngl
        self.gross_boe = self.Qp / 6 + self.gross_oil + self.gross_ngl
        self.gross_mcfe = self.gross_boe * 6
        self.net_gas = p_s * (0.3 * p10.net_gas + 0.4 * p50.net_gas + 0.3 * p90.net_gas) + (1-p_s) * pfail.net_gas - pbase.net_gas
        self.net_oil = p_s * (0.3 * p10.net_oil + 0.4 * p50.net_oil + 0.3 * p90.net_oil) + (1-p_s) * pfail.net_oil - pbase.net_oil
        self.net_ngl = p_s * (0.3 * p10.net_ngl + 0.4 * p50.net_ngl + 0.3 * p90.net_ngl) + (1-p_s) * pfail.net_ngl - pbase.net_ngl
        self.net_boe = self.net_gas / 6 + self.net_oil + self.net_ngl
        self.net_mcfe = self.net_boe * 6
        self.shrink = np.sum(self.net_gas) / (np.sum(self.gross_gas) * self.NRI)

        # Pricing Section
        self.gas_price_base = p50.gas_price_base
        self.oil_price_base = p50.oil_price_base
        self.gas_price_real = p50.gas_price_real
        self.oil_price_real = p50.oil_price_real
        self.ngl_price_real = p50.ngl_price_real

        # Revenue Section
        self.rev_gas = self.net_gas * self.gas_price_real
        self.rev_oil = self.net_oil * self.oil_price_real
        self.rev_ngl = self.net_ngl * self.ngl_price_real
        self.rev_total = self.rev_gas + self.rev_oil + self.rev_ngl

        # Expenses Section
        self.fixed_cost = p_s * (0.3 * p10.fixed_cost + 0.4 * p50.fixed_cost + 0.3 * p90.fixed_cost) + (1-p_s) * pfail.fixed_cost - pbase.fixed_cost
        # self.var_cost = (self.gross_gas * self.shrink * p50.var_gas_rate + self.gross_oil * p50.var_oil_rate) * self.WI
        self.var_cost = p_s * (0.3 * p10.var_cost + 0.4 * p50.var_cost + 0.3 * p90.var_cost) + (1-p_s) * pfail.var_cost - pbase.var_cost
        self.overhead = p_s * (0.3 * p10.overhead + 0.4 * p50.overhead + 0.3 * p90.overhead) + (1-p_s) * pfail.overhead - pbase.overhead
        self.sev_tax = p50.sev_rate * self.rev_total
        self.adval_tax = p50.adval_rate * (self.rev_total - self.sev_tax)
        self.exp_total = self.fixed_cost + self.var_cost + self.overhead + self.adval_tax + self.sev_tax

        # Capex Section
        self.gross_capex = p_s * (0.3 * p10.gross_capex + 0.4 * p50.gross_capex + 0.3 * p90.gross_capex) + (1-p_s) * pfail.gross_capex - pbase.gross_capex
        self.net_capex = p_s * (0.3 * p10.net_capex + 0.4 * p50.net_capex + 0.3 * p90.net_capex) + (1-p_s) * pfail.net_capex - pbase.net_capex
        self.net_capex_disc = np.zeros(self.periods)
        for i in range(self.periods):
            self.net_capex_disc[i] = self.net_capex[i] / (1+0.1)**((self.t[i] - 30.4375 / 2) / 365.25)
    def incrementalize(self, pbase):
        # Calculate production for a "mean" case (incremental)
        # Replaces "production" and "expenses" class methods
        # Calculate production for a "mean" case (non-incremental)
        # Replaces production, pricing, revenue, expenses, and capex class methods
        # Production Section
        self.Qp = self.Qp - pbase.gross_gas
        self.q = self.q - pbase.q
        self.gross_gas = self.Qp
        # self.gross_gas_rate = self.Qp / 30.4375
        self.gross_oil = self.gross_oil - pbase.gross_oil
        self.gross_ngl = self.gross_ngl - pbase.gross_ngl
        self.gross_boe = self.Qp / 6 + self.gross_oil + self.gross_ngl
        self.gross_mcfe = self.gross_boe * 6
        self.net_gas = self.net_gas - pbase.net_gas
        self.net_oil = self.net_oil - pbase.net_oil
        self.net_ngl = self.net_ngl - pbase.net_ngl
        self.net_boe = self.net_gas / 6 + self.net_oil + self.net_ngl
        self.net_mcfe = self.net_boe * 6

        # Revenue Section
        self.rev_gas = self.net_gas * self.gas_price_real
        self.rev_oil = self.net_oil * self.oil_price_real
        self.rev_ngl = self.net_ngl * self.ngl_price_real
        self.rev_total = self.rev_gas + self.rev_oil + self.rev_ngl

        # Expenses Section
        self.fixed_cost = self.fixed_cost - pbase.fixed_cost
        self.var_cost = self.var_cost - pbase.var_cost
        self.overhead = self.overhead - pbase.overhead
        self.sev_tax = self.sev_rate * self.rev_total
        self.adval_tax = self.adval_rate * (self.rev_total - self.sev_tax)
        self.exp_total = self.fixed_cost + self.var_cost + self.overhead + self.adval_tax + self.sev_tax

        # Capex Section
        self.gross_capex = self.gross_capex - pbase.gross_capex
        self.net_capex = self.net_capex - pbase.net_capex
        self.net_capex_disc = np.zeros(self.periods)
        for i in range(self.periods):
            self.net_capex_disc[i] = self.net_capex[i] / (1+0.1)**((self.t[i] - 30.4375 / 2) / 365.25)
        self.cash_flow()
        self.life(self.LOSS)
        self.metrics()
    def cash_flow(self):
        self.ncf_pv0 = self.rev_total - self.net_capex - self.exp_total
        self.ccf_pv0 = np.zeros(self.periods)
        self.ccf_pv0[0] = self.ncf_pv0[0]
        self.ncf_pv10 = (self.rev_total - self.exp_total) / (1+0.1)**((self.t - 30.4375/2) / 365.25) - self.net_capex_disc
        self.ccf_pv10 = np.zeros(self.periods)
        self.ccf_pv10[0] = self.ncf_pv10[0]
        self.payout = -999
        for i in range(1,self.periods):
            self.ccf_pv0[i] = self.ncf_pv0[i] + self.ccf_pv0[i-1]
            self.ccf_pv10[i] = self.ncf_pv10[i] + self.ccf_pv10[i-1]
            if self.ccf_pv0[i] > 0 and self.ccf_pv0[i-1] < 0:
                self.payout = (self.t[i] - 30.4375/2) / 30.4375
        if self.payout == -999:
            self.payout = "N/A"
        else:
            self.payout = int(self.payout)
    def life(self,LOSS):
        self.LOSS = LOSS
        non_ind = 0
        if LOSS == "NO":
            # Truncate when cash flow is negative, ignoring overhead
            life_ind = 0
            detect = self.rev_total[0] - self.fixed_cost[0] - self.var_cost[0] - self.sev_tax[0] - self.adval_tax[0]
            while detect > 0 and life_ind < self.periods-1:
                life_ind+=1
                detect = self.rev_total[life_ind] - self.fixed_cost[life_ind] - self.var_cost[life_ind] - self.sev_tax[life_ind] - self.adval_tax[life_ind]
            for i in range(life_ind,self.periods):
                self.gross_gas[i] = non_ind
                self.gross_gas_rate[i] = non_ind
                self.gross_oil[i] = non_ind
                self.gross_ngl[i] = non_ind
                self.gross_boe[i] = non_ind
                self.gross_mcfe[i] = non_ind
                self.net_gas[i] = non_ind
                self.net_oil[i] = non_ind
                self.net_ngl[i] = non_ind
                self.net_boe[i] = non_ind
                self.net_mcfe[i] = non_ind
                self.rev_gas[i] = non_ind
                self.rev_oil[i] = non_ind
                self.rev_ngl[i] = non_ind
                self.rev_total[i] = non_ind
                self.fixed_cost[i] = non_ind
                self.var_cost[i] = non_ind
                self.overhead[i] = non_ind
                self.sev_tax[i] = non_ind
                self.adval_tax[i] = non_ind
                self.exp_total[i] = non_ind
                self.ncf_pv0[i] = non_ind
                self.ccf_pv0[i] = non_ind
                self.ncf_pv10[i] = non_ind
                self.ccf_pv10[i] = non_ind
            self.EOL = self.t[life_ind]
        elif LOSS == "BFIT":
            # Truncate when cash flow is negative, including all expenses
            life_ind = 0
            detect = self.rev_total[0] - self.exp_total[0]
            while detect > 0 and life_ind < self.periods-1:
                life_ind+=1
                detect = self.rev_total[life_ind] - self.exp_total[life_ind]
            for i in range(life_ind,self.periods):
                self.gross_gas[i] = non_ind
                self.gross_gas_rate[i] = non_ind
                self.gross_oil[i] = non_ind
                self.gross_ngl[i] = non_ind
                self.gross_boe[i] = non_ind
                self.gross_mcfe[i] = non_ind
                self.net_gas[i] = non_ind
                self.net_oil[i] = non_ind
                self.net_ngl[i] = non_ind
                self.net_boe[i] = non_ind
                self.net_mcfe[i] = non_ind
                self.rev_gas[i] = non_ind
                self.rev_oil[i] = non_ind
                self.rev_ngl[i] = non_ind
                self.rev_total[i] = non_ind
                self.fixed_cost[i] = non_ind
                self.var_cost[i] = non_ind
                self.overhead[i] = non_ind
                self.sev_tax[i] = non_ind
                self.adval_tax[i] = non_ind
                self.exp_total[i] = non_ind
                self.ncf_pv0[i] = non_ind
                self.ccf_pv0[i] = non_ind
                self.ncf_pv10[i] = non_ind
                self.ccf_pv10[i] = non_ind
            self.EOL = self.t[life_ind]
        elif LOSS == "OK":
            # Allow loss - make no modifications to existing calculations
            self.EOL = max(self.t)
    def metrics(self):
        self.GROSS_CAPEX = int(round(np.sum(self.gross_capex) / 1000, 2))
        self.NET_CAPEX = int(round(np.sum(self.net_capex) / 1000, 2))
        self.NET_CAPEX_DISC = np.sum(self.net_capex_disc)
        self.PV0 = int(round(np.sum(self.ncf_pv0) / 1000, 2))
        self.PV10 = int(round(np.sum(self.ncf_pv10) / 1000, 2))
        self.NET_GAS_SALES = np.sum(self.net_gas)
        self.NET_MBOE = int(round(np.sum(self.net_boe) / 1000, 2))
        self.NET_MMCFE = int(round(np.sum(self.net_mcfe) / 1000, 2))
        self.NET_BOED = int(round(self.net_boe[0] / 30.4375, 2))
        self.NET_MCFED = int(round(self.net_mcfe[0] / 30.4375, 2))
        self.GROSS_GAS = round(np.sum(self.gross_gas) / 1000000, 2)
        if self.NET_CAPEX == 0 or self.GROSS_GAS == 0:
            self.PVR0 = 0
            self.PVR10 = 0
        else:
            self.PVR0 = self.PV0 / self.NET_CAPEX + 1
            self.PVR10 = np.sum(self.ncf_pv10) / self.NET_CAPEX_DISC + 1
    def make_run_table(self):
        self.col_titles = "Time (Days),Gross Gas (Mcf),Gross Oil (Bbl),Gross NGL (Bbl),Net Gas (Mcf),Net Oil (Mcf),Net NGL (Mcf),Base Gas Price ($/Mcf),Base Oil Price ($/Bbl),Realized Gas Price ($/Mcf),Realized Oil Price ($/Mcf,Realized NGL Price ($/Bbl),Gas Revenue ($),Oil Revenue ($),NGL Revenue ($),Total Net Revenue ($),Severance Tax ($),Ad Valorem Tax ($),Total Expenses ($),Net CAPEX ($),Net PV0 ($),Cum PV0 ($),Net PV10 ($),Cum PV10 ($)"
        table = np.column_stack((self.t,self.gross_gas,self.gross_oil,self.gross_ngl,self.net_gas,self.net_oil,self.net_ngl,
        self.gas_price_base,self.oil_price_base,self.gas_price_real,self.oil_price_real,self.ngl_price_real,self.rev_gas,
        self.rev_oil,self.rev_ngl,self.rev_total,self.sev_tax,self.adval_tax,self.exp_total,self.net_capex,self.ncf_pv0,
        self.ccf_pv0,self.ncf_pv10,self.ccf_pv10))

        return table