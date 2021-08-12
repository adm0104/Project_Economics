import numpy as np
import matplotlib.pyplot as plt
import case as case
import Toolbox as tb

# This script generates a range of potential outcomes for a natural gas
# rate add or workover project, as defined by the user. It then aggregates
# those outcomes into a "mean" case, and integrates a chance of success
# to deliver a "risked mean" output to aid in decision making.

months = 600
dt = np.linspace(0,months,months+1) * 30.4375
incremental = True                                              # Boolean - should this be an incremental run?

# Ownership
WI = 1                                                          # Working interest          (Fraction)
NRI = 0.86                                                      # Net revenue interest      (Fraction)

# Shrinks & Yields
shrink = 0.83                                                   # Gas shrink factor         (mcf/mcf)
ngl_yield = 63                                                  # NGL yield                 (bbl/mmcf)
oil_yield = 10                                                  # Condensate yield          (bbl/mmcf)

# Basic LOS Parameters
fixed_cost = 0                                                  # Fixed field cost          (USD/month)
var_gas_cost = 0.2176 + 0.4154                                  # Variable field cost       (USD/mcfe/month)
var_oil_cost = var_gas_cost * 6                                 # Variable field cost       (USD/boe/month)
overhead = 0                                                    # Overhead expense          (USD/month)
adval_rate = 0.0157                                             # Ad Valorem Tax Rate       (%)
sev_rate = 0.0623                                               # Severance Tax Rate        (%)

# CAPEX Scheduling
capex_months = [0]                                              # CAPEX timing              (Months)
capex_amts = [215000]                                           # CAPEX amount              (USD)

# Failure CAPEX Scheduling
fail_capex_months = [0]                                         # CAPEX timing              (Months)
fail_capex_amts = [215000]                                      # CAPEX amount              (USD)

# Pricing
pricing_type = "flat"
gas_price = 2.50
oil_price = 45
gas_diff = -0.1
oil_diff = -10.7
ngl_diff = 0.39

# Economic Life Calc Mode
# Same as Aries: NO, BFIT, or OK
LOSS = "BFIT"

# Probability of success
# As a fraction
p_s = 0.9

# Initialize Outcome Objects
p10 = case.case(dt, WI, NRI)
p50 = case.case(dt, WI, NRI)
p90 = case.case(dt, WI, NRI)
pfail = case.case(dt, WI, NRI)
pmean = case.case(dt, WI, NRI)
if incremental:
    pbase = case.case(dt, WI, NRI)

# Base Case Decline Parameters
# 1 = Exponential, 2 = Hyperbolic, 3 = Harmonic, 4 = Modified Hyperbolic
if incremental:
    pbase.Decline_type = 1
    pbase.qi = 50
    pbase.Di_sec = 0.05
    pbase.b = -999.25
    pbase.Dterm_sec = -999.25
    pbase.peak = -999.25


# P10 Decline Parameters
# 1 = Exponential, 2 = Hyperbolic, 3 = Harmonic, 4 = Modified Hyperbolic , 5 = NULL, 6 = peak rate (coal dewatering)
p10.Decline_type = 4                                               
p10.qi = 190
p10.Di_sec = 0.58
p10.b = 2.6
p10.Dterm_sec = 0.08
p10.peak = -999.25

# P50 Decline Parameters
# 1 = Exponential, 2 = Hyperbolic, 3 = Harmonic, 4 = Modified Hyperbolic , 5 = NULL, 6 = peak rate (coal dewatering)
p50.Decline_type = 4
p50.qi = 150
p50.Di_sec = 0.58
p50.b = 2.6
p50.Dterm_sec = 0.08
p50.peak = -999.25

# P90 Decline Parameters
# 1 = Exponential, 2 = Hyperbolic, 3 = Harmonic, 4 = Modified Hyperbolic , 5 = NULL, 6 = peak rate (coal dewatering)
p90.Decline_type = 4
p90.qi = 120
p90.Di_sec = 0.58
p90.b = 2.6
p90.Dterm_sec = 0.08
p90.peak = -999.25

# Failure Decline Parameters
# 1 = Exponential, 2 = Hyperbolic, 3 = Harmonic, 4 = Modified Hyperbolic , 5 = no rate at all
pfail.Decline_type = 5
pfail.qi = -999.25
pfail.Di_sec = -999.25
pfail.b = -999.25
pfail.Dterm_sec = -999.25
pfail.peak = -999.25

# Populate Object Properties
if incremental:
    pbase.decline(pbase.Decline_type, pbase.qi, pbase.Di_sec, pbase.Dterm_sec, pbase.b, pbase.peak)
    pbase.production(oil_yield,ngl_yield,shrink)
    pbase.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
    pbase.revenue()
    pbase.expenses(fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate)
    pbase.capex([0],[0])
    pbase.cash_flow()
    pbase.life(LOSS)
    pbase.metrics()
    print("Base Case Complete")

p10.decline(p10.Decline_type, p10.qi, p10.Di_sec, p10.Dterm_sec, p10.b, p10.peak)
p10.production(oil_yield,ngl_yield,shrink)
p10.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
p10.revenue()
p10.expenses(fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate)
p10.capex(capex_months,capex_amts)
p10.cash_flow()
p10.life(LOSS)
p10.metrics()
print("P10 Complete")

p50.decline(p50.Decline_type, p50.qi, p50.Di_sec, p50.Dterm_sec, p50.b, p50.peak)
p50.production(oil_yield,ngl_yield,shrink)
p50.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
p50.revenue()
p50.expenses(fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate)
p50.capex(capex_months,capex_amts)
p50.cash_flow()
p50.life(LOSS)
p50.metrics()
print("P50 Complete")

p90.decline(p90.Decline_type, p90.qi, p90.Di_sec, p90.Dterm_sec, p90.b, p90.peak)
p90.production(oil_yield,ngl_yield,shrink)
p90.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
p90.revenue()
p90.expenses(fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate)
p90.capex(capex_months,capex_amts)
p90.cash_flow()
p90.life(LOSS)
p90.metrics()
print("P90 Complete")

pfail.decline(pfail.Decline_type, pfail.qi, pfail.Di_sec, pfail.Dterm_sec, pfail.b, pfail.peak)
pfail.production(oil_yield,ngl_yield,shrink)
pfail.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
pfail.revenue()
pfail.expenses(fixed_cost,var_gas_cost,var_oil_cost,overhead,adval_rate,sev_rate)
pfail.capex(fail_capex_months,fail_capex_amts)
pfail.cash_flow()
pfail.life(LOSS)
pfail.metrics()
print("Pfail Complete")

if incremental:
    pmean.swansons_mean_inc(p10, p50, p90, pfail, pbase, p_s)
    pmean.cash_flow()
    pmean.life(LOSS)
    pmean.metrics()
    print("Pmean Complete")
    p10.incrementalize(pbase)
    p50.incrementalize(pbase)
    p90.incrementalize(pbase)
    # pfail.incrementalize(pbase)
else:
    pmean.swansons_mean(p10, p50, p90, pfail, p_s)
    pmean.cash_flow()
    pmean.life(LOSS)
    pmean.metrics()
    print("Pmean Complete")


# Run Results, CSV Output
# print("End of life at "+str(round(pmean.EOL/30.4375/12,2))+" years (LOSS "+str(LOSS)+")")
print("PVR10 = "+str(round(pmean.PVR10,2))+", PV10 = $"+str(round(pmean.PV10,0)))
print("PVR0 = "+str(round(pmean.PVR0,2))+", PV0 = $"+str(round(pmean.PV0,0)))
print("Net Gas Sales = "+str(round(pmean.NET_GAS_SALES/1000,0)))
np.savetxt("data.csv",pmean.make_run_table(),delimiter=",",header=pmean.col_titles)

# Generate Run Results Slide
# Populate Output Table
plt.figure(figsize = (15, 7))
grid = plt.GridSpec(2, 8)
plt.subplot(grid[0:,:2])
ax = plt.gca()
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
plt.box(on = None)
if incremental:
    x = pbase.GROSS_GAS
    table_values = [[pmean.GROSS_GAS, p10.GROSS_GAS, p50.GROSS_GAS, p90.GROSS_GAS, pfail.GROSS_GAS, pbase.GROSS_GAS],
    [round(pmean.GROSS_GAS+x,2), round(p10.GROSS_GAS+x,2), round(p50.GROSS_GAS+x,2), round(p90.GROSS_GAS+x,2), pfail.GROSS_GAS, pbase.GROSS_GAS],
    [pmean.GROSS_CAPEX, p10.GROSS_CAPEX, p50.GROSS_CAPEX, p90.GROSS_CAPEX, pfail.GROSS_CAPEX, pbase.GROSS_CAPEX],
    [pmean.NET_CAPEX, p10.NET_CAPEX, p50.NET_CAPEX, p90.NET_CAPEX, pfail.NET_CAPEX, pbase.NET_CAPEX],
    [pmean.NET_MBOE, p10.NET_MBOE, p50.NET_MBOE, p90.NET_MBOE, pfail.NET_MBOE, pbase.NET_MBOE],
    [pmean.NET_MMCFE, p10.NET_MMCFE, p50.NET_MMCFE, p90.NET_MMCFE, pfail.NET_MMCFE, pbase.NET_MMCFE],
    [pmean.NET_BOED, p10.NET_BOED, p50.NET_BOED, p90.NET_BOED, pfail.NET_BOED, pbase.NET_BOED],
    [pmean.NET_MCFED, p10.NET_MCFED, p50.NET_MCFED, p90.NET_MCFED, pfail.NET_MCFED, pbase.NET_MCFED],
    [pmean.PV10, p10.PV10, p50.PV10, p90.PV10, pfail.PV10, pbase.PV10],
    [pmean.payout, p10.payout, p50.payout, p90.payout, pfail.payout, pbase.payout],
    [round(pmean.PVR10,2), round(p10.PVR10,2), round(p50.PVR10,2), round(p90.PVR10,2), round(pfail.PVR10,2), round(pbase.PVR10,2)]]
    cols = ["Mean", "P10", "P50", "P90", "Fail", "Base"]
    rows = ["Incremental EUR (Bcf)", "Total Gas EUR (Bcf)", "Gross CAPEX ($M)", "Net CAPEX ($M)", "Net Res. (Mboe)", "Net Res. (Mmcfe)", "Net IP30 (Boe/d)", "Net IP30 (Mcfe/d)", "PV-10 ($M)", "Payout (Months)", "PVR-10"]

else:
    table_values = [[pmean.GROSS_GAS, p10.GROSS_GAS, p50.GROSS_GAS, p90.GROSS_GAS, pfail.GROSS_GAS],
    [pmean.GROSS_CAPEX, p10.GROSS_CAPEX, p50.GROSS_CAPEX, p90.GROSS_CAPEX, p10.GROSS_CAPEX],
    [pmean.NET_CAPEX, p10.NET_CAPEX, p50.NET_CAPEX, p90.NET_CAPEX, p10.NET_CAPEX],
    [pmean.NET_MBOE, p10.NET_MBOE, p50.NET_MBOE, p90.NET_MBOE, pfail.NET_MBOE],
    [pmean.NET_MMCFE, p10.NET_MMCFE, p50.NET_MMCFE, p90.NET_MMCFE, pfail.NET_MMCFE],
    [pmean.NET_BOED, p10.NET_BOED, p50.NET_BOED, p90.NET_BOED, pfail.NET_BOED],
    [pmean.NET_MCFED, p10.NET_MCFED, p50.NET_MCFED, p90.NET_MCFED, pfail.NET_MCFED],
    [pmean.PV10, p10.PV10, p50.PV10, p90.PV10, pfail.PV10],
    [pmean.payout, p10.payout, p50.payout, p90.payout, pfail.payout],
    [round(pmean.PVR10,2), round(p10.PVR10,2), round(p50.PVR10,2), round(p90.PVR10,2), round(pfail.PVR10,2)]]
    cols = ["Mean", "P10", "P50", "P90", "Fail"]
    rows = ["Gross Gas EUR (Bcf)", "Gross CAPEX ($M)", "Net CAPEX ($M)", "Net Res. (Mboe)", "Net Res. (Mmcfe)", "Net IP30 (Boe/d)", "Net IP30 (Mcfe/d)", "PV-10 ($M)", "Payout (Months)", "PVR-10"]

rcolors = plt.cm.BuGn(np.full(len(rows), 0.6))
ccolors = plt.cm.BuGn(np.full(len(cols), 0.6))

metrics_table = plt.table(cellText = table_values, rowLabels = rows, colLabels = cols, rowLoc='right', loc='center', rowColours=rcolors, colColours=ccolors)
metrics_table.scale(1, 1.5)

# Plot Decline Curves
decline_plot = plt.subplot(grid[0,3:])
P10, = plt.semilogy(p10.t / 30.4375, p10.gross_gas_rate, lw=1.8, color='green')
P50, = plt.semilogy(p50.t / 30.4375, p50.gross_gas_rate, lw=1.8, color='blue')
P90, = plt.semilogy(p90.t / 30.4375, p90.gross_gas_rate, lw=1.8, color='orange')
Failure, = plt.semilogy(pfail.t / 30.4375, pfail.gross_gas_rate, lw=1.5, color='crimson', linestyle='--')
if incremental:
    Base, = plt.semilogy(pbase.t / 30.4375, pbase.gross_gas_rate, lw=1.5, color='black', linestyle='--')
    Pmean, = plt.semilogy(pmean.t / 30.4375, pmean.gross_gas_rate, lw=2.2, color='red')
    plt.legend([Pmean, Base, Failure, P10, P50, P90], ['Pmean', 'Base', 'Failure', 'P10', 'P50', 'P90'])
else: 
    Pmean, = plt.semilogy(pmean.t / 30.4375, pmean.gross_gas_rate, lw=2.2, color='r')
    plt.legend([Pmean, Failure, P10, P50, P90], ['Pmean', 'Failure', 'P10', 'P50', 'P90'])
plt.grid(which='both', axis='both', lw=1, color='w')
plt.axis([0, p10.EOL / 30.4375, 10, tb.roundup_log(max(p10.gross_gas_rate))])
plt.xlabel('Time (Months)')
plt.ylabel('Gas Rate (Mcf/d)')
decline_plot.set_facecolor('xkcd:light grey')

# Plot Cumulative Cash Flow
ccf_plot = plt.subplot(grid[1,3:])
PV0, = plt.plot(pmean.t / 30.4375, pmean.ccf_pv0 / 1000, lw=2.2, color='red')
PV10, = plt.plot(pmean.t / 30.4375, pmean.ccf_pv10 / 1000, lw=2.2, color='blue')
plt.plot([0, pmean.payout],[-pmean.NET_CAPEX, 0], 'ro')
plt.legend([PV0, PV10], ['Undiscounted', 'Discounted (10%)'])
plt.grid(which='both', axis='both', lw=1, color='w')
plt.axis([0, p10.EOL / 30.4375, -1*tb.roundup_lin(abs(min(pmean.ccf_pv0 / 1000))), tb.roundup_lin(max(pmean.ccf_pv0 / 1000))])
plt.xlabel('Time (Months)')
plt.ylabel('Cumulative Cash Flow ($M)')
ccf_plot.set_facecolor('xkcd:light grey')

# Show
plt.savefig('run.png', bbox_inches='tight')
plt.show()