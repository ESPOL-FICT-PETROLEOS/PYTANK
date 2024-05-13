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
from new.utilities import normalize_date_freq, interp_dates_row
from collections import defaultdict
from pandera.errors import SchemaError
from uw import underground_widrawal
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
lista_n = []
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
                                          cols_fill_na=cols_fills_na,
                                          method_no_cols="ffill",
                                          )
    try:
        prod_vector = ProdVector(
            freq=EXPECTED_FREQ,
            data=group_prod_norm
        )
        # In case where wells don't have pressure info

    except SchemaError as e:
        expected_error_msg = 'ValueError("Need at least 3 dates to infer frequency")'
        if str(e) == expected_error_msg:
            # group_prod_norm = group_prod_norm.asfreq(EXPECTED_FREQ)
            group_prod_norm.index.freq = EXPECTED_FREQ
            prod_vector = ProdVector(
                freq=None,
                data=group_prod_norm
            )
    press_vector = None
    # Check if there's pressure data available for this well
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

    # Creating Well object with both production and pressure data
    info_well = Well(
        name=name,
        prod_data=prod_vector,
        press_data=press_vector
    )

    tank_wells[group_prod_norm[TANK_COL].iloc[0]].append(info_well)

"Underground Withdrawal"
"""for tank, wells in tank_wells.items():
    for well in wells:
        press_vector = well.press_data
        prod_vector = well.prod_data
        if press_vector is not None:
            for col in [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]:
                prod_vector.data[DATE_COL] = prod_vector.data.index
                prod_vector.data[WELL_COL] = well.name
                press_vector.data[DATE_COL] = press_vector.data.index
                press_vector.data[WELL_COL] = well.name
                press_vector.data[col] = press_vector.data.apply(
                    lambda x: interp_dates_row(
                        x, DATE_COL, prod_vector.data, DATE_COL, col, WELL_COL, WELL_COL, left=0.0
                    ),
                    axis=1,
                )
                press_vector.data[col].fillna(0, inplace=True)
                prod_vector.data.drop([DATE_COL, WELL_COL], axis=1, inplace=True)
                press_vector.data.drop([DATE_COL, WELL_COL], axis=1, inplace=True)

            press_vector.data["UW"] = underground_widrawal(press_vector)

            lista_v.append(well.name)

        else:
            lista_n.append(well.name)

print(lista_v)
print(lista_n)"""
