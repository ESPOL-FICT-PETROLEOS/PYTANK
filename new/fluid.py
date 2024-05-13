import numpy as np
import pandas as pd
from typing import Optional, Callable
from pydantic import BaseModel, field_validator
from scipy.interpolate import interp1d
from constants import (PRESSURE_PVT_COL,
                       OIL_FVF_COL,
                       GAS_FVF_COL,
                       RS_COL,
                       )


class FluidModel(BaseModel):
    data_pvt: pd.DataFrame
    temperature: float

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def validate_data_pvt(cls, value):
        """Validate that the corresponding columns exist"""
        required_columns = {PRESSURE_PVT_COL, OIL_FVF_COL, GAS_FVF_COL, RS_COL}
        if not required_columns.issubset(value.columns):
            raise ValueError(f"DataFrame must have columns: {PRESSURE_PVT_COL}, "
                             f"{OIL_FVF_COL}, "
                             f" {GAS_FVF_COL}, "
                             f"{RS_COL}")

        """Validate the values found in each column of the DataFrame"""
        for column in value.columns:
            if not all(isinstance(val, (float, int)) and val >= 0 or np.isnan(val) for val in value[column]):
                raise ValueError(f"Invalid values in columns '{column}'")
        return value

    @field_validator("data_pvt")
    def check_data_pvt(cls, value):
        return cls.validate_data_pvt(value)

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

validation = FluidModel(
    data_pvt=df_pvt_inv,
    temperature=25
)

# %%
# Quicktest for some method
df_pvt = pd.read_csv("../old/tests/data_for_tests/full_example_1/pvt.csv")
fluid = FluidModel(
    data_pvt=df_pvt,
    temperature=25
)

#print(f"Bo is: {fluid.get_bo_at_press(np.array([100,200,300]))}")
#print(f"Bg is: {fluid.get_bg_at_press(100)}")
#print(f"GOR is: {fluid.get_rs_at_press(100)}")


# %%
# Working...
class OilFluidModel(FluidModel):
    specific_gravity: Optional[float] = None

    def interp_table(self) -> pd.DataFrame:
        pass

    def get_bo_at_press(self, pressure) -> float:
        pass

    def get_bg_at_press(self, pressure) -> float:
        pass

    def get_rs_at_press(self, pressure) -> float:
        pass

from old.utilities.pvt_correlations import RS_bw, Bo_bw
class WaterFluidModel(BaseModel):
    salinity: float = 3000
    correlation: Callable
    temperature: float = 220
    #unit: Optional[int] = 1

    def interp_table(self) -> pd.DataFrame:
        pass

    def get_bw_at_press(self, pressure: float, temperature: float, salinity: float, unit: int = 1) -> float:
        bw = self.correlation(pressure, temperature, salinity, unit)
        return bw

    def get_rs_at_press(self, pressure: float,temperature: float, salinity: float, unit: int = 1) -> float:
        rs = self.correlation(pressure, temperature, salinity, unit)
        return rs

from get_wells import tank_wells
tankc = tank_wells["tank_center"][0]
water = WaterFluidModel(correlation=Bo_bw)
print(water.get_bw_at_press(tankc.press_data.data,250,3000,unit=1))

class FullFluidModel(BaseModel):
    oil: OilFluidModel
    water: WaterFluidModel

