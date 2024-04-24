import pandas as pd
from pydantic import BaseModel
from old.utilities.pvt_interp import interp_pvt_matbal
from scipy.interpolate import interp1d
from well import Well
from new.vector_data import VectorData, ProdVector, InjVector, PressVector
from typing import Optional


class FluidModel(BaseModel):
    data_pvt: pd.DataFrame
    data_press: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True

    def interp_table(self) -> pd.DataFrame:
        df_pvt = self.data_pvt
        df_press = self.data_press

        # Names of columns
        oil_fvf_col = "Bo"
        gas_fvf_col = "Bg"
        gas_oil_rs_col = "GOR"

        # Interpolated
        oil_fvf_interp = interp1d(df_pvt["Pressure"], df_pvt["Bo"], fill_value="extrapolate")
        gas_fvf_interp = interp1d(df_pvt["Pressure"], df_pvt["Bg"], fill_value="extrapolate")
        gas_oil_rs_interp = interp1d(df_pvt["Pressure"], df_pvt["GOR"], fill_value="extrapolate")

        # Apply the functions to pressure data
        df_press[oil_fvf_col] = oil_fvf_interp(df_press["PRESSURE_DATUM"])
        df_press[gas_fvf_col] = gas_fvf_interp(df_press["PRESSURE_DATUM"])
        df_press[gas_oil_rs_col] = gas_oil_rs_interp(df_press["PRESSURE_DATUM"])

        return df_press

    def get_bo_at_press(self, pressure):
        pass

    def get_bg_at_press(self, pressure):
        pass

    def get_rs_at_press(self, pressure):
        pass

