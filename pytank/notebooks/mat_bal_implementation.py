"""
mat_bal_implementation.py

This file containing the steps to use the PyTank library .
"""

#%%
import pandas as pd
from pytank.fluid_model.fluid import OilModel, WaterModel
from pytank.tank.tank import Tank
from pytank.well.well import Well
from pytank.analysis.poes import Analysis

# transform the csv to dataframes
df_pvt = pd.read_csv("C:/Users/CompuMundo/PycharmProjects/PYTANK/pytank/resources/data_csv/pvt.csv")
df_production = pd.read_csv("C:/Users/CompuMundo/PycharmProjects/PYTANK/pytank/resources/data_csv/production.csv")
df_pressures = pd.read_csv("C:/Users/CompuMundo/PycharmProjects/PYTANK/pytank/resources/data_csv/pressures.csv")

"------------------------------------- Well Module----------------------------------------"
freq = "MS"

well = Well(df_prod=df_production,
            df_press=df_pressures,
            freq_prod=freq,
            freq_press=None)
well_dict = well.get_wells()
print(well_dict)
#%%
"--------------------------------- Fluid Models Module -----------------------------------"
oil_model = OilModel(
    data_pvt=df_pvt,
    temperature=25,
)

water_model = WaterModel(
    salinity=3000,
    temperature=200,
    unit=1
)

#%%
"------------------------------------- Tank Module ------------------------------------------"
tank_name = "tank_center"
tank1 = Tank(
    name=tank_name,
    wells=well,
    oil_model=oil_model,
    water_model=water_model,
    pi=3700,
    swo=0.25,
    cw=3.5e-6,
    cf=4.6e-6,
    aquifer=None
)
df_press = tank1.get_pressure_df()
print(df_press)

#%%
"------------------------------------ Analysis Module ---------------------------------------"
analysis = Analysis(
    tank_class=tank1,
    freq="12MS",
    position="end"
)

"Campbell"
camp = analysis.campbell("plot")
camp.show()

#%%
"Havlena"
havlena_plot = analysis.havlena_odeh("plot")
havlena_data = analysis.havlena_odeh("data")
havlena_plot.show()
print(havlena_data)

#%%
"With Aquifer - Fetkovich"
aq_radius = 14000
res_radius = 2000
aq_thickness = 20
phi = 0.25
ct = 0.000007
theta = 290
k = 25
water_visc = 0.6

analysis.setup_fetkovich_aquifer(
    aq_radius=aq_radius,
    res_radius=res_radius,
    aq_thickness=aq_thickness,
    aq_por=phi,
    ct=ct,
    theta=theta,
    k=k,
    water_visc=water_visc,
)
"Analytic method"

analitic_meth_fet = analysis.analytic_method(
    poes=67e+6,
    option="plot"
)
analitic_meth_fet.show()

"Havlena Method"
havlena_fet = analysis.havlena_odeh("plot")
havlena_data = analysis.havlena_odeh("data")
havlena_fet.show()
print(havlena_data)

#%%
"With Aquifer - Carter Tracy"
res_radius = 2000
aq_thickness = 13
phi = 0.30
ct = 0.000007
theta = 140
k = 25
water_visc = 0.6
analysis.setup_carter_tracy_aquifer(
    aq_por=phi,
    ct=ct,
    res_radius=res_radius,
    aq_thickness=aq_thickness,
    theta=theta,
    aq_perm=k,
    water_visc=water_visc
)
"Analytic method"
analitic_meth_car = analysis.analytic_method(
    poes=67e+6,
    option="plot"
)
analitic_meth_car.show()

"Havlena Method"
havlena_car = analysis.havlena_odeh("plot")
havlena_car_data = analysis.havlena_odeh("data")
havlena_car.show()
print(havlena_car_data)

#%%
"----EDA METHOD---"
eda_plot = analysis.eda(
    method="production_per_well",
    option=None
)
eda_plot.show()
