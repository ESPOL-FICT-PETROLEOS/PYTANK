# %%
# Importing necessary libraries and modules
import pandas as pd
from new.constants import (OIL_CUM_COL,
                           WATER_CUM_COL,
                           GAS_CUM_COL,
                           LIQ_CUM,
                           PRESSURE_COL,
                           TANK_COL,
                           DATE_COL,
                           OIL_FVF_COL,
                           GAS_FVF_COL,
                           RS_COL)
from new.vector_data import ProdVector, PressVector
from new.well import Well
from new.utilities import normalize_date_freq
from collections import defaultdict
from pandera.errors import SchemaError
from uw import underground_widrawal
from new.fluid import FluidModel

# Data to process production info
df_production = pd.read_csv("../old/tests/data_for_tests/full_example_1/production.csv")
df_production[DATE_COL] = pd.to_datetime(df_production[DATE_COL])
df_production.set_index(df_production[DATE_COL], inplace=True)

# Data to process pressure info
df_pressures = pd.read_csv("../old/tests/data_for_tests/full_example_1/pressures.csv")
df_pressures.rename(columns={"DATE": "START_DATETIME", "WELLLBORE": "ITEM_NAME"}, inplace=True)
df_pressures["START_DATETIME"] = pd.to_datetime(df_pressures["START_DATETIME"])

# Data to process pvt info
df_pvt = pd.read_csv("../old/tests/data_for_tests/full_example_1/pvt.csv")

# Empty dictionary for the different tanks
tank_wells = defaultdict(list)

EXPECTED_FREQ = "MS"
# Group data by well name and apply the function to create ProdWell objects
for name, group_prod in df_production.groupby("ITEM_NAME"):
    print(f"Creating well {name}")

    group_prod = group_prod.rename(
        columns={
            OIL_CUM_COL: OIL_CUM_COL,
            WATER_CUM_COL: WATER_CUM_COL,
            GAS_CUM_COL: GAS_CUM_COL,
            TANK_COL: TANK_COL
        }
    )
    group_prod[LIQ_CUM] = group_prod[OIL_CUM_COL] + group_prod[WATER_CUM_COL]

    group_prod = group_prod[[OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM, TANK_COL]]
    group_prod_norm = normalize_date_freq(df=group_prod,
                                          freq=EXPECTED_FREQ,
                                          method_no_cols="ffill",
                                          )

    try:
        prod_vector = ProdVector(
            freq=EXPECTED_FREQ,
            data=group_prod_norm
        )
    except SchemaError as e:
        expected_error_msg = 'ValueError("Need at least 3 dates to infer frequency")'
        if str(e) == expected_error_msg:
            # group_prod_norm = group_prod_norm.asfreq(EXPECTED_FREQ)
            group_prod_norm.index.freq = EXPECTED_FREQ
            prod_vector = ProdVector(
                freq=None,
                data=group_prod_norm
            )

    # In case where wells don't have pressure info
    press_vector = None
    # Check if there's pressure data available for this well
    if name in df_pressures["WELLBORE"].unique():
        group_press = df_pressures[df_pressures["WELLBORE"] == name]

        # Interpolated pvt properties
        pvt = FluidModel(
            data_pvt=df_pvt
        )

        # Create a copy of group_press to avoid warnings
        group_press = group_press.copy()

        # Add columns of pvt properties
        group_press[OIL_FVF_COL] = pvt.get_bo_at_press(group_press[PRESSURE_COL])
        group_press[GAS_FVF_COL] = pvt.get_bg_at_press(group_press[PRESSURE_COL])
        group_press[RS_COL] = pvt.get_rs_at_press(group_press[PRESSURE_COL])

        # Renaming columns of pressure data
        group_press = group_press.rename(
            columns={
                PRESSURE_COL: PRESSURE_COL,
                OIL_FVF_COL: OIL_FVF_COL,
                GAS_FVF_COL: GAS_FVF_COL,
                RS_COL: RS_COL,
            }
        )
        group_press.set_index("START_DATETIME", inplace=True)

        press_vector = PressVector(
            freq=None,
            data=group_press
        )

    # Creating Well object with both production and pressure data
    info_well = Well(
        name=name,
        prod_data=prod_vector,
        press_data=press_vector
    )

    tank_wells[group_prod_norm[TANK_COL].iloc[0]].append(info_well)

print(tank_wells["tank_center"])

for tank, wells in tank_wells.items():
    for well in wells:
        prod_vector = well.prod_data
        press_vector = well.press_data
        try:
            total_withdrawal = underground_widrawal(prod_vector, press_vector)
            print(f"Total Underground withdrawal for {well.name}", total_withdrawal)

        except Exception as e:
            print(e)
