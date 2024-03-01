from pandera import Column, Check, DataFrameSchema

date_col = "DATE"
press_col = "PRESSURE"
oil_cum_col = "OIL_CUM"
water_cum_col = "WATER_CUM"
gas_cum_col = "GAS_CUM"
oil_fvf_col = "Bo"
gas_fvf_col = "Bg"
injection_water = "WATER_VOL"
influx_water = "We"

# Frequency's of time
VALID_FREQS = ["D", "W", "M", "MS", "Q", "Y"]

_VECTOR_RATE_COL_VALIDATION = Column(
    float,
    Check(lambda s: s >= 0),
    coerce=True,
    nullable=False,
)

"""_PRESSURE_COL_VALIDATION = Column(
    float,
    Check(lambda s: s >= 0),
    coerce=True,
    nullable=False,
)
"""

_PROD_SCHEMA_DICT = {
    oil_cum_col: _VECTOR_RATE_COL_VALIDATION,
    water_cum_col: _VECTOR_RATE_COL_VALIDATION,
}

_INJ_SCHEMA_DICT = {injection_water: _VECTOR_RATE_COL_VALIDATION}

PROD_SCHEMA = DataFrameSchema(_PROD_SCHEMA_DICT, strict="filter")
INJ_SCHEMA = DataFrameSchema(_INJ_SCHEMA_DICT, strict="filter")
