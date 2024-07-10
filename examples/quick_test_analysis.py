from quick_test_tank import (tank1,
                             wells_info,
                             tank_name,
                             oil_model,
                             water_model)
from pytank.aquifer_model import Fetkovich
from pytank.analysis import Analysis
from pytank.tank import Tank

# No Aquifer Case
analysis1 = Analysis(tank_class=tank1,
                     freq="12MS",
                     position="end")

# With Fetkovich
aq_radius = 14000
res_radius = 2000
aq_thickness = 20
phi = 0.25
ct = 0.000007
theta = 290
k = 25
water_visc = 0.6

fet = Fetkovich(
    aq_radius=aq_radius,
    res_radius=res_radius,
    aq_thickness=aq_thickness,
    aq_por=phi,
    ct=ct,
    theta=theta,
    k=k,
    water_visc=water_visc,
)

tank_fet = Tank(name=tank_name,
                wells=wells_info,
                oil_model=oil_model,
                water_model=water_model,
                pi=3700,
                swo=0.25,
                cw=3.5e-6,
                cf=4.5e-6,
                aquifer=fet)

analysis_aquifer = Analysis(
    tank_class=tank_fet,
    freq="12MS",
    position="end")

# analytic = analysis_aquifer.analytic_method(72e+6, "plot")
# analytic.show()
# havlena = analysis_aquifer.havlena_odeh_plot()
# havlena.show()
