import pandas as pd
from pydantic import BaseModel
from typing import Optional
from pytank.constants.constants import (OIL_CUM_COL,
                                        WATER_CUM_COL,
                                        GAS_CUM_COL,
                                        LIQ_CUM,
                                        PRESSURE_COL,
                                        TANK_COL,
                                        DATE_COL
                                        )
from pytank.vector_data.vector_data import ProdVector, PressVector
from pandera.errors import SchemaError
from pytank.functions.utilities import normalize_date_freq
import warnings


class CreateWell(BaseModel):
    name: str
    tank: Optional[str] = None
    prod_data: Optional[ProdVector] = None
    press_data: Optional[PressVector] = None


class Well(BaseModel):
    freq_prod: Optional[str] = None
    freq_press: Optional[str] = None
    df_prod: pd.DataFrame = None
    df_press: pd.DataFrame = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, df_prod: pd.DataFrame, df_press: pd.DataFrame, freq_prod=None, freq_press=None) -> None:
        super().__init__(df_prod=df_prod, df_press=df_press, freq_prod=freq_prod, freq_press=freq_press)

    def process_data(self):
        prod_data = self.df_prod
        prod_data[DATE_COL] = pd.to_datetime(prod_data[DATE_COL])
        prod_data.set_index(prod_data[DATE_COL],inplace=True)

        press_data = self.df_press
        press_data[DATE_COL] = pd.to_datetime(press_data["DATE"])
        press_data = press_data.drop("DATE", axis=1)

        return prod_data, press_data

    def get_wells(self):
        prod_data, press_data = self.process_data()
        cols_fills_na = [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM, TANK_COL]
        all_wells = set(prod_data["ITEM_NAME"]).union(press_data["WELLBORE"])
        tank_wells = []

        for name in all_wells:
            prod_vector = None
            press_vector = None

            if name in prod_data["ITEM_NAME"].unique():
                group_prod = prod_data[prod_data["ITEM_NAME"] == name]

                group_prod = group_prod.rename(
                    columns={
                        OIL_CUM_COL: OIL_CUM_COL,
                        WATER_CUM_COL: WATER_CUM_COL,
                        GAS_CUM_COL: GAS_CUM_COL,
                        TANK_COL: TANK_COL
                    }
                )
                group_prod[LIQ_CUM] = group_prod[OIL_CUM_COL] + group_prod[WATER_CUM_COL]
                group_prod = group_prod[[OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM, TANK_COL]]

                if self.freq_prod is not None:
                    group_prod_norm = normalize_date_freq(df=group_prod,
                                                          freq=self.freq_prod,
                                                          cols_fill_na=cols_fills_na,
                                                          method_no_cols="ffill")
                    try:
                        prod_vector = ProdVector(
                            freq=self.freq_prod,
                            data=group_prod_norm
                        )
                    except SchemaError as e:
                        expected_error_msg = 'ValueError("Need at least 3 dates to infer frequency")'
                        if str(e) == expected_error_msg:
                            group_prod.index.freq = self.freq_prod
                            prod_vector = ProdVector(
                                freq=None,
                                data=group_prod_norm
                            )
                    tank_name = group_prod_norm[TANK_COL].iloc[0]

                else:
                    prod_vector = ProdVector(
                        freq=self.freq_prod,
                        data=group_prod
                    )
                    tank_name = group_prod[TANK_COL].iloc[0]

            if name in press_data["WELLBORE"].unique():
                group_press = press_data[press_data["WELLBORE"] == name]

                group_press = group_press.rename(
                    columns={
                        PRESSURE_COL: PRESSURE_COL,
                    }
                )
                group_press.set_index(DATE_COL, inplace=True)
                press_vector = PressVector(
                    freq=self.freq_press,
                    data=group_press
                )
                if prod_vector is None and TANK_COL in group_press.columns:
                    tank_name = group_press[TANK_COL].iloc[0]

            info_well = CreateWell(
                name=name,
                tank=tank_name,
                prod_data=prod_vector,
                press_data=press_vector
            )

            tank_wells.append(info_well)

        return tank_wells

