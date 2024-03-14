# %%
import pandas as pd
from new.constants import OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM
from new.vector_data import ProdVector
from new.well import Well

# Data to process
df_production = pd.read_csv("../old/tests/data_for_tests/full_example_1/prueba.csv")
df_production["START_DATETIME"] = pd.to_datetime(df_production["START_DATETIME"])

df_production.set_index(df_production["START_DATETIME"], inplace=True)
prod_wells = []

# Group data by well name and apply the function to create ProdWell objects
for name, group in df_production.groupby("ITEM_NAME"):
    print(f"Creating well {name}")

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
        data=group[[OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM]],
    )

    # Create rates colums
    oil_rates = prod_vector.calculate_rate(OIL_CUM_COL)
    water_rates = prod_vector.calculate_rate(WATER_CUM_COL)
    prod_vector.data["OIL_RATE"] = oil_rates
    prod_vector.data["WATER_RATE"] = water_rates

    # Create the well
    prod_well = Well(
        name=name,
        vector_data=prod_vector,
    )
    prod_wells.append(prod_well)

print(prod_wells)
