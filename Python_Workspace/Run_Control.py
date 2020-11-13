import numpy as np
import matplotlib.pyplot as plt
import Case as cases

Decline_type = 4                                                # 1 = Exponential, 2 = Hyperbolic, 3 = Harmonic, 4 = Modified Hyperbolic 
qi = 1000                                                       # Initial Rate              (Mcf/d)
Di_sec = 0.45                                                   # Decline Rate              (Secant-effective %/yr)
dt = np.linspace(0,600,601) * 30.4375                           # Time interval declaration (Days)

# For Hyperbolic (2) and Modified Hyperbolic Only (4)
b = 2                                                           # B-factor                  (Dimensionless)
# For Modified Hyperbolic Only (4)
Dterm_sec = 0.05                                                # Terminal decline rate     (Secant-effective %/yr)

# Ownership
WI = 1                                                          # Working interest          (Fraction)
NRI = 0.965                                                     # Net revenue interest      (Fraction)

# Shrinks & Yields
shrink = 0.85                                                   # Gas shrink factor         (mcf/mcf)
ngl_yield = 40                                                  # NGL yield                 (bbl/mmcf)
oil_yield = 10                                                  # Condensate yield          (bbl/mmcf)

# Basic LOS Parameters
fixed_cost = 1000                                               # Fixed field cost          (USD/month)
var_gas_cost = 0.9                                              # Variable field cost       (USD/mcfe/month)
var_oil_cost = var_gas_cost * 6                                 # Variable ield cost        (USD/boe/month)
overhead = 0                                                    # Overhead expense          (USD/month)
adval_rate = 0.0605                                             # Ad Valorem Tax Rate       (%)
sev_rate = 0.0582                                               # Severance Tax Rate        (%)

# CAPEX Scheduling
capex_months = [0]                                              # CAPEX timing              (Months)
capex_amts = [1e5]                                              # CAPEX amount              (USD)

# Economic Life Calc Mode
# Same as Aries: NO, BFIT, or OK
LOSS = "NO"

# Generate case object, run economic calculations
doodad = cases.case(dt,WI,NRI)
doodad.decline(Decline_type, qi, Di_sec, Dterm_sec, b)
doodad.production(oil_yield,ngl_yield,shrink)
doodad.pricing("flat",2,30,-0.3,-2,0.32)
doodad.revenue()
doodad.expenses(fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate)
doodad.capex(capex_months,capex_amts)
doodad.cash_flow()
doodad.life(LOSS)
doodad.metrics()

# Run Results, CSV Output
print("End of life at "+str(round(doodad.EOL/30.4375/12,2))+" years (LOSS "+str(LOSS)+")")
print("PVR10 = "+str(round(doodad.PVR10,2))+", PV10 = $"+str(round(doodad.PV10,0)))
print("PVR0 = "+str(round(doodad.PVR0,2))+", PV0 = $"+str(round(doodad.PV0,0)))
print("Net Gas Sales = "+str(round(doodad.NET_GAS_SALES/1000,0)))
np.savetxt("data.csv",doodad.make_run_table(),delimiter=",",header=doodad.col_titles)