# %%
# Importing necessary libraries and modules
import warnings
from collections import defaultdict

import pandas as pd
from pandera.errors import SchemaError

from pytank.constants.constants import (OIL_CUM_COL, WATER_CUM_COL,
                                        GAS_CUM_COL, LIQ_CUM, PRESSURE_COL,
                                        DATE_COL)
from pytank.functions.utilities import normalize_date_freq
from pytank.vector_data.vector_data import ProdVector, PressVector
from pytank.well.well import Well

# Avoid warnings
warnings.filterwarnings("ignore",
                        message="DataFrame.fillna with 'method' is deprecated")

# Data to process production info
df_production = pd.read_csv("../resources/data_csv/production.csv")
df_production[DATE_COL] = pd.to_datetime(df_production[DATE_COL])
df_production.set_index(df_production[DATE_COL], inplace=True)

# Data to process pressure info
df_pressures = pd.read_csv("../resources/data_csv/pressures.csv")
df_pressures.rename(columns={
    "DATE": "START_DATETIME",
    "WELLBORE": "ITEM_NAME"
},
    inplace=True)
df_pressures["START_DATETIME"] = pd.to_datetime(df_pressures["START_DATETIME"])

# Empty dictionary for the different tanks
tank_wells = defaultdict(list)
cols_fills_na = [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM]
EXPECTED_FREQ = "MS"

# Create a set with all well names from both DataFrames
all_wells = set(df_production["ITEM_NAME"]).union(df_pressures["WELLBORE"])
list_wells = []
for name in all_wells:
    # Initialize production and pressure vectors as None
    prod_vector = None
    press_vector = None

    # If the well has production data, process it
    if name in df_production["ITEM_NAME"].unique():
        group_prod = df_production[df_production["ITEM_NAME"] == name]

        group_prod = group_prod.rename(
            columns={
                OIL_CUM_COL: OIL_CUM_COL,
                WATER_CUM_COL: WATER_CUM_COL,
                GAS_CUM_COL: GAS_CUM_COL,
            })
        group_prod[
            LIQ_CUM] = group_prod[OIL_CUM_COL] + group_prod[WATER_CUM_COL]
        group_prod = group_prod[[
            OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM
        ]]

        group_prod_norm = normalize_date_freq(
            df=group_prod,
            freq=EXPECTED_FREQ,
            cols_fill_na=cols_fills_na,
            method_no_cols="ffill",
        )
        try:
            prod_vector = ProdVector(freq=EXPECTED_FREQ, data=group_prod_norm)
            # In case where wells don't have pressure info

        except SchemaError as e:
            expected_error_msg = ('ValueError("Need at least 3 dates to infer'
                                  ' frequency")')
            if str(e) == expected_error_msg:
                # group_prod_norm = group_prod_norm.asfreq(EXPECTED_FREQ)
                group_prod_norm.index.freq = EXPECTED_FREQ
                prod_vector = ProdVector(freq=None, data=group_prod_norm)

    # If the well has pressure data, process it
    if name in df_pressures["WELLBORE"].unique():
        group_press = df_pressures[df_pressures["WELLBORE"] == name]

        # Renaming columns of pressure data
        group_press = group_press.rename(columns={
            PRESSURE_COL: PRESSURE_COL,
        })
        group_press.set_index("START_DATETIME", inplace=True)
        press_vector = PressVector(freq=None, data=group_press)

    # Creating Well object with both production and pressure data
    info_well = Well(name=name,
                     prod_data=prod_vector,
                     press_data=press_vector)

    # Add the well to the tank dictionary
    list_wells.append(info_well)
