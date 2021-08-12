import numpy as np
import matplotlib.pyplot as plt
import case as case

def run_econs(pars, runSettingsFrame):
    dt = np.linspace(0, int(runSettingsFrame.settings.months), int(runSettingsFrame.settings.months) + 1) * 30.4375

    # Pricing
    pricing_type = "flat"
    gas_price = 2.50
    oil_price = 45
    gas_diff = -0.1
    oil_diff = -10.7
    ngl_diff = 0.39

    # CAPEX Scheduling
    capex_months = [0]                                              # CAPEX timing              (Months)
    capex_amts = [200000]                                           # CAPEX amount              (USD)

    # Failure CAPEX Scheduling
    fail_capex_months = [0]                                         # CAPEX timing              (Months)
    fail_capex_amts = [200000]                                      # CAPEX amount              (USD)

    if runSettingsFrame.settings.incremental:
        pbase = case.case(dt, runSettingsFrame.settings.WI, runSettingsFrame.settings.NRI)
        pbase.decline(pars.pbase.Decline_type, pars.pbase.qi, pars.pbase.Di_sec,
        pars.pbase.Dterm_sec, pars.pbase.b, pars.pbase.peak)
        pbase.production(pars.pbase.oil_yield, pars.pbase.ngl_yield, pars.pbase.shrink)
        pbase.pricing(pricing_type, gas_price,oil_price, gas_diff, oil_diff, ngl_diff)
        pbase.revenue()
        pbase.expenses(pars.pbase.fixed_cost, pars.pbase.var_gas_cost, pars.pbase.var_oil_cost,
        pars.pbase.overhead, runSettingsFrame.settings.adval_rate, runSettingsFrame.settings.sev_rate)
        pbase.capex([0],[0])
        pbase.cash_flow()
        pbase.life(runSettingsFrame.settings.LOSS)
        pbase.metrics()
        print("Base Case Complete")

    p10 = case.case(dt, runSettingsFrame.settings.WI, runSettingsFrame.settings.NRI)
    p10.decline(pars.p10.Decline_type, pars.p10.qi, pars.p10.Di_sec,
    pars.p10.Dterm_sec, pars.p10.b, pars.p10.peak)
    p10.production(pars.p10.oil_yield, pars.p10.ngl_yield, pars.p10.shrink)
    p10.pricing(pricing_type, gas_price, oil_price, gas_diff, oil_diff, ngl_diff)
    p10.revenue()
    p10.expenses(pars.p10.fixed_cost, pars.p10.var_gas_cost, pars.p10.var_oil_cost, 
    pars.p10.overhead, runSettingsFrame.settings.adval_rate, runSettingsFrame.settings.sev_rate)
    p10.capex(capex_months,capex_amts)
    p10.cash_flow()
    p10.life(runSettingsFrame.settings.LOSS)
    p10.metrics()
    print("P10 Complete")

    p50 = case.case(dt, runSettingsFrame.settings.WI, runSettingsFrame.settings.NRI)
    p50.decline(pars.p50.Decline_type, pars.p50.qi, pars.p50.Di_sec,
    pars.p50.Dterm_sec, pars.p50.b, pars.p50.peak)
    p50.production(pars.p50.oil_yield, pars.p50.ngl_yield, pars.p50.shrink)
    p50.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
    p50.revenue()
    p50.expenses(pars.p50.fixed_cost, pars.p50.var_gas_cost, pars.p50.var_oil_cost,
    pars.p50.overhead, runSettingsFrame.settings.adval_rate, runSettingsFrame.settings.sev_rate)
    p50.capex(capex_months,capex_amts)
    p50.cash_flow()
    p50.life(runSettingsFrame.settings.LOSS)
    p50.metrics()
    print("P50 Complete")

    p90 = case.case(dt, runSettingsFrame.settings.WI, runSettingsFrame.settings.NRI)
    p90.decline(pars.p90.Decline_type, pars.p90.qi, pars.p90.Di_sec,
    pars.p90.Dterm_sec, pars.p90.b, pars.p90.peak)
    p90.production(pars.p90.oil_yield, pars.p90.ngl_yield, pars.p90.shrink)
    p90.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
    p90.revenue()
    p90.expenses(pars.p90.fixed_cost, pars.p90.var_gas_cost, pars.p90.var_oil_cost,
    pars.p90.overhead, runSettingsFrame.settings.adval_rate, runSettingsFrame.settings.sev_rate)
    p90.capex(capex_months,capex_amts)
    p90.cash_flow()
    p90.life(runSettingsFrame.settings.LOSS)
    p90.metrics()
    print("P90 Complete")

    pfail = case.case(dt, runSettingsFrame.settings.WI, runSettingsFrame.settings.NRI)
    pfail.decline(pars.pfail.Decline_type, pars.pfail.qi, pars.pfail.Di_sec,
    pars.pfail.Dterm_sec, pars.pfail.b, pars.pfail.peak)
    pfail.production(pars.pfail.oil_yield, pars.pfail.ngl_yield, pars.pfail.shrink)
    pfail.pricing(pricing_type,gas_price,oil_price,gas_diff,oil_diff,ngl_diff)
    pfail.revenue()
    pfail.expenses(pars.pfail.fixed_cost, pars.pfail.var_gas_cost, pars.pfail.var_oil_cost,
    pars.pfail.overhead, runSettingsFrame.settings.adval_rate, runSettingsFrame.settings.sev_rate)
    pfail.capex(fail_capex_months,fail_capex_amts)
    pfail.cash_flow()
    pfail.life(runSettingsFrame.settings.LOSS)
    pfail.metrics()
    print("Pfail Complete")

    pmean = case.case(dt, runSettingsFrame.settings.WI, runSettingsFrame.settings.NRI)
    if runSettingsFrame.settings.incremental:
        pmean.swansons_mean_inc(p10, p50, p90, pfail, pbase, runSettingsFrame.settings.p_s)
        pmean.cash_flow()
        pmean.life(runSettingsFrame.settings.LOSS)
        pmean.metrics()
        print("Pmean Complete")
        p10.incrementalize(pbase)
        p50.incrementalize(pbase)
        p90.incrementalize(pbase)
        # pfail.incrementalize(pbase)
    else:
        pmean.swansons_mean(p10, p50, p90, pfail, runSettingsFrame.settings.p_s)
        pmean.cash_flow()
        pmean.life(runSettingsFrame.settings.LOSS)
        pmean.metrics()
        print("Pmean Complete")

    if runSettingsFrame.settings.incremental:
        return pmean, p10, p50, p90, pfail, pbase
    else:
        return pmean, p10, p50, p90, pfail, None

"""
# Run Results, CSV Output
# print("End of life at "+str(round(pmean.EOL/30.4375/12,2))+" years (LOSS "+str(LOSS)+")")
#print("PVR10 = "+str(round(pmean.PVR10,2))+", PV10 = $"+str(round(pmean.PV10,0)))
#print("PVR0 = "+str(round(pmean.PVR0,2))+", PV0 = $"+str(round(pmean.PV0,0)))
#print("Net Gas Sales = "+str(round(pmean.NET_GAS_SALES/1000,0)))
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
if pars.p50.incremental:
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
if pars.p50.incremental:
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
"""