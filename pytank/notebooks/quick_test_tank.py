import pandas as pd
from pytank.fluid_model.fluid import OilModel, WaterModel
from pytank.tank.tank import Tank
from pytank.well.well import Well

# Quicktest
df_pvt = pd.read_csv("../resources/data_csv/pvt.csv")
df_production = pd.read_csv("../resources/data_csv/production.csv")
df_pressures = pd.read_csv("../resources/data_csv/pressures.csv")
freq = "MS"

tank_name = "tank_center"

well = Well(df_prod=df_production, df_press=df_pressures)

oil_model = OilModel(
    data_pvt=df_pvt,
    temperature=200,
)

water_model = WaterModel(
    salinity=3000,
    temperature=200,
    unit=1
)

tank1 = Tank(
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
