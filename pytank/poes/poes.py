import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series
from matplotlib import pyplot as plt
from pydantic import BaseModel
from scipy import stats


class _DFMbalSchema(pa.DataFrameModel):
    Tank: Series[str] = pa.Field(nullable=False)
    START_DATETIME: Series[pd.Timestamp] = pa.Field(nullable=False)
    PRESSURE_DATUM: Series[float] = pa.Field(nullable=False)
    OIL_CUM_TANK: Series[float] = pa.Field(nullable=False)
    WATER_CUM_TANK: Series[float] = pa.Field(nullable=False)
    GAS_CUM_TANK: Series[float] = pa.Field(nullable=False)
    Bo: Series[float] = pa.Field(nullable=False)
    Bg: Series[float] = pa.Field(nullable=True)
    GOR: Series[float] = pa.Field(nullable=False)
    Time_Step: Series[float] = pa.Field(nullable=False)


class POES(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    we_df: pd.DataFrame = None
    mbal_df: DataFrame[_DFMbalSchema]

    def campbell(self, f: str, eo: str, efw: str, np: float):
        y = self.mbal_df[f] / (self.mbal_df[eo] + self.mbal_df[efw])
        x = self.mbal_df[np]
        data = pd.DataFrame({"Np": x, "F/Eo+Efw": y})
        fig, ax1 = plt.subplots()
        ax1.plot(x, y)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("F/Eo+Efw")
        ax1.set_title("Campbell plot")
        plt.show()
        return data

    def havlena_odeh(self, f: str, eo: str, efw: str, we: str):
        y = self.mbal_df[f] - self.we_df[we]
        x = self.mbal_df[eo] + self.mbal_df[efw]
        data = pd.DataFrame({"Eo+Efw": x, "F-Wwe": y})
        slope, intercept, r, p, se = stats.linregress(data["Eo+Efw"], data["F-Wwe"])
        print(f"N [MMStb]: {slope / 1000000:.4f}")
        fig, ax1 = plt.subplots()
        ax1.scatter(data["Eo+Efw"], data["F-Wwe"], color="blue")
        reg_line = (slope * data["Eo+Efw"]) + intercept
        ax1.plot(data["Eo+Efw"], reg_line, color="red", label="Regression line")
        ax1.set_xlabel("Eo+Efw")
        ax1.set_ylabel("F")
        ax1.set_title("Havlena_Odeh plot")
        plt.show()
        return data
