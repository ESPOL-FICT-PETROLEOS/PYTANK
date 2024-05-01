from pandera import Column, Check, DataFrameSchema, String

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
GAS_FVF_COL = "Bg"
UO_COL= "uo"
RS_COL = "GOR"
INJECTION_WATER = "WATER_VOL"
INFLUX_WATER = "We"


VALID_FREQS = ["D", "W", "M", "MS", "Q", "Y", None]

# Validations
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


# Schemas dictionaries
_PROD_SCHEMA_DICT = {
    PRESSURE_COL: _PRESSURE_VALIDATION,
    OIL_CUM_COL: _VECTOR_VALIDATION,
    WATER_CUM_COL: _VECTOR_VALIDATION,
    GAS_CUM_COL: _VECTOR_VALIDATION,
    LIQ_CUM: _VECTOR_VALIDATION,
}

_PRESS_SCHEMA_DICT = {
    PRESSURE_COL: _PRESSURE_VALIDATION,
}

_INJ_SCHEMA_DICT = {
    INJECTION_WATER: _VECTOR_VALIDATION,
}

_PVT_TABLE_SCHEMA_DICT = {
    Column(PRESSURE_PVT_COL): float,
    Column(RS_COL): float,
    Column(OIL_FVF_COL): float,
    Column(UO_COL): float,
    Column(GAS_FVF_COL): float,
}

# Schemas
PROD_SCHEMA = DataFrameSchema(_PROD_SCHEMA_DICT, strict="filter")
PRESS_SCHEMA = DataFrameSchema(_PRESS_SCHEMA_DICT, strict="filter")
INJ_SCHEMA = DataFrameSchema(_INJ_SCHEMA_DICT, strict="filter")
PVT_TABLE_SCHEMA = DataFrameSchema(_PVT_TABLE_SCHEMA_DICT, strict="filter")