from pandera import Column, Check, DataFrameSchema

# Constants of DataFrames
DATE_COL = "START_DATETIME"
PRESSURE_COL = "PRESSURE"
WELL_COL = "WELL_BORE"
OIL_CUM_COL = "OIL_CUM"
WATER_CUM_COL = "WATER_CUM"
GAS_CUM_COL = "GAS_CUM"
LIQ_CUM = "LIQ_CUM"
# OIL_FVF_COL = "Bo"
# GAS_FVF_COL = "Bg"
INJECTION_WATER = "WATER_VOL"
# INFLUX_WATER = "We"
TANK_COL = "TANK"

# Frecuency's of time
VALID_FREQS = ["D", "W", "M", "MS", "Q", "Y", None]

_VECTOR_VALIDATION = Column(
    float,
    Check(lambda s: s >= 0),
    coerce=True,
    nullable=False,
)

_PRESSURE_VALIDATION = Column(
    float,
    Check(lambda s: s >= 0),
    coerce=True,
    nullable=False,
    required=False
)

_PROD_SCHEMA_DICT = {
    OIL_CUM_COL: _VECTOR_VALIDATION,
    WATER_CUM_COL: _VECTOR_VALIDATION,
    GAS_CUM_COL: _VECTOR_VALIDATION,
    LIQ_CUM: _VECTOR_VALIDATION,
    PRESSURE_COL: _PRESSURE_VALIDATION,
}

_INJ_SCHEMA_DICT = {INJECTION_WATER: _VECTOR_VALIDATION}

PROD_SCHEMA = DataFrameSchema(_PROD_SCHEMA_DICT, strict="filter")
INJ_SCHEMA = DataFrameSchema(_INJ_SCHEMA_DICT, strict="filter")
