"""
mat_bal_implementation.py

This file containing the steps to use the PyTank library .
"""

# %%
import pandas as pd
from pytank.fluid_model.fluid import OilModel, WaterModel
from pytank.tank.tank import Tank
from pytank.well.well import Wells
from pytank.analysis.poes import Analysis
from pytank.aquifer.aquifer_model import Fetkovich, CarterTracy

# transform the csv to dataframes
df_pvt = pd.read_csv("C:/Users/User/PycharmProjects/PYTANK/pytank/resources/data_csv/pvt.csv")
df_production = pd.read_csv("C:/Users/User/PycharmProjects/PYTANK/pytank/resources/data_csv/production.csv")
df_pressures = pd.read_csv("C:/Users/User/PycharmProjects/PYTANK/pytank/resources/data_csv/pressures.csv")

"------------------------------------- Well Module----------------------------------------"

well = Wells(df_prod=df_production,
             df_press=df_pressures,
             freq_prod="MS",
             freq_press=None)
all_wells = well.get_wells()
my_wells = ["A-1-P", "A-10-P", "A-11-P"]
wells_info = well.search_wells(my_wells)

# %%
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

# %%
"------------------------------------- Tank Module ------------------------------------------"
tank_name = "tank_center"
tank1 = Tank(
    name=tank_name,
    wells=wells_info,
    oil_model=oil_model,
    water_model=water_model,
    pi=3700,
    swo=0.25,
    cw=3.5e-6,
    cf=4.6e-6,
    aquifer=None
)
df_press = tank1.get_pressure_df()

# %%
"------------------------------------ Analysis Module ---------------------------------------"
analysis = Analysis(
    tank_class=tank1,
    freq="12MS",
    position="end"
)

"Campbell"
camp = analysis.campbell("plot")
camp.show()

# %%
"Havlena"
havlena_plot = analysis.havlena_odeh("plot")
havlena_data = analysis.havlena_odeh("data")
havlena_plot.show()
print(havlena_data)

# %%
"----------------------------------Aquifer Models--------------------------------------------"

"With Aquifer - Fetkovich-------------------"
aq_radius = 14000
res_radius = 2000
aq_thickness = 20
phi = 0.25
ct = 0.000007
theta = 290
k = 25
water_visc = 0.6

mbal_tank1 = analysis.mat_bal_df()
pr_list = list(mbal_tank1["PRESSURE_DATUM"])
ts_list = list(mbal_tank1["Time_Step"])

fet = Fetkovich(
    aq_radius=aq_radius,
    res_radius=res_radius,
    aq_thickness=aq_thickness,
    aq_por=phi,
    ct=ct,
    theta=theta,
    k=k,
    water_visc=water_visc,
    pr=pr_list,
    time_step=ts_list
)

tank_fet = Tank(
    name=tank_name,
    wells=wells_info,
    oil_model=oil_model,
    water_model=water_model,
    pi=3700,
    swo=0.25,
    cw=3.5e-6,
    cf=4.6e-6,
    aquifer=fet
)

analysis_fet = Analysis(
    tank_class=tank_fet,
    freq="12MS",
    position="end"
)

"Analytic method"

analitic_meth_fet = analysis_fet.analytic_method(
    poes=67e+6,
    option="plot"
)
analitic_meth_fet.show()

"Havlena Method"
havlena_fet = analysis_fet.havlena_odeh("plot")
havlena_fet.show()

# %%
"With Aquifer - Carter Tracy-----------------"
res_radius = 2000
aq_thickness = 13
phi = 0.30
ct = 0.000007
theta = 140
k = 25
water_visc = 0.6

carter = CarterTracy(
    aq_por=phi,
    ct=ct,
    res_radius=res_radius,
    aq_thickness=aq_thickness,
    theta=theta,
    aq_perm=k,
    water_visc=water_visc,
    pr=pr_list,
    time=ts_list
)

tank_carter = Tank(
    name=tank_name,
    wells=wells_info,
    oil_model=oil_model,
    water_model=water_model,
    pi=3700,
    swo=0.25,
    cw=3.5e-6,
    cf=4.6e-6,
    aquifer=carter
)

analysis_carter = Analysis(
    tank_class=tank_carter,
    freq="12MS",
    position="end"
)

"Analytic method"
analitic_meth_car = analysis_carter.analytic_method(
    poes=67e+6,
    option="plot"
)
analitic_meth_car.show()

"Havlena Method"
havlena_car = analysis_carter.havlena_odeh("plot")
havlena_car.show()

# %%
"----GRAPHS---"
plot1 = analysis_carter.plot_cum_prod_per_well()
plot1.show()

plot2 = analysis_carter.plot_press_time()
plot2.show()

plot3 = analysis_carter.plot_press_avg_time()
plot3.show()

plot4 = analysis_carter.plot_press_liq_cum()
plot4.show()

plt5 = analysis_carter.plot_press_avg_liq_cum()
plt5.show()

plt6 = analysis_carter.plot_cum_prod_time()
plt6.show()

plt7 = analysis_carter.plot_cum_prod_tot_time()
plt7.show()
