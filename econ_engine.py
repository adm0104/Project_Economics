import numpy as np
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
    capex_months = [0]                                                              # CAPEX timing              (Months)
    capex_amts = [pars['p50']['capex']]                                             # CAPEX amount              (USD)

    # Failure CAPEX Scheduling
    fail_capex_months = [0]                                                         # CAPEX timing              (Months)
    fail_capex_amts = [pars['p50']['capex']]                                        # CAPEX amount              (USD)

    if runSettingsFrame.settings.incremental == 'Incremental':
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
    if runSettingsFrame.settings.incremental == 'Incremental':
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

    if runSettingsFrame.settings.incremental == 'Incremental':
        return pmean, p10, p50, p90, pfail, pbase
    else:
        return pmean, p10, p50, p90, pfail, None