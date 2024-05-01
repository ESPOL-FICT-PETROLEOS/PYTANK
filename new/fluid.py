import pandas as pd
from pydantic import BaseModel
from scipy.interpolate import interp1d
from vector_data import PvtVector

class FluidModel(BaseModel):
    data_pvt: PvtVector

    class Config:
        arbitrary_types_allowed = True

    def interp_table(self) -> pd.DataFrame:
        pass

    def get_bo_at_press(self, pressure):
        df_pvt = self.data_pvt
        oil_fvf_interp = interp1d(df_pvt["Pressure"], df_pvt["Bo"], fill_value="extrapolate")
        bo_interp = oil_fvf_interp(pressure)
        return bo_interp

    def get_bg_at_press(self, pressure):
        df_pvt = self.data_pvt
        gas_fvf_interp = interp1d(df_pvt["Pressure"], df_pvt["Bg"], fill_value="extrapolate")
        bg_interp = gas_fvf_interp(pressure)
        return bg_interp

    def get_gor_at_press(self, pressure):
        df_pvt = self.data_pvt
        gas_oil_rs_interp = interp1d(df_pvt["Pressure"], df_pvt["GOR"], fill_value="extrapolate")
        gor_interp = gas_oil_rs_interp(pressure)
        return gor_interp

df_pvt = pd.read_csv("../old/tests/data_for_tests/full_example_1/pvt.csv").fillna(0)

pvt = FluidModel(
    freq=None,
    data_pvt=df_pvt
)

print(pvt)

