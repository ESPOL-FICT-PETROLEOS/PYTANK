from pytank.notebooks.quick_test_tank import (tank1,
                                              tank_dict,
                                              tank_name,
                                              oil_model,
                                              water_model)
from pytank.aquifer.aquifer_model import Fetkovich
from pytank.analysis.poes import Analysis
from pytank.tank.tank import Tank

# No Aquifer Case
analisis1 = Analysis(tank_class=tank1, freq="12MS", position="end")

mbal1 = analisis1.havlena_odeh2("data")

# Analysis 2 (Aquifer Case)
aq_radius = 46000
res_radius = 9200
aq_thickness = 100
phi = 0.25
ct = 0.000007
pr = list(analisis1.mat_bal_df()["PRESSURE_DATUM"])
theta = 140
k = 200
water_visc = 0.55
time_step = list(analisis1.mat_bal_df()["Time_Step"])

we_fet = Fetkovich(aq_radius,
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
    wells=tank_dict[tank_name],
    oil_model=oil_model,
    water_model=water_model,
    pi=3700,
    swo=0.15,
    cw=3.5e-6,
    cf=3.6e-6,
    aquifer=we_fet
)
analisis2 = Analysis(tank_class=tank_with_aquifer, freq="12MS", position="end")
mbal2 = analisis2.havlena_odeh("data")
print(mbal2)
