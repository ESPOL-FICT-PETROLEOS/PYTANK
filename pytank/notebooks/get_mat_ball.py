from pytank.constants.constants import (OIL_FVF_COL,
                                        GAS_FVF_COL,
                                        RS_COL,
                                        PRESSURE_COL,
                                        OIL_CUM_COL,
                                        GAS_CUM_COL,
                                        WATER_CUM_COL,
                                        DATE_COL,
                                        WELL_COL,
                                        WATER_FVF_COL,
                                        RS_W_COL,
                                        TANK_COL,
                                        LIQ_CUM,
                                        UW_COL,
                                        PRESSURE_PVT_COL)
from pytank.functions.pvt_interp import interp_pvt_matbal
from pytank.functions.utilities import interp_dates_row
from pytank.notebooks.get_wells import tank_wells
from pytank.fluid_model.fluid import OilModel, WaterModel
from pytank.functions.pvt_correlations import RS_bw, Bo_bw
from pytank.tank.tank import Tank
import pandas as pd

df_pvt = pd.read_csv("../resources/data_csv/pvt.csv")
tank_dict = tank_wells
tank_name = list(tank_dict.keys())[0]
oil_model = OilModel(
    data_pvt=df_pvt,
    temperature=25,
)

water_model = WaterModel(
    correlation_bw=Bo_bw,
    correlation_rs=RS_bw,
    salinity=3000,
    temperature=200,
    unit=1
)

# Uw calc
uw = Tank(
    tanks=tank_dict,
    name=tank_name,
    wells=tank_dict[tank_name],
    oil_model=oil_model,
    water_model=water_model
).calc_uw()

# Average Pressure
avg = Tank(
    tanks=tank_dict,
    name=tank_name,
    wells=tank_dict[tank_name],
    oil_model=oil_model,
    water_model=water_model
).pressure_vol_avg(
    avg_freq="12MS",
    position="end"
)

prod = Tank(
    tanks=tank_dict,
    name=tank_name,
    wells=tank_dict[tank_name],
    oil_model=oil_model,
    water_model=water_model
).prod_df_int()

avg[PRESSURE_COL] = avg[PRESSURE_COL].interpolate(method='linear')

cols_input = [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]
cols_output = ["oil_vol", "water_vol", "gas_vol"]
prod[cols_output] = (prod.groupby(WELL_COL)[cols_input]).diff().fillna(prod[cols_input])

cols_group = [DATE_COL, TANK_COL, "oil_vol", "water_vol", "gas_vol"]
df_tanks = (
    prod[cols_group]
    .groupby(cols_group[0:2])
    .sum()
    .groupby(TANK_COL)
    .cumsum()
    .reset_index()
)

df_tanks.rename(columns={
    "oil_vol": OIL_CUM_COL,
    "water_vol": WATER_CUM_COL,
    "gas_vol": GAS_CUM_COL
}, inplace=True)

oil_cum_col_per_tank = OIL_CUM_COL + "_Tank"
water_cum_col_per_tank = WATER_CUM_COL + "_Tank"
gas_cum_col_per_tank = GAS_CUM_COL + "_Tank"

for col, cum_col in zip([oil_cum_col_per_tank, water_cum_col_per_tank, gas_cum_col_per_tank],
                       [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]):
    avg[col] = avg.apply(
        lambda g: interp_dates_row(
            g, DATE_COL, df_tanks, DATE_COL, cum_col, TANK_COL, TANK_COL
        ),
        axis=1
    )

df_mbal = avg.sort_values(DATE_COL)

for col, prop in zip([OIL_FVF_COL, GAS_FVF_COL, RS_COL],
                    [OIL_FVF_COL, GAS_FVF_COL, RS_COL]):
    df_mbal[col] = df_mbal[PRESSURE_COL].apply(
        lambda press: interp_pvt_matbal(df_pvt, PRESSURE_PVT_COL, prop, press)
    )

df_mbal = pd.concat([df_mbal, df_mbal[OIL_FVF_COL], df_mbal[GAS_FVF_COL], df_mbal[RS_COL]], axis=1).sort_values(DATE_COL)

# Rename columns to match the variables names stated in the file attached in unterbase
df_mbal.rename(columns={
    "OIL_CUM_Tank": OIL_CUM_COL,
    "WATER_CUM_Tank": WATER_CUM_COL,
    "GAS_CUM_Tank": GAS_CUM_COL
}, inplace=True)

# Convert the mbal dataframe to a csv file
#df_mbal.to_csv("mbal_Dataframe2.csv", index=False)
print(df_mbal)