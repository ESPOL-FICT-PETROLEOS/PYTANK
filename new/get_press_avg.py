from get_wells import tank_wells
from new.constants import (OIL_FVF_COL, GAS_FVF_COL, RS_COL, PRESSURE_COL, OIL_CUM_COL, GAS_CUM_COL, WATER_CUM_COL,LIQ_CUM,
                           DATE_COL, WELL_COL, WATER_FVF_COL, RS_W_COL, TANK_COL
                           )
import pandas as pd
from fluid import OilModel, WaterModel
from new.utilities import interp_dates_row
from old.utilities.pvt_correlations import RS_bw, Bo_bw
from old.material_balance import underground_withdrawal


df_pvt = pd.read_csv("../old/tests/data_for_tests/full_example_1/pvt.csv")
pvt = OilModel(data_pvt=df_pvt, temperature=25)


df_press = pd.DataFrame()
df_prod = pd.DataFrame()

for tank_name, wells in tank_wells.items():
    for well in wells:
        press_vector = well.press_data
        prod_vector = well.prod_data
        if press_vector is not None:
            well_name = well.name
            well_date = press_vector.data.index
            well_oil_fvf = pvt.get_bo_at_press(press_vector.data[PRESSURE_COL])
            well_gas_fvf = pvt.get_bg_at_press(press_vector.data[PRESSURE_COL])
            well_rs = pvt.get_rs_at_press(press_vector.data[PRESSURE_COL])
            #well_water_fvf = WaterModel(correlation_bw=Bo_bw, correlation_rs=RS_bw, salinity=3000, temperature=200,
            #                            unit=1).get_bw_at_press(press_vector.data[PRESSURE_COL])
            #well_rs_w = WaterModel(correlation_bw=Bo_bw, correlation_rs=RS_bw, salinity=3000, temperature=200,
            #                       unit=1).get_rs_at_press(press_vector.data[PRESSURE_COL])

            # Create a copy of data from press_vector
            temp_df_press = press_vector.data.copy()

            # Add columns to DataFrame
            temp_df_press[WELL_COL] = well_name
            temp_df_press[DATE_COL] = well_date
            temp_df_press[OIL_FVF_COL] = well_oil_fvf
            temp_df_press[GAS_FVF_COL] = well_gas_fvf
            temp_df_press[RS_COL] = well_rs
            #temp_df_press[WATER_FVF_COL] = well_water_fvf
            #temp_df_press[RS_W_COL] = well_rs_w
            temp_df_press[TANK_COL] = tank_name

            df_press = pd.concat([df_press, temp_df_press], ignore_index=True)

        if prod_vector is not None:
            well_name = well.name
            well_date = prod_vector.data.index
            well_oil_cum = prod_vector.data[OIL_CUM_COL]
            well_water_cum = prod_vector.data[WATER_CUM_COL]
            well_gas_cum = prod_vector.data[GAS_CUM_COL]
            well_liq_cum = prod_vector.data[LIQ_CUM]

            temp_df_prod = prod_vector.data.copy()

            temp_df_prod[WELL_COL] = well_name
            temp_df_prod[DATE_COL] = well_date
            temp_df_prod[OIL_CUM_COL] = well_oil_cum
            temp_df_prod[WATER_CUM_COL] = well_water_cum
            temp_df_prod[GAS_CUM_COL] = well_gas_cum
            temp_df_prod[LIQ_CUM] = well_liq_cum

            df_prod = pd.concat([df_prod, temp_df_prod], ignore_index=True)

print(1)
#df_prod = df_prod.sort_values(by=[WELL_COL,DATE_COL])
#df_press = df_press.sort_values(by=[WELL_COL,DATE_COL])


for col in [OIL_CUM_COL,WATER_CUM_COL,GAS_CUM_COL]:
    df_press[col] = df_press.apply(
        lambda x: interp_dates_row(
            x, DATE_COL, df_prod, DATE_COL, col, WELL_COL, WELL_COL, left=0.0
        ),
        axis=1,
    )
    # For wells not available in the production data frame, fill nans with 0
    df_press[col].fillna(0, inplace=True)

df_press["UW"] = underground_withdrawal(
    df_press,
    OIL_CUM_COL,
    WATER_CUM_COL,
    GAS_CUM_COL,
    OIL_FVF_COL,
    1,
    GAS_FVF_COL,
    RS_COL,
    0,
)
print(2)
#df_press.set_index(["START_DATETIME"], inplace=True)
#print(df_press[[WELL_COL,PRESSURE_COL,OIL_FVF_COL,GAS_FVF_COL,RS_COL]])
df_press.to_csv("uw_.csv", index=False)
df_prod.to_csv("prod_1.csv",index=False)
