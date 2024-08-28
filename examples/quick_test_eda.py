from pytank.tank import Tank
from pytank.analysis import Analysis
from quick_test_tank import wells_info, oil_model, water_model

# Quicktest
tank_name = "tank_center"

tank1 = Tank(
    name=tank_name,
    wells=wells_info,
    oil_model=oil_model,
    water_model=water_model,
    pi=3700,
    swo=0.15,
    cw=3.5e-6,
    cf=3.6e-6,
    aquifer=None,
)

analysis = Analysis(tank_class=tank1, freq="12MS", position="end")

# PLOTS
plot1 = analysis.plot_flow_rate_tank()
# plot1.show()

plot2 = analysis.plot_press_time()
# plot2.show()

plot3 = analysis.plot_press_avg_time()
# plot3.show()

plot4 = analysis.plot_press_liq_cum()
# plot4.show()

plt5 = analysis.plot_press_avg_liq_cum()
# plt5.show()

plt6 = analysis.plot_cum_prod_time()
# plt6.show()

plt7 = analysis.plot_cum_prod_tot_time()
# plt7.show()

plt8 = analysis.plot_flow_rate_well()
# plt8.show()

plt9 = analysis.plot_cum_prod_well()
# plt9.show()
