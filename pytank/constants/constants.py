"""
constants.py

This archive.py containing the constant or columns names used in some methods
and classes in the library

libraries:
    - pandera
"""
from pandera import Column, Check, DataFrameSchema

# Constants of DataFrames
DATE_COL = "START_DATETIME"
PRESSURE_COL = "PRESSURE_DATUM"
PRESSURE_PVT_COL = "Pressure"
TANK_COL = "Tank"
WELL_COL = "WELL_BORE"
OIL_CUM_COL = "OIL_CUM"
OIL_VOL_COL = "OIL_VOL"
WATER_CUM_COL = "WATER_CUM"
GAS_CUM_COL = "GAS_CUM"
LIQ_CUM = "LIQ_CUM"
OIL_FVF_COL = "Bo"
UO_COL = "uo"
GAS_FVF_COL = "Bg"
RS_COL = "GOR"
INJECTION_WATER = "WATER_VOL"
INFLUX_WATER = "We"
RS_W_COL = "RS_bw"
WATER_FVF_COL = "Bw"
UW_COL = "UW"
OIL_EXP = "Eo"
RES_EXP = "Efw"
OIL_CUM_TANK = "OIL_CUM_TANK"
WATER_CUM_TANK = "WATER_CUM_TANK"
GAS_CUM_TANK = "GAS_CUM_TANK"
WE = "Cumulative We"
OIL_RATE_COL = "OIL_RATE"
WATER_RATE_COL = "WATER_RATE"

# Frequency's of time
VALID_FREQS = ["D", "W", "M", "MS", "Q", "Y", None]

# VALIDATIONS:
_VECTOR_VALIDATION = Column(
    float,
    Check(lambda s: s >= 0),
    coerce=True,
    nullable=False,
)

_PRESSURE_VALIDATION = Column(float,
                              Check(lambda s: s >= 0),
                              coerce=True,
                              nullable=False,
                              required=False)

_STR_VALIDATION = Column(str,
                         Check(lambda s: s == s),
                         coerce=True,
                         nullable=False)

# SCHEMAS DICTIONARIES:
_PROD_SCHEMA_DICT = {
    OIL_CUM_COL: _VECTOR_VALIDATION,
    WATER_CUM_COL: _VECTOR_VALIDATION,
    GAS_CUM_COL: _VECTOR_VALIDATION,
    LIQ_CUM: _VECTOR_VALIDATION,
}

_PRESS_SCHEMA_DICT = {
    PRESSURE_COL: _PRESSURE_VALIDATION,
}

_INJ_SCHEMA_DICT = {INJECTION_WATER: _VECTOR_VALIDATION}

# SCHEMAS:
PROD_SCHEMA = DataFrameSchema(_PROD_SCHEMA_DICT, strict="filter")
PRESS_SCHEMA = DataFrameSchema(_PRESS_SCHEMA_DICT, strict="filter")
INJ_SCHEMA = DataFrameSchema(_INJ_SCHEMA_DICT, strict="filter")
