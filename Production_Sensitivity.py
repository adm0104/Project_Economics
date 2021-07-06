import numpy as np
import matplotlib.pyplot as plt
import case as case

# This script generates a range of potential outcomes for a natural gas
# rate add or workover project, as defined by the user. It then aggregates
# those outcomes into a "mean" case, and integrates a chance of success
# to deliver a "risked mean" output to aid in decision making.
# This script does not perform incremental calculations.

dt = np.linspace(0,600,601) * 30.4375

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

# Pricing
pricing_type = "flat"
gas_price = 2
oil_price = 30
gas_diff = -0.3
oil_diff = -2
ngl_diff = 0.32

# Economic Life Calc Mode
# Same as Aries: NO, BFIT, or OK
LOSS = "NO"

# Probability of success
# As a fraction
p_s = 0.5

# Initialize Outcome Objects
p10 = case.case(dt, WI, NRI)
p50 = case.case(dt, WI, NRI)
p90 = case.case(dt, WI, NRI)
pfail = case.case(dt, WI, NRI)
pmean = case.case(dt, WI, NRI)

# P10 Decline Parameters
# 1 = Exponential, 2 = Hyperbolic, 3 = Harmonic, 4 = Modified Hyperbolic 
p10.Decline_type = 4                                                
p10.qi = 1000
p10.Di_sec = 0.45
p10.b = 2
p10.Dterm_sec = 0.05

# P50 Decline Parameters
# 1 = Exponential, 2 = Hyperbolic, 3 = Harmonic, 4 = Modified Hyperbolic 
p50.Decline_type = 4
p50.qi = 400
p50.Di_sec = 0.45
p50.b = 2
p50.Dterm_sec = 0.05

# P90 Decline Parameters
# 1 = Exponential, 2 = Hyperbolic, 3 = Harmonic, 4 = Modified Hyperbolic 
p90.Decline_type = 4
p90.qi = 300
p90.Di_sec = 0.45
p90.b = 2
p90.Dterm_sec = 0.05

# Failure Decline Parameters
# 1 = Exponential, 2 = Hyperbolic, 3 = Harmonic, 4 = Modified Hyperbolic 
pfail.Decline_type = 4
pfail.qi = 100
pfail.Di_sec = 0.45
pfail.b = 2
pfail.Dterm_sec = 0.05

# Populate Object Properties
p10.decline(p10.Decline_type, p10.qi, p10.Di_sec, p10.Dterm_sec, p10.b)
p10.production(oil_yield,ngl_yield,shrink)
p10.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
p10.revenue()
p10.expenses(fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate)
p10.capex(capex_months,capex_amts)
p10.cash_flow()
p10.life(LOSS)
p10.metrics()

p50.decline(p50.Decline_type, p50.qi, p50.Di_sec, p50.Dterm_sec, p50.b)
p50.production(oil_yield,ngl_yield,shrink)
p50.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
p50.revenue()
p50.expenses(fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate)
p50.capex(capex_months,capex_amts)
p50.cash_flow()
p50.life(LOSS)
p50.metrics()

p90.decline(p90.Decline_type, p90.qi, p90.Di_sec, p90.Dterm_sec, p90.b)
p90.production(oil_yield,ngl_yield,shrink)
p90.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
p90.revenue()
p90.expenses(fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate)
p90.capex(capex_months,capex_amts)
p90.cash_flow()
p90.life(LOSS)
p90.metrics()

pfail.decline(pfail.Decline_type, pfail.qi, pfail.Di_sec, pfail.Dterm_sec, pfail.b)
pfail.production(oil_yield,ngl_yield,shrink)
pfail.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
pfail.revenue()
pfail.expenses(fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate)
pfail.capex(capex_months,capex_amts)
pfail.cash_flow()
pfail.life(LOSS)
pfail.metrics()

pmean.Qp = p_s * (0.3 * p10.gross_gas + 0.4 * p50.gross_gas + 0.3 * p90.gross_gas) + (1-p_s) * pfail.Qp
pmean.q = p_s * (0.3 * p10.q + 0.4 * p50.q + 0.3 * p90.q) + (1-p_s) * pfail.q
pmean.production(oil_yield,ngl_yield, shrink)
pmean.pricing(pricing_type, gas_price,oil_price, gas_diff, oil_diff, ngl_diff)
pmean.revenue()
pmean.expenses(fixed_cost, var_gas_cost, var_oil_cost, overhead, adval_rate, sev_rate)
pmean.capex(capex_months, capex_amts)
pmean.cash_flow()
pmean.life(LOSS)
pmean.metrics()

# Run Results, CSV Output
print("End of life at "+str(round(pmean.EOL/30.4375/12,2))+" years (LOSS "+str(LOSS)+")")
print("PVR10 = "+str(round(pmean.PVR10,2))+", PV10 = $"+str(round(pmean.PV10,0)))
print("PVR0 = "+str(round(pmean.PVR0,2))+", PV0 = $"+str(round(pmean.PV0,0)))
print("Net Gas Sales = "+str(round(pmean.NET_GAS_SALES/1000,0)))
# np.savetxt("data.csv",pmean.make_run_table(),delimiter=",",header=pmean.col_titles)

# Generate Run Results Slide
plt.figure(figsize = (20,10))
ax1 = plt.subplot()
plt.semilogy(p10.t, p10.gross_gas_rate)
plt.semilogy(p50.t, p50.gross_gas_rate)
plt.semilogy(p90.t, p90.gross_gas_rate)
plt.semilogy(pfail.t, pfail.gross_gas_rate)
plt.semilogy(pmean.t, pmean.gross_gas_rate)
plt.grid(which='both', axis='both')
plt.show()