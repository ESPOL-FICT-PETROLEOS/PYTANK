import pandas as pd
import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel
from pytank.constants.constants import (OIL_FVF_COL,
                                        GAS_FVF_COL,
                                        RS_COL,
                                        PRESSURE_COL,
                                        OIL_CUM_COL,
                                        GAS_CUM_COL,
                                        WATER_CUM_COL,
                                        DATE_COL,
                                        WELL_COL,
                                        WATER_FVF_COL,
                                        RS_W_COL,
                                        TANK_COL,
                                        LIQ_CUM,
                                        UW_COL,
                                        PRESSURE_PVT_COL,
                                        OIL_CUM_TANK,
                                        WATER_CUM_TANK,
                                        GAS_CUM_TANK,
                                        OIL_EXP,
                                        RES_EXP)
from pytank.fluid_model.fluid import OilModel, WaterModel
from pytank.functions.utilities import interp_dates_row
from pytank.functions.pvt_interp import interp_pvt_matbal
from pytank.functions.material_balance import underground_withdrawal, pressure_vol_avg, fw_expansion


class _PressSchema(pa.DataFrameModel):
    """
    Private Class to validate data of df_press_int method in Tank Class
    """
    PRESSURE_DATUM: Series[float] = pa.Field(nullable=False)
    WELL_BORE: Series[str] = pa.Field(nullable=False)
    START_DATETIME: Series[pd.Timestamp] = pa.Field(nullable=False)
    Bo: Series[float] = pa.Field(nullable=False)
    Bg: Series[float] = pa.Field(nullable=True)
    GOR: Series[float] = pa.Field(nullable=False)
    Bw: Series[float] = pa.Field(nullable=True)
    RS_bw: Series[float] = pa.Field(nullable=True)
    Tank: Series[str] = pa.Field(nullable=False)


class _ProdSchema(pa.DataFrameModel):
    """
    Private Class to validate data of df_prod_int method in Tank Class
    """
    OIL_CUM: Series[float] = pa.Field(nullable=False)
    WATER_CUM: Series[float] = pa.Field(nullable=False)
    GAS_CUM: Series[float] = pa.Field(nullable=False)
    LIQ_CUM: Series[float] = pa.Field(nullable=False)
    WELL_BORE: Series[str] = pa.Field(nullable=True)
    START_DATETIME: Series[pd.Timestamp] = pa.Field(nullable=False)
    Tank: Series[str] = pa.Field(nullable=False)


class Tank(BaseModel):
    tanks: dict
    name: str
    wells: list
    oil_model: OilModel
    water_model: WaterModel

    def __init__(self, tanks: dict, name: str, wells: list, oil_model: OilModel, water_model: WaterModel):
        super().__init__(tanks=tanks, name=name, wells=wells, oil_model=oil_model, water_model=water_model)

    def _press_df_int(self):
        """
        Private method that internally manages the pressure vector for use in the UW method

        Parameters
        ----------

        Returns
        -------
        A pressure DataFrame with properties PVT of oil and water
        """
        df_press = pd.DataFrame()
        for tank_name, wells in self.tanks.items():
            for well in wells:
                press_vector = well.press_data
                if press_vector is not None:
                    well_name = well.name
                    well_date = press_vector.data.index
                    well_oil_fvf = self.oil_model.get_bo_at_press(press_vector.data[PRESSURE_COL])
                    well_gas_fvf = self.oil_model.get_bg_at_press(press_vector.data[PRESSURE_COL])
                    well_rs = self.oil_model.get_rs_at_press(press_vector.data[PRESSURE_COL])

                    # In case properties are calculated using correlations
                    if (
                            self.water_model.salinity is not None
                            and self.water_model.temperature is not None
                            and self.water_model.unit is not None):
                        well_bw = self.water_model.get_bw_at_press(press_vector.data[PRESSURE_COL])
                        well_rs_w = self.water_model.get_rs_at_press(press_vector.data[PRESSURE_COL])

                    # In case there are default values for Bw and Rs_w
                    else:
                        well_bw = self.water_model.get_default_bw()
                        well_rs_w = self.water_model.get_default_rs()

                    # Create a copy of data from press_vector
                    temp_df_press = press_vector.data.copy()

                    # Add columns to DataFrame
                    temp_df_press[WELL_COL] = well_name
                    temp_df_press[DATE_COL] = well_date
                    temp_df_press[OIL_FVF_COL] = well_oil_fvf
                    temp_df_press[GAS_FVF_COL] = well_gas_fvf
                    temp_df_press[RS_COL] = well_rs
                    temp_df_press[WATER_FVF_COL] = well_bw
                    temp_df_press[RS_W_COL] = well_rs_w
                    temp_df_press[TANK_COL] = tank_name

                    df_press = pd.concat([df_press, temp_df_press], ignore_index=True)
        return df_press

    def _prod_df_int(self) -> pd.DataFrame:
        """
        Private method that internally manages production vector for use in the UW method

        Parameters
        ----------

        Returns
        -------
        A production DataFrame

        """
        df_prod = pd.DataFrame()
        for tank_name, wells in self.tanks.items():
            for well in wells:
                prod_vector = well.prod_data
                if prod_vector is not None:
                    well_name = well.name
                    well_date = prod_vector.data.index
                    well_oil_cum = prod_vector.data[OIL_CUM_COL]
                    well_water_cum = prod_vector.data[WATER_CUM_COL]
                    well_gas_cum = prod_vector.data[GAS_CUM_COL]
                    well_liq_cum = prod_vector.data[LIQ_CUM]

                    # Create a copy of data from prod_vector
                    temp_df_prod = prod_vector.data.copy()

                    temp_df_prod[WELL_COL] = well_name
                    temp_df_prod[DATE_COL] = well_date
                    temp_df_prod[OIL_CUM_COL] = well_oil_cum
                    temp_df_prod[WATER_CUM_COL] = well_water_cum
                    temp_df_prod[GAS_CUM_COL] = well_gas_cum
                    temp_df_prod[LIQ_CUM] = well_liq_cum
                    temp_df_prod[TANK_COL] = tank_name

                    df_prod = pd.concat([df_prod, temp_df_prod], ignore_index=True)
        return df_prod

    def calc_uw(self) -> pd.DataFrame:
        df_press = self._press_df_int()
        df_prod = self._prod_df_int()
        df_press = df_press.loc[df_press[TANK_COL] == self.name]

        # Validate df_press and df_prod
        df_press_validate = pd.DataFrame(_PressSchema.validate(df_press))
        df_prod_validate = pd.DataFrame(_ProdSchema.validate(df_prod))
        # df_prod = df_prod.loc[df_prod[TANK_COL]==self.name]

        # Calculate the accumulated production in the pressure dataframe, based on the production dataframe
        for col in [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]:
            df_press_validate[col] = df_press_validate.apply(
                lambda x: interp_dates_row(
                    x, DATE_COL, df_prod_validate, DATE_COL, col, WELL_COL, WELL_COL, left=0.0
                ),
                axis=1,
            )
            # For wells not available in the production data frame, fill nans with 0
            df_press_validate[col].fillna(0)

        uw_well = []
        for well, group in df_press_validate.groupby(WELL_COL):
            group[UW_COL] = underground_withdrawal(
                group,
                OIL_CUM_COL,
                WATER_CUM_COL,
                GAS_CUM_COL,
                OIL_FVF_COL,
                WATER_FVF_COL,
                GAS_FVF_COL,
                RS_COL,
                RS_W_COL,
            )
            uw_well.append(group)

        df_press_validate = pd.concat(uw_well, ignore_index=True)
        return df_press_validate

    def pressure_vol_avg(self, avg_freq: str, position: str) -> pd.DataFrame:
        df_press = self.calc_uw()
        df_press_avg = (
            df_press.groupby(TANK_COL).apply(
                lambda g: pressure_vol_avg(
                    g,
                    WELL_COL,
                    DATE_COL,
                    PRESSURE_COL,
                    UW_COL,
                    avg_freq,
                    position
                )
            ).reset_index(0)
        )
        return df_press_avg

    def mat_bal_df(self, avg_freq: str, position: str, swo: float, cw: float, cf: float, pi) -> pd.DataFrame:
        """
        Obtain material balance parameters at a certain frequency

        Parameters
        ----------
        avg_freq: str
            Frequency for averaging
        position: str
            Position for averaging

        Returns
        -------
        pd.DataFrame

            Dataframe with data to calculate material balance

        """
        avg = self.pressure_vol_avg(avg_freq, position)

        #  Validate df_prod from _prod_df_int
        prod = pd.DataFrame(_ProdSchema.validate(self._prod_df_int()))

        df_pvt = self.oil_model.data_pvt

        avg[PRESSURE_COL] = avg[PRESSURE_COL].interpolate(method="linear")

        cols_input = [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]
        cols_output = ["oil_vol", "water_vol", "gas_vol"]
        prod[cols_output] = (prod.groupby(WELL_COL)[cols_input]).diff().fillna(prod[cols_input])
        cols_group = [DATE_COL, TANK_COL, "oil_vol", "water_vol", "gas_vol"]
        df_tank = (
            prod[cols_group]
            .groupby(cols_group[0:2])
            .sum()
            .groupby(TANK_COL)
            .cumsum()
            .reset_index()
        )

        df_tank.rename(columns={
            "oil_vol": OIL_CUM_COL,
            "water_vol": WATER_CUM_COL,
            "gas_vol": GAS_CUM_COL
        }, inplace=True)

        oil_cum_per_tank = OIL_CUM_COL + "_TANK"
        water_cum_per_tank = WATER_CUM_COL + "_TANK"
        gas_cum_per_tank = GAS_CUM_COL + "_TANK"

        for col, cum_col in zip([oil_cum_per_tank, water_cum_per_tank, gas_cum_per_tank],
                                [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]):
            avg[col] = avg.apply(
                lambda g: interp_dates_row(
                    g, DATE_COL, df_tank, DATE_COL, cum_col, TANK_COL, TANK_COL
                ),
                axis=1
            )

        df_mbal = avg.sort_values(DATE_COL)

        for col, prop in zip([OIL_FVF_COL, GAS_FVF_COL, RS_COL],
                             [OIL_FVF_COL, GAS_FVF_COL, RS_COL]):
            df_mbal[col] = df_mbal[PRESSURE_COL].apply(
                lambda press: interp_pvt_matbal(df_pvt, PRESSURE_PVT_COL, prop, press)
            )

        if (
                self.water_model.salinity is not None
                and self.water_model.temperature is not None
                and self.water_model.unit is not None):
            df_mbal[WATER_FVF_COL] = self.water_model.get_bw_at_press(df_mbal[PRESSURE_COL])
            df_mbal[RS_W_COL] = self.water_model.get_rs_at_press(df_mbal[PRESSURE_COL])

        # In case there are default values for Bw and Rs_w
        else:
            df_mbal[WATER_FVF_COL] = self.water_model.get_default_bw()
            df_mbal[RS_W_COL] = self.water_model.get_default_rs()

        df_mbal["Time_Step"] = 365.0
        df_mbal.loc[df_mbal.index[1:], "Time_Step"] = (df_mbal[DATE_COL].diff().dt.days.iloc[1:]).cumsum() + 365.0

        df_mbal[UW_COL] = underground_withdrawal(df_mbal,
                                                 OIL_CUM_TANK,
                                                 WATER_CUM_TANK,
                                                 GAS_CUM_TANK,
                                                 OIL_FVF_COL,
                                                 WATER_FVF_COL,
                                                 GAS_FVF_COL,
                                                 RS_COL,
                                                 RS_W_COL)
        df_mbal[OIL_EXP] = df_mbal[OIL_FVF_COL] - self.oil_model.get_bo_at_press(pi)
        #df_mbal[OIL_EXP] = df_mbal[OIL_FVF_COL] - df_mbal[OIL_FVF_COL][0]
        df_mbal[RES_EXP] = fw_expansion(df_mbal,
                                        OIL_FVF_COL,
                                        PRESSURE_COL,
                                        swo,
                                        cw,
                                        cf,
                                        float(self.oil_model.get_bo_at_press(pi)),
                                        pi)
        #df_mbal[RES_EXP] = self.oil_model.get_bo_at_press(pi) * (((cw*swo)+cf) / (1-swo)) * (pi - df_mbal[PRESSURE_COL])
        return df_mbal

