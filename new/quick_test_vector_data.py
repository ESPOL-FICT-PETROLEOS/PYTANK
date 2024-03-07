import pandas as pd
from new.vector_data import VectorData, ProdVector, InjVector
from new.constants import (
    OIL_CUM_COL,
    WATER_CUM_COL,
    GAS_CUM_COL,
    LIQ_CUM,
    PRESSURE_COL,
    DATE_COL,
    INJECTION_WATER
)

# %% Create a sample pandas dataframe with 2 columns and a DateTimeIndex with MS
# frequency
date_index_prod = pd.date_range("2020-01-01", periods=5, freq="MS")
df_prod = (
    pd.DataFrame(
        {
            OIL_CUM_COL: [1, 5, 13, 35, 89],
            WATER_CUM_COL: [10, 20, 30, 40, 50],
            GAS_CUM_COL: [100, 200, 300, 400, 500],
            DATE_COL: date_index_prod,
        }
    ).set_index(DATE_COL)
    .assign(
        **{
            LIQ_CUM: lambda x: x[OIL_CUM_COL]
            + x[WATER_CUM_COL]
        }
    )
)
# %% Create sample df for injection
date_index_inj = pd.date_range("2020-01-01", periods=5, freq="D")
df_inj = pd.DataFrame(
    {
        INJECTION_WATER: [1, 2, 3, 4, 5],
        DATE_COL: date_index_inj,
    }
).set_index(DATE_COL)
# %% Production vector data
prod_vector_data = ProdVector(freq="MS", data=df_prod)
oil_cum = prod_vector_data
water_cum = prod_vector_data
print(prod_vector_data.cal_day())
