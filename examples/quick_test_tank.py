import pandas as pd
from pytank.fluid_model import OilModel, WaterModel
from pytank.tank import Tank
from pytank.functions.helpers import create_wells, search_wells

# Quicktest
df_pvt = pd.read_csv("../examples_data/pvt.csv")
df_production = pd.read_csv("../examples_data/production.csv")
df_pressures = pd.read_csv("../examples_data/pressures.csv")
freq = "MS"

tank_name = "tank_center"

wells = create_wells(df_prod=df_production,
                     df_press=df_pressures,
                     freq_prod=freq,
                     freq_press=None)

# List of wells for user selection
my_wells = [
    "A-1-P", "A-10-P", "A-11-P", "A-12-P", "A-13-P", "A-14-P", "A-16-P",
    "A-17-P", "A-18-P", "A-19-P", "A-21-P", "A-22-P", "A-23-P", "A-24-I",
    "A-4-P", "A-5-P", "A-6-P", "A-8-P", "A-9-P"
]

# lis of wells with the pressure and production info for user selection
wells_info = search_wells(wells, my_wells)


oil_model = OilModel(
    data_pvt=df_pvt,
    temperature=25,
)

water_model = WaterModel(salinity=3000, temperature=200, unit=1)

tank1 = Tank(name=tank_name,
             wells=wells_info,
             oil_model=oil_model,
             water_model=water_model,
             pi=3700,
             swo=0.15,
             cw=3.5e-6,
             cf=3.6e-6,
             aquifer=None)

# Its only a test, this method is PRIVATE
df_press = tank1.get_pressure_df()
# print(df_press)
