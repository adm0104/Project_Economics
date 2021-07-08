import numpy as np
import matplotlib.pyplot as plt
import case as cases

Decline_type = 4                                                # 1 = Exponential, 2 = Hyperbolic, 3 = Harmonic, 4 = Modified Hyperbolic 
qi = 242                                                       # Initial Rate              (Mcf/d)
Di_sec = 0.65                                                   # Decline Rate              (Secant-effective %/yr)
dt = np.linspace(0,600,601) * 30.4375                           # Time interval declaration (Days)

# For Hyperbolic (2) and Modified Hyperbolic Only (4)
b = 1.5                                                           # B-factor                  (Dimensionless)
# For Modified Hyperbolic Only (4)
Dterm_sec = 0.05                                                # Terminal decline rate     (Secant-effective %/yr)

# Ownership
WI = 1                                                          # Working interest          (Fraction)
NRI = 0.965                                                     # Net revenue interest      (Fraction)

# Shrinks & Yields
shrink = 0.939                                                  # Gas shrink factor         (mcf/mcf)
ngl_yield = 31.17                                               # NGL yield                 (bbl/mmcf)
oil_yield = 1                                                   # Condensate yield          (bbl/mmcf)

# Basic LOS Parameters
fixed_cost = 1085                                               # Fixed field cost          (USD/month)
var_gas_cost = 0.95                                             # Variable field cost       (USD/mcfe/month)
var_oil_cost = var_gas_cost * 6                                 # Variable ield cost        (USD/boe/month)
overhead = 692                                                  # Overhead expense          (USD/month)
adval_rate = 0.0547                                             # Ad Valorem Tax Rate       (%)
sev_rate = 0.0476                                               # Severance Tax Rate        (%)

# CAPEX Scheduling
capex_months = [0]                                              # CAPEX timing              (Months)
capex_amts = [8e4]                                              # CAPEX amount              (USD)

# Economic Life Calc Mode
# Same as Aries: NO, BFIT, or OK
LOSS = "NO"

# Generate case object, run economic calculations
run_case = cases.case(dt,WI,NRI)
run_case.decline(Decline_type, qi, Di_sec, Dterm_sec, b, -999.25)
run_case.production(oil_yield,ngl_yield,shrink)
run_case.pricing("flat",2.27,45,0.27,-3.14,0.4)
run_case.revenue()
run_case.expenses(fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate)
run_case.capex(capex_months,capex_amts)
run_case.cash_flow()
run_case.life(LOSS)
run_case.metrics()

# Run Results, CSV Output
print("End of life at "+str(round(run_case.EOL/30.4375/12,2))+" years (LOSS "+str(LOSS)+")")
print("PVR10 = "+str(round(run_case.PVR10,2))+", PV10 = $"+str(round(run_case.PV10,0)))
print("PVR0 = "+str(round(run_case.PVR0,2))+", PV0 = $"+str(round(run_case.PV0,0)))
print("Net Gas Sales = "+str(round(run_case.NET_GAS_SALES/1000,0)))