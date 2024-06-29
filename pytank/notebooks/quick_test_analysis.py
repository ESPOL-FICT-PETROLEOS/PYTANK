from pytank.notebooks.quick_test_tank import (tank1,
                                              well,
                                              tank_name,
                                              oil_model,
                                              water_model)
# from pytank.aquifer.aquifer_model import Fetkovich, CarterTracy
from pytank.analysis.poes import Analysis
from pytank.tank.tank import Tank

# No Aquifer Case
analysis1 = Analysis(tank_class=tank1, freq="12MS", position="end")

tank_with_aquifer = Tank(
    name=tank_name,
    wells=well,
    oil_model=oil_model,
    water_model=water_model,
    pi=3700,
    swo=0.25,
    cw=3.5e-6,
    cf=4.5e-6,
    aquifer=None
)

analysis2 = Analysis(tank_class=tank_with_aquifer,
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

analysis2.setup_fetkovich_aquifer(
    aq_radius=aq_radius,
    res_radius=res_radius,
    aq_thickness=aq_thickness,
    aq_por=phi,
    ct=ct,
    theta=theta,
    k=k,
    water_visc=water_visc,
)


anali_fet = analysis2.analytic_method(72e+6, "plot")
havle = analysis2.havlena_odeh("plot")
havle.show()


# With Carter Tracy
res_radius = 2000
aq_thickness = 13
phi = 0.30
ct = 0.000007
theta = 140
k = 25


water_visc = 0.6
analysis2.setup_carter_tracy_aquifer(
    aq_por=phi,
    ct=ct,
    res_radius=res_radius,
    aq_thickness=aq_thickness,
    theta=theta,
    aq_perm=k,
    water_visc=water_visc
)
anali_carter = analysis2.analytic_method(72e+6, "plot")
anali_carter.show()

x = analysis1.eda()
