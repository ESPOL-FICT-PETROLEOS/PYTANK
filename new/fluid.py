import numpy as np
import pandas as pd
from typing import Optional, Callable
from pydantic import BaseModel
from scipy.interpolate import interp1d
import pandera as pa
from pandera.typing import DataFrame, Series
from new.constants import (PRESSURE_PVT_COL,
                           OIL_FVF_COL,
                           GAS_FVF_COL,
                           RS_COL
                           )


class PVTSchema(pa.DataFrameModel):
    Pressure: Series[float] = pa.Field(ge=0, unique=True, coerce=True, nullable=False)
    Bo: Series[float] = pa.Field(ge=0, coerce=True)
    Bg: Series[float] = pa.Field(ge=0, coerce=True, nullable=True)
    GOR: Series[float] = pa.Field(ge=0, coerce=True)


class OilModel(BaseModel):
    data_pvt: DataFrame[PVTSchema]
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


# %%
# Quicktest for validation
df_pvt_inv = pd.DataFrame({
    PRESSURE_PVT_COL: [100.0, 200, 300],
    OIL_FVF_COL: [10, 20, 30],
    GAS_FVF_COL: [1, 2, 45],
    RS_COL: [10.3, 34, 50],
})

validation = OilModel(
    data_pvt=df_pvt_inv,
    temperature=25
)

# %%
# Quicktest for some method
df_pvt = pd.read_csv("../old/tests/data_for_tests/full_example_1/pvt.csv")
fluid = OilModel(
    data_pvt=df_pvt,
    temperature=25
)

print(f"Bo is: {fluid.get_bo_at_press(np.array([100,200,300]))}")
print(f"Bg is: {fluid.get_bg_at_press(100)}")
print(f"GOR is: {fluid.get_rs_at_press(100)}")

#%%
class WaterModel(BaseModel):
    correlation_bw: Callable
    correlation_rs: Callable
    salinity: float
    temperature: float
    unit: float

    def interp_table(self) -> pd.DataFrame:
        pass

    def get_bw_at_press(self, pressure: float) -> float:
        bw = self.correlation_bw(pressure, self.temperature, self.salinity, self.unit)
        return bw

    def get_rs_at_press(self, pressure: float) -> float:
        rs = self.correlation_rs(pressure, self.temperature, self.salinity, self.unit)
        return rs


class FluidModel(BaseModel):
    oil: OilModel
    water: WaterModel

