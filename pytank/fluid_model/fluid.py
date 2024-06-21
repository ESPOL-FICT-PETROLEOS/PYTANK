from typing import Callable
from pydantic import BaseModel
from scipy.interpolate import interp1d
import pandera as pa
from pandera.typing import DataFrame, Series
from pytank.constants.constants import (PRESSURE_PVT_COL,
                                        OIL_FVF_COL,
                                        GAS_FVF_COL,
                                        RS_COL
                                        )
from pytank.functions.pvt_correlations import RS_bw, Bo_bw, Rs_McCain


class _PVTSchema(pa.DataFrameModel):
    Pressure: Series[float] = pa.Field(ge=0, unique=True, coerce=True, nullable=False)
    Bo: Series[float] = pa.Field(ge=0, coerce=True)
    Bg: Series[float] = pa.Field(ge=0, coerce=True, nullable=True)
    GOR: Series[float] = pa.Field(ge=0, coerce=True)


class OilModel(BaseModel):
    data_pvt: DataFrame[_PVTSchema]
    temperature: float

    class Config:
        arbitrary_types_allowed = True

    def _interpolated_column_at_pressure(self, column_name: str, pressure: float) -> float:
        df_pvt_local = self.data_pvt
        interp_func = interp1d(df_pvt_local[PRESSURE_PVT_COL], df_pvt_local[column_name], fill_value="extrapolate")
        return interp_func(pressure)

    def get_bo_at_press(self, pressure) -> float:
        return self._interpolated_column_at_pressure(OIL_FVF_COL, pressure)

    def get_bg_at_press(self, pressure) -> float:
        return self._interpolated_column_at_pressure(GAS_FVF_COL, pressure)

    def get_rs_at_press(self, pressure) -> float:
        return self._interpolated_column_at_pressure(RS_COL, pressure)


#%%
class WaterModel(BaseModel):
    salinity: float = None
    temperature: float = None
    unit: float = None

    def get_bw_at_press(self, pressure: float) -> float:
        bw = Bo_bw(pressure, self.temperature, self.salinity, self.unit)
        return bw

    def get_rs_at_press(self, pressure: float) -> float:
        rs = RS_bw(pressure, self.temperature, self.salinity, self.unit)
        # rs = Rs_McCain(pressure, self.temperature, self.salinity)
        return rs

    def get_default_bw(self) -> float:
        return float(1)

    def get_default_rs(self) -> float:
        return float(0)


