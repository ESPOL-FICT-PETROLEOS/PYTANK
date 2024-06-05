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
                           WELL_COL
                           )
from new.vector_data import ProdVector, PressVector
from new.well import Well
from new.utilities import normalize_date_freq
from collections import defaultdict
from pandera.errors import SchemaError
import warnings

# Avoid warnings
warnings.filterwarnings("ignore", message="DataFrame.fillna with 'method' is deprecated")

# Data to process production info
df_production = pd.read_csv("../old/tests/data_for_tests/full_example_1/production.csv")
df_production[DATE_COL] = pd.to_datetime(df_production[DATE_COL])
df_production.set_index(df_production[DATE_COL], inplace=True)

# Data to process pressure info
df_pressures = pd.read_csv("../old/tests/data_for_tests/full_example_1/pressures.csv")
df_pressures.rename(columns={"DATE": "START_DATETIME", "WELLLBORE": "ITEM_NAME"}, inplace=True)
df_pressures["START_DATETIME"] = pd.to_datetime(df_pressures["START_DATETIME"])

# Empty dictionary for the different tanks
tank_wells = defaultdict(list)
cols_fills_na = [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM, TANK_COL]
EXPECTED_FREQ = "MS"

# Create a set with all well names from both DataFrames
all_wells = sorted(set(df_production["ITEM_NAME"]).union(df_pressures["WELLBORE"]))

for name in all_wells:
    # Initialize production and pressure vectors as None
    prod_vector = None
    press_vector = None

    # If the well has production data, process it
    if name in df_production["ITEM_NAME"].unique():
        group_prod = df_production[df_production["ITEM_NAME"] == name]

        group_prod = group_prod.rename(
            columns={
                OIL_CUM_COL:OIL_CUM_COL,
                WATER_CUM_COL:WATER_CUM_COL,
                GAS_CUM_COL:GAS_CUM_COL,
                TANK_COL:TANK_COL
            }
        )
        group_prod[LIQ_CUM] = group_prod[OIL_CUM_COL] + group_prod[WATER_CUM_COL]
        group_prod = group_prod[[OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM, TANK_COL]]

        """group_prod_norm = normalize_date_freq(df=group_prod,
                                              freq=EXPECTED_FREQ,
                                              cols_fill_na=cols_fills_na,
                                              method_no_cols="ffill",
                                              )"""
        try:
            prod_vector = ProdVector(
                freq=None,
                data=group_prod
            )
            # In case where wells don't have pressure info

        except SchemaError as e:
            expected_error_msg = 'ValueError("Need at least 3 dates to infer frequency")'
            if str(e) == expected_error_msg:
                # group_prod_norm = group_prod_norm.asfreq(EXPECTED_FREQ)
                group_prod.index.freq = EXPECTED_FREQ
                prod_vector = ProdVector(
                    freq=None,
                    data=group_prod
                )
        tank_name = group_prod[TANK_COL].iloc[0]

    # If the well has pressure data, process it
    if name in df_pressures["WELLBORE"].unique():
        group_press = df_pressures[df_pressures["WELLBORE"] == name]

        # Renaming columns of pressure data
        group_press = group_press.rename(
            columns={
                PRESSURE_COL: PRESSURE_COL,
            }
        )
        group_press.set_index("START_DATETIME", inplace=True)
        press_vector = PressVector(
            freq=None,
            data=group_press
        )

        # If there is no production data, get the tank name from the pressure data
        if prod_vector is None and TANK_COL in group_press.columns:
            tank_name = group_press[TANK_COL].iloc[0]

        # Creating Well object with both production and pressure data
    info_well = Well(
        name=name,
        prod_data=prod_vector,
        press_data=press_vector
    )

    # Add the well to the tank dictionary
    tank_wells[tank_name].append(info_well)

