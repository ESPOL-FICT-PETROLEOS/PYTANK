# %%
import pandas as pd
from new.constants import OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM
from new.vector_data import ProdVector
from new.well import ProdWell


def create_prod_well(name, data):
    oil_cum_col = name + "_OCP"
    water_cum_col = name + "_WCP"
    gas_cum_col = name + "GCP"

    rename_dict = {
        oil_cum_col: OIL_CUM_COL,
        water_cum_col: WATER_CUM_COL,
        gas_cum_col: GAS_CUM_COL,
    }

    prod_well_data = data.rename(rename_dict, axis=1)
    prod_well_data[LIQ_CUM] = (
        prod_well_data[OIL_CUM_COL] + prod_well_data[WATER_CUM_COL]
    )

    prod_vector = ProdVector(freq="MS", data=prod_well_data)
    prod_well = ProdWell(name=name, vector_data=prod_vector)
    return prod_well


# Data to process
df_production = pd.read_csv("old/tests/data_for_tests/full_example_1/production.csv")
df_production["START_DATETIME"] = pd.to_datetime(df_production["START_DATETIME"])

# Group data by well name and apply the function to create ProdWell objects
prod_wells = [
    create_prod_well(name, data)
    for name, data in df_production.groupby("ITEM_NAME")[
        ["OIL_CUM", "WATER_CUM", "GAS_CUM"]
    ]
]

# Now 'prod_wells' contains a list of ProdWell objects
print(prod_wells)
