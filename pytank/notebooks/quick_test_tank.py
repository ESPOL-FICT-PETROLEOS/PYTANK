import pandas as pd
from pytank.fluid_model.fluid import OilModel, WaterModel
from pytank.notebooks.get_wells import tank_wells
from pytank.tank.tank import Tank

# Quicktest
df_pvt = pd.read_csv("../resources/data_csv/pvt.csv")
# df_pvt[GAS_FVF_COL].fillna(0)

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

tank = Tank(
    tanks=tank_dict,
    name=tank_name,
    wells=tank_dict[tank_name],
    oil_model=oil_model,
    water_model=water_model
)
# Uw calc
mbal = tank.mat_bal_df("12MS", "end", 0.15, 3.5e-6, 3.62e-6, 3700)
mbal2 = tank.mat_bal_df2("12MS", "end", 0.15, 3.5e-6, 3.62e-6, 3700)
print(mbal)
print(mbal2)
mbal_nosotros = mbal.to_csv("mbal_nosotros.csv", index=False)
mbal_oscar = mbal2.to_csv("mbal_oscar.csv", index=False)