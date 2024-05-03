import pandas as pd
from pydantic import BaseModel
from old.utilities.pvt_interp import interp_pvt_matbal
from scipy.interpolate import interp1d
from new.vector_data import VectorData, ProdVector, InjVector, PressVector
from constants import (PRESSURE_PVT_COL,
                       OIL_FVF_COL,
                       GAS_FVF_COL,
                       RS_COL,
)


class FluidModel(BaseModel):
    data_pvt: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True

    def interp_table(self) -> pd.DataFrame:
        # Preguntar que iria aqui
        pass

    def get_bo_at_press(self, pressure) -> float:
        df_pvt = self.data_pvt
        oil_fvf_interp = interp1d(df_pvt[PRESSURE_PVT_COL], df_pvt[OIL_FVF_COL], fill_value="extrapolate")
        bo_interp = oil_fvf_interp(pressure)
        return bo_interp

    def get_bg_at_press(self, pressure) -> float:
        df_pvt = self.data_pvt
        gas_fvf_interp = interp1d(df_pvt[PRESSURE_PVT_COL], df_pvt[GAS_FVF_COL], fill_value="extrapolate")
        bg_interp = gas_fvf_interp(pressure)
        return bg_interp

    def get_rs_at_press(self, pressure) -> float:
        df_pvt = self.data_pvt
        gas_oil_rs_interp = interp1d(df_pvt[PRESSURE_PVT_COL], df_pvt[RS_COL], fill_value="extrapolate")
        gor_interp = gas_oil_rs_interp(pressure)
        return gor_interp


# QUICKTEST
# Data to process with pv.t info
df_pvt = pd.read_csv("../old/tests/data_for_tests/full_example_1/pvt.csv")
bo = FluidModel(
    data_pvt=df_pvt
).get_bo_at_press(1456)
print(bo)