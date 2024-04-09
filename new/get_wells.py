# %%
import pandas as pd
from new.constants import OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM, PRESSURE_COL, TANK_COL
from new.vector_data import ProdVector, PressVector, VectorData
from new.well import Well
from new.utilities import normalize_date_freq
from old.utilities import interp_dates_row
from collections import defaultdict

# Data to process with production info
df_production = pd.read_csv("../old/tests/data_for_tests/full_example_1/production.csv")
df_production["START_DATETIME"] = pd.to_datetime(df_production["START_DATETIME"])
df_production.set_index(df_production["START_DATETIME"], inplace=True)

# Data to process with pressure info
df_pressures = pd.read_csv("../old/tests/data_for_tests/full_example_1/pressures.csv")
df_pressures.rename(columns={"DATE": "START_DATETIME", "WELLLBORE": "ITEM_NAME"}, inplace=True)
df_pressures["START_DATETIME"] = pd.to_datetime(df_pressures["START_DATETIME"])
df_pressures.set_index(df_pressures["START_DATETIME"], inplace=True)

# Empty list for the different wells
prod_wells = []

# Empty dictionary for the different tanks
tank_wells = defaultdict(list)

# Group data by well name and apply the function to create ProdWell objects
for name, group in df_production.groupby("ITEM_NAME"):
    print(f"Creating well {name}")

    group = group.rename(
        columns={
            OIL_CUM_COL: OIL_CUM_COL,
            WATER_CUM_COL: WATER_CUM_COL,
            GAS_CUM_COL: GAS_CUM_COL
        }
    )
    group[LIQ_CUM] = group[OIL_CUM_COL] + group[WATER_CUM_COL]

    group_norm = normalize_date_freq(group,
                                     freq="MS",
                                     method_no_cols="ffill"
                                    )
    prod_vector = ProdVector(
        freq="MS",
        data=group_norm
    )

    prod_well = Well(
        name=name,
        prod_data=prod_vector
    )
    prod_wells.append(prod_well)



