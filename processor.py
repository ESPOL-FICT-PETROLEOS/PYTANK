import pandas as pd
from new.constants import (
    OIL_CUM_COL,
    WATER_CUM_COL,
    LIQ_CUM,
    GAS_CUM_COL,
)
from new.vector_data import ProdVector, InjVector
from new.well import ProdWell

# Data to process
df_production = pd.read_csv("old/tests/data_for_tests/full_example_1/production.csv")
df_production["START_DATETIME"] = pd.to_datetime(df_production["START_DATETIME"])

# new_df_prod = df_production.to_csv("production.csv", index=False)

# df_prod = pd.read_csv("production.csv")
df_production.set_index(df_production["START_DATETIME"], inplace=True)
# prod = df_production[["ITEM_NAME", OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]]
# prod_well_names = set([col for col in df_production["ITEM_NAME"]])
prod_wells = []
OIL_CUM_NEW_COL = "OCP"
WATER_NEW_COL = "WCP"
GAS_NEW_COL = "GCP"
# %%
for name, group in df_production.groupby("ITEM_NAME"):
    print(f"Creating well {name}")
    # Get the data related to each well
    group = group.rename(
        columns={
            OIL_CUM_COL: OIL_CUM_NEW_COL,
            WATER_CUM_COL: WATER_NEW_COL,
            GAS_CUM_COL: GAS_NEW_COL,
        }
    )
    group[LIQ_CUM] = group[OIL_CUM_NEW_COL] + group[WATER_NEW_COL]

    # cumulative_data = group[[OIL_CUM_NEW_COL, WATER_NEW_COL, GAS_NEW_COL]].sum()
    # Create the Production vector
    prod_vector = ProdVector(
        freq="MS",
        data=group[[OIL_CUM_NEW_COL, WATER_NEW_COL, GAS_NEW_COL, LIQ_CUM]],
    )
    # Create the well
    prod_well = ProdWell(
        name=name,
        vector_data=prod_vector,
    )
    prod_wells.append(prod_well)

print(prod_wells)
