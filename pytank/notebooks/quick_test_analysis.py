from pytank.notebooks.quick_test_tank import (tank1,
                                              well,
                                              tank_name,
                                              oil_model,
                                              water_model)
from pytank.aquifer.aquifer_model import Fetkovich
from pytank.analysis.poes import Analysis
from pytank.tank.tank import Tank

# No Aquifer Case
analisis1 = Analysis(tank_class=tank1, freq="12MS", position="end")

# Analysis 2 (Aquifer Case)
aq_radius = 14000
res_radius = 2000
aq_thickness = 20
phi = 0.25
ct = 0.000007
pr = list(analisis1.mat_bal_df()["PRESSURE_DATUM"])
theta = 290
k = 25
water_visc = 0.6
time_step = list(analisis1.mat_bal_df()["Time_Step"])

we = Fetkovich(aq_radius,
               res_radius,
               aq_thickness,
               phi,
               ct,
               pr,
               theta,
               k,
               water_visc,
               time_step)

tank_with_aquifer = Tank(
    name=tank_name,
    wells=well,
    oil_model=oil_model,
    water_model=water_model,
    pi=3700,
    swo=0.25,
    cw=3.5e-6,
    cf=4.5e-6,
    aquifer=we
)

analisis2 = Analysis(tank_class=tank_with_aquifer, freq="12MS", position="end")

analit_data = analisis2.analytic_method(72e+6, option="data")
print(analit_data)
analit_figure = analisis2.analytic_method(72e+6, option="plot")
analit_figure.show()
havlnea_N = analisis2.havlena_odeh(option="plot")
havlnea_N.show()
havlnea_N_data = analisis2.havlena_odeh(option="data")
print(havlnea_N_data)
