import pandas as pd
from pytank.fluid_model.fluid import OilModel, WaterModel
from pytank.notebooks.get_wells import tank_wells
from pytank.tank.tank import Tank
from pytank.analysis.poes import Analysis
from pytank.notebooks.quick_test_tank import well

# Quicktest
df_pvt = pd.read_csv("../resources/data_csv/pvt.csv")

tank_dict = tank_wells
tank_name = "tank_center"

oil_model = OilModel(
    data_pvt=df_pvt,
    temperature=25,
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
    swo=0.15,
    cw=3.5e-6,
    cf=3.6e-6,
    aquifer=None
)

analysis = Analysis(tank_class=tank1, freq="12MS", position="end")

eda = analysis.campbell(option="plot")
print(eda)