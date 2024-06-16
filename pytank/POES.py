import pandas as pd
from matplotlib import pyplot as plt
from pydantic import BaseModel
from typing import Type
from scipy import stats
from pytank.constants.constants import (OIL_FVF_COL,
                                        GAS_FVF_COL,
                                        RS_COL,
                                        PRESSURE_COL,
                                        OIL_CUM_TANK,
                                        GAS_CUM_TANK,
                                        WATER_CUM_TANK,
                                        DATE_COL,
                                        WATER_FVF_COL,
                                        RS_W_COL,
                                        UW_COL,
                                        OIL_EXP,
                                        RES_EXP)
from pytank.functions.material_balance import underground_withdrawal, pressure_vol_avg, gas_expansion, oil_expansion, \
    fw_expansion, campbell_function
from pytank.aquifer.we import Aquifer

df = pd.read_csv("../tank/mbal_tank.csv")

we = pd.read_csv("../tank/we_tank.csv")
class POES(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    we_df: pd.DataFrame = None
    mbal_df: pd.DataFrame

    def Campbell(self, f: str, eo: str, efw: str, np: float ):
        y = self.mbal_df[f]/(self.mbal_df[eo]+self.mbal_df[efw])
        x = self.mbal_df[np]
        fig, ax1 = plt.subplots()
        ax1.plot(x, y)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("F/Eo+Efw")
        ax1.set_title("Campbell plot")
        plt.show()

    def havlena_odeh(self, f: str, eo: str, efw: str, we: str):
        y = self.mbal_df[f] - self.we_df[we]
        x = self.mbal_df[eo] + self.mbal_df[efw]
        fig, ax1 = plt.subplots()
        ax1.plot(x, y)
        ax1.set_xlabel("Eo+Efw")
        ax1.set_ylabel("F")
        ax1.set_title("Havlena_Odeh plot")
        plt.show()


poes = POES(mbal_df=df, we_df=we)
campbell = poes.Campbell(UW_COL, OIL_EXP, RES_EXP, OIL_CUM_TANK)


ho = poes.havlena_odeh(UW_COL, OIL_EXP, RES_EXP, "Cumulative We")
