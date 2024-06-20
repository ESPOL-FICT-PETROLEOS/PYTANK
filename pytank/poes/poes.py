import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series
from matplotlib import pyplot as plt
from pydantic import BaseModel
from scipy import stats
from pytank.constants.constants import (UW_COL,
                                        OIL_EXP,
                                        RES_EXP,
                                        OIL_CUM_TANK,
                                        WE)


class _DFMbalSchema(pa.DataFrameModel):
    Tank: Series[str] = pa.Field(nullable=False)
    START_DATETIME: Series[pd.Timestamp] = pa.Field(nullable=False)
    PRESSURE_DATUM: Series[float] = pa.Field(nullable=False)
    OIL_CUM_TANK: Series[float] = pa.Field(nullable=False)
    WATER_CUM_TANK: Series[float] = pa.Field(nullable=False)
    GAS_CUM_TANK: Series[float] = pa.Field(nullable=False)
    Bo: Series[float] = pa.Field(nullable=False)
    Bg: Series[float] = pa.Field(nullable=True)
    RS_bw: Series[float] = pa.Field(nullable=False)
    Bw: Series[float] = pa.Field(nullable=False)
    GOR: Series[float] = pa.Field(nullable=False)
    Time_Step: Series[float] = pa.Field(nullable=False)
    UW: Series[float] = pa.Field(nullable=False)
    Eo: Series[float] = pa.Field(nullable=False)
    Efw: Series[float] = pa.Field(nullable=False)


class POES(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    we_df: pd.DataFrame = None
    mbal_df: DataFrame[_DFMbalSchema]

    def campbell(self):
        y = self.mbal_df[UW_COL] / (self.mbal_df[OIL_EXP] + self.mbal_df[RES_EXP])
        x = self.mbal_df[OIL_CUM_TANK]
        data = pd.DataFrame({"Np": x, "F/Eo+Efw": y})

        # Graphic
        fig, ax1 = plt.subplots()
        ax1.scatter(x, y)
        ax1.set_xlabel("Np Cumulative Oil Production [MMStb]")
        ax1.set_ylabel("F/Eo+Efw")
        ax1.set_title(f"Campbell plot of " + str(self.mbal_df["Tank"][0].replace("_", " ")))
        plt.show()
        return data

    def havlena_odeh(self):
        y = self.mbal_df[UW_COL] / (self.mbal_df[OIL_EXP] + self.mbal_df[RES_EXP])
        x = self.we_df[WE] / (self.mbal_df[OIL_EXP] + self.mbal_df[RES_EXP])
        data = pd.DataFrame({"WeBw/Eo+Efw": x, "F/Eo+Efw": y})

        # Graphic
        slope, intercept, r, p, se = stats.linregress(data["WeBw/Eo+Efw"], data["F/Eo+Efw"])
        print(f"N [MMStb]: {intercept / 1000000:.4f}")
        fig, ax1 = plt.subplots()
        ax1.scatter(data["WeBw/Eo+Efw"], data["F/Eo+Efw"], color="blue")
        reg_line = (slope * data["WeBw/Eo+Efw"]) + intercept
        ax1.plot(data["WeBw/Eo+Efw"], reg_line, color="red", label="Regression line")
        ax1.set_xlabel("WeBw/Eo+Efw")
        ax1.set_ylabel("F/Eo+Efw")
        ax1.set_title("Havlena y Odeh plot of " + str(self.mbal_df["Tank"][0].replace("_", " ")))
        ax1.annotate(
            "N [MMStb]: {:.2f}".format(intercept / 1000000),
            xy=(3, 5),
            xytext=(4, 5)
        )
        ax1.legend()
        plt.grid(True)
        plt.show()
        return data

    def havlena_odeh2(self):
        y = self.mbal_df[UW_COL] - self.we_df[WE]
        x = self.mbal_df[OIL_EXP] + self.mbal_df[RES_EXP]
        data = pd.DataFrame({"Eo+Efw": x, "F-We": y})

        # Graphic
        slope, intercept, r, p, se = stats.linregress(data["Eo+Efw"], data["F-We"])
        print(f"N [MMStb]: {slope / 1000000:.4f}")
        fig, ax2 = plt.subplots()
        ax2.scatter(data["Eo+Efw"], data["F-We"], color="blue")
        reg_line = (slope * data["Eo+Efw"]) + intercept
        ax2.plot(data["Eo+Efw"], reg_line, color="red", label="Regression line")
        ax2.set_xlabel("Eo+Efw")
        ax2.set_ylabel("F-We")
        ax2.set_title("Havlena y Odeh plot of " + str(self.mbal_df["Tank"][0].replace("_", " ")))
        ax2.annotate(
            "N [MMStb]: {:.2f}".format(slope / 1000000),
            xy=(0.035, 0.2),
            xytext=(10, 3)
        )
        ax2.legend()
        plt.grid(True)
        plt.show()
        return data
