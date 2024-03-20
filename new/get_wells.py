# %%
import pandas as pd
from new.constants import OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM, PRESSURE_COL
from new.vector_data import ProdVector, PressVector
from new.well import Well
from new.utilities import normalize_date_freq
from old.utilities import interp_dates_row

# Data to process
df_production = pd.read_csv("../old/tests/data_for_tests/full_example_1/production.csv")
df_production["START_DATETIME"] = pd.to_datetime(df_production["START_DATETIME"])

df_production.set_index(df_production["START_DATETIME"], inplace=True)
prod_wells = []

# Group data by well name and apply the function to create ProdWell objects
for name, group in df_production.groupby("ITEM_NAME"):
    #print(f"Creating well {name}")

    group = group.rename(
        columns={
            OIL_CUM_COL: OIL_CUM_COL,
            WATER_CUM_COL: WATER_CUM_COL,
            GAS_CUM_COL: GAS_CUM_COL,
        }
    )
    group[LIQ_CUM] = group[OIL_CUM_COL] + group[WATER_CUM_COL]

    prod_vector = ProdVector(
        freq=None,
        data=group
    )

    # Create rates colums
    oil_rates = prod_vector.calculate_rate(OIL_CUM_COL)
    water_rates = prod_vector.calculate_rate(WATER_CUM_COL)
    prod_vector.data["OIL_RATE"] = oil_rates
    prod_vector.data["WATER_RATE"] = water_rates

    # Interpolated dates
    date_interpo = normalize_date_freq(prod_vector.data,
                                       "MS",
                                       cols_fill_na=["OIL_RATE", "WATER_RATE"],
                                       method_no_cols="ffill")
    prod_vector.data = date_interpo

    # Calculate new rates based on interpolated dates
    prod_vector.data["OIL_RATE"] = prod_vector.calculate_rate(OIL_CUM_COL)
    prod_vector.data["WATER_RATE"] = prod_vector.calculate_rate(WATER_CUM_COL)

    # Create the well
    prod_well = Well(
        name=name,
        vector_data=prod_vector,
    )
    prod_wells.append(prod_well)


df_pressures = pd.read_csv("../old/tests/data_for_tests/full_example_1/pressures.csv")
df_pressures.rename(columns={"DATE":"START_DATETIME"}, inplace=True)
df_pressures["START_DATETIME"] = pd.to_datetime(df_pressures["START_DATETIME"])

df_pressures.set_index(df_pressures["START_DATETIME"], inplace=True)
pressures_wells = []


for name, group in df_pressures.groupby("WELLBORE"):
    print(f"Creating well pressures {name}")
    group = group.rename(
        columns={
            PRESSURE_COL: PRESSURE_COL
        }
    )
    press_vector = PressVector(
        freq=None,
        data=group
    )

    press_well = Well(
        name=name,
        vector_data=press_vector
    )
    pressures_wells.append(press_well)

print(pressures_wells)