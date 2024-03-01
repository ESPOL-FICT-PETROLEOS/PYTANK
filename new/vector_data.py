from datetime import datetime
import pandas as pd
from typing import Any
from pydantic import BaseModel, validator, PrivateAttr
from pandera import DataFrameSchema
import pandera as pa
from model.utilities import add_date_index_validation, add_bhp_validation
from new.constants import (
    PROD_SCHEMA,
    INJ_SCHEMA,
    date_col,
    press_col,
    oil_cum_col,
    water_cum_col,
    gas_cum_col,
    oil_fvf_col,
    injection_water,
    influx_water,
)
import matplotlib.pyplot as plt
import numpy as np

class VectorData(BaseModel):
    is_result: bool = False
    data_schema: DataFrameSchema = DataFrameSchema()
    freq: str
    data: Any
    use_pressure: bool = False

    class Config:
        arbitrary_types_allowed = True


class ProdVectorData:
    def __init__(self, data: Any):
        self.data = data


    def get_oil_prod_rate(self) -> pd.Series:

