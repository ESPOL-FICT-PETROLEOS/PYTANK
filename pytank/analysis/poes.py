import pandas as pd
import pandera as pa
from pandera.typing import Series
from matplotlib import pyplot as plt
from pydantic import BaseModel
from scipy import stats
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
                                        UW_COL,
                                        PRESSURE_PVT_COL,
                                        OIL_CUM_TANK,
                                        WATER_CUM_TANK,
                                        GAS_CUM_TANK,
                                        OIL_EXP,
                                        RES_EXP,
                                        WE)
from pytank.functions.utilities import interp_dates_row
from pytank.functions.pvt_interp import interp_pvt_matbal
from pytank.functions.material_balance import underground_withdrawal, pressure_vol_avg, ho_terms_equation
from pytank.tank.tank import Tank, _PressSchema, _ProdSchema
from pytank.aquifer.aquifer_model import Fetkovich, Carter_Tracy


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


class Analysis(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    tank_class: Tank
    freq: str
    position: str

    def __init__(self, tank_class, freq, position):
        super().__init__(tank_class=tank_class, freq=freq, position=position)

    def _calc_uw(self) -> pd.DataFrame:
        df_press = self.tank_class._press_df_int()
        df_prod = self.tank_class._prod_df_int()
        df_press = df_press.loc[df_press[TANK_COL] == self.tank_class.name]

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

    def _pressure_vol_avg(self) -> pd.DataFrame:
        df_press = self._calc_uw()
        df_press_avg = (
            df_press.groupby(TANK_COL).apply(
                lambda g: pressure_vol_avg(
                    g,
                    WELL_COL,
                    DATE_COL,
                    PRESSURE_COL,
                    UW_COL,
                    self.freq,
                    self.position
                )
            ).reset_index(0)
        )
        return df_press_avg

    def mat_bal_df(self) -> pd.DataFrame:
        """
        Obtain material balance parameters at a certain frequency

        Returns
        -------
        pd.DataFrame
        """
        avg = self._pressure_vol_avg()

        #  Validate df_prod from _prod_df_int
        prod = pd.DataFrame(_ProdSchema.validate(self.tank_class._prod_df_int()))

        df_pvt = self.tank_class.oil_model.data_pvt

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

        # Interpolated Cumulative production
        for col, cum_col in zip([oil_cum_per_tank, water_cum_per_tank, gas_cum_per_tank],
                                [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]):
            avg[col] = avg.apply(
                lambda g: interp_dates_row(
                    g, DATE_COL, df_tank, DATE_COL, cum_col, TANK_COL, TANK_COL
                ),
                axis=1
            )

        df_mbal = avg.sort_values(DATE_COL)

        # Interpolated PVT properties from pres_avg
        for col, prop in zip([OIL_FVF_COL, GAS_FVF_COL, RS_COL],
                             [OIL_FVF_COL, GAS_FVF_COL, RS_COL]):
            df_mbal[col] = df_mbal[PRESSURE_COL].apply(
                lambda press: interp_pvt_matbal(df_pvt, PRESSURE_PVT_COL, prop, press)
            )

        # In case properties are calculated using correlations
        if (self.tank_class.water_model.salinity is not None
                and self.tank_class.water_model.temperature is not None
                and self.tank_class.water_model.unit is not None):
            df_mbal[WATER_FVF_COL] = self.tank_class.water_model.get_bw_at_press(df_mbal[PRESSURE_COL])
            df_mbal[RS_W_COL] = self.tank_class.water_model.get_rs_at_press(df_mbal[PRESSURE_COL])

            # In case there are default values for Bw and Rs_w
        else:
            df_mbal[WATER_FVF_COL] = self.tank_class.water_model.get_default_bw()
            df_mbal[RS_W_COL] = self.tank_class.water_model.get_default_rs()

        df_mbal["Time_Step"] = 365.0
        df_mbal.loc[df_mbal.index[1:], "Time_Step"] = (df_mbal[DATE_COL].diff().dt.days.iloc[1:]).cumsum() + 365.0
        df_mbal = df_mbal.fillna(0.0)

        mbal_term = ho_terms_equation(
            df_mbal,
            OIL_CUM_TANK,
            WATER_CUM_TANK,
            GAS_CUM_TANK,
            PRESSURE_COL,
            OIL_FVF_COL,
            GAS_FVF_COL,
            RS_COL,
            WATER_FVF_COL,
            RS_W_COL,
            self.tank_class.swo,
            self.tank_class.cw,
            self.tank_class.cf,
            float(self.tank_class.oil_model.get_bo_at_press(self.tank_class.pi)),
            float(self.tank_class.oil_model.get_bg_at_press(self.tank_class.pi)),
            float(self.tank_class.oil_model.get_bo_at_press(self.tank_class.pi)),
            float(self.tank_class.oil_model.get_rs_at_press(self.tank_class.pi)),
            self.tank_class.pi
        )
        mbal_final_per_tank = mbal_term.fillna(0.0)
        if self.tank_class.aquifer is None:
            mbal_final_per_tank[WE] = 0

        elif isinstance(self.tank_class.aquifer, Fetkovich):
            df = self.tank_class.aquifer.we()
            mbal_final_per_tank = mbal_final_per_tank.join(df["Cumulative We"])
            # list_we = list(df["Cumulative We"])
            # mbal_final_per_tank[WE] = list_we
            # mbal_final_per_tank = pd.concat([df["Cumulative We"], mbal_final_per_tank], axis=1)

        elif isinstance(self.tank_class.aquifer, Carter_Tracy):
            df = self.tank_class.aquifer.we()
            mbal_final_per_tank = mbal_final_per_tank.join(df["Cumulative We"])
            # mbal_final_per_tank = pd.concat([df["Cumulative We"], mbal_final_per_tank], axis=1)

        return mbal_final_per_tank

    def campbell(self, option, ):
        mbal_df = self.mat_bal_df()
        y = mbal_df[UW_COL] / (mbal_df[OIL_EXP] + mbal_df[RES_EXP])
        x = mbal_df[OIL_CUM_TANK]

        if option == "data":
            data = pd.DataFrame({"Np": x, "F/Eo+Efw": y})
            return data

        # Graphic
        elif option == "plot":
            fig, ax1 = plt.subplots()
            ax1.scatter(x, y)
            ax1.set_xlabel("Np Cumulative Oil Production [MMStb]")
            ax1.set_ylabel("F/Eo+Efw")
            ax1.set_title(f"Campbell plot of " + str(mbal_df["Tank"][0].replace("_", " ")))
            plt.show()

    def havlena_odeh(self, option):
        mbal_df = self.mat_bal_df()
        y = mbal_df[UW_COL] / (mbal_df[OIL_EXP] + mbal_df[RES_EXP])
        x = mbal_df[WE] / (mbal_df[OIL_EXP] + mbal_df[RES_EXP])
        data = pd.DataFrame({"WeBw/Eo+Efw": x, "F/Eo+Efw": y})
        slope, intercept, r, p, se = stats.linregress(data["WeBw/Eo+Efw"], data["F/Eo+Efw"])

        # Data
        if option == "data":
            print(f"N [MMStb]: {intercept / 1000000:.4f}")
            return data

        # Graphic
        elif option == "plot":
            fig, ax1 = plt.subplots()
            ax1.scatter(data["WeBw/Eo+Efw"], data["F/Eo+Efw"], color="blue")
            reg_line = (slope * data["WeBw/Eo+Efw"]) + intercept
            ax1.plot(data["WeBw/Eo+Efw"], reg_line, color="red", label="Regression line")
            ax1.set_xlabel("WeBw/Eo+Efw")
            ax1.set_ylabel("F/Eo+Efw")
            ax1.set_title("Havlena y Odeh plot of " + str(mbal_df["Tank"][0].replace("_", " ")))
            ax1.annotate(
                "N [MMStb]: {:.2f}".format(intercept / 1000000),
                xy=(3, 5),
                xytext=(4, 5)
            )
            ax1.legend()
            plt.grid(True)
            plt.show()

    def havlena_odeh2(self, option):
        mbal_df = self.mat_bal_df()
        y = mbal_df[UW_COL] - mbal_df[WE]
        x = mbal_df[OIL_EXP] + mbal_df[RES_EXP]
        data = pd.DataFrame({"Eo+Efw": x, "F-We": y})
        slope, intercept, r, p, se = stats.linregress(data["Eo+Efw"], data["F-We"])

        # Data
        if option == "data":
            print(f"N [MMStb]: {slope / 1000000:.4f}")
            return data

        # Graphic
        elif option == "plot":
            fig, ax2 = plt.subplots()
            ax2.scatter(data["Eo+Efw"], data["F-We"], color="blue")
            reg_line = (slope * data["Eo+Efw"]) + intercept
            ax2.plot(data["Eo+Efw"], reg_line, color="red", label="Regression line")
            ax2.set_xlabel("Eo+Efw")
            ax2.set_ylabel("F-We")
            ax2.set_title("Havlena y Odeh plot of " + str(mbal_df["Tank"][0].replace("_", " ")))
            ax2.annotate(
                "N [MMStb]: {:.2f}".format(slope / 1000000),
                xy=(0.035, 0.2),
                xytext=(10, 3)
            )
            ax2.legend()
            plt.grid(True)
            plt.show()

    def eda(self, method, option=None):
        # Production Data
        df_prod = self.tank_class._prod_df_int()
        df_prod[DATE_COL] = pd.to_datetime(df_prod[DATE_COL])
        df_prod = df_prod.sort_values(by=DATE_COL)

        # Pressure Data
        df_press = self.tank_class._press_df_int()
        df_press[DATE_COL] = pd.to_datetime(df_press[DATE_COL])
        df_press = df_press.sort_values(by=DATE_COL)

        # Pressure date with Cumulative Production
        df_press_cum = self._calc_uw()
        df_press_cum[DATE_COL] = pd.to_datetime(df_press[DATE_COL])
        df_press_cum = df_press.sort_values(by=DATE_COL)

        # Average Pressure Data
        df_press_avg = self.mat_bal_df()

        # Production per Well
        if method == "production_per_well":
            pass

        # Cumulative production per Date
        if method == "cumulative_production_per_date":
            # Oil and Water
            if option == "liquids":
                fig1, ax1 = plt.subplots(figsize=(10, 6))
                colors = ["black", "blue"]
                columns = [OIL_CUM_COL, WATER_CUM_COL]

                for i, col in enumerate(columns):
                    ax1.plot(df_prod[DATE_COL], df_prod[col], color=colors[i], label=col)

                ax1.set_title("Cumulative Production per Date - " + str(df_prod[TANK_COL][0].replace("_", " ").upper()),
                              fontsize=16)
                ax1.set_xlabel("Date", fontsize=14)
                ax1.set_ylabel("Cumulative Production [MMStb]", fontsize=14)
                ax1.legend(loc='upper left', fontsize=12)

                plt.gcf().autofmt_xdate()
                plt.grid(True)
                plt.show()

            # Total Production
            elif option == "total_liquids":
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                colors = "skyblue"
                total_liquid = df_prod[OIL_CUM_COL] + df_prod[WATER_CUM_COL]

                ax2.plot(df_prod[DATE_COL], total_liquid, color=colors, label="Total Liquid")

                ax2.set_title("Cumulative Total Liquid Production per Date - " + str(
                    df_prod[TANK_COL][0].replace("_", " ").upper()),
                              fontsize=16)
                ax2.set_xlabel("Date", fontsize=14)
                ax2.set_ylabel("Cumulative Production [MMStb]", fontsize=14)
                ax2.legend(loc='upper left', fontsize=12)

                plt.gcf().autofmt_xdate()
                plt.grid(True)
                plt.show()

        # Pressure per Date
        if method == "pressure_per_date":
            # Observed Pressure
            if option == "observed":
                fig3, ax3 = plt.subplots(figsize=(10, 6))
                color = "green"

                ax3.plot(df_press[DATE_COL], df_press[PRESSURE_COL], color=color, label="Pressure")

                ax3.set_title(
                    "Pressure per Date - " + str(df_press[TANK_COL][0].replace("_", " ").upper()),
                    fontsize=16)
                ax3.set_xlabel("Date", fontsize=14)
                ax3.set_ylabel("Pressure [PSI]", fontsize=14)
                ax3.legend(loc='upper left', fontsize=12)

                plt.gcf().autofmt_xdate()
                plt.grid(True)
                plt.show()

            # Average Pressure
            elif option == "avg":
                fig4, ax4 = plt.subplots(figsize=(10, 6))
                color = "red"

                ax4.plot(df_press_avg[DATE_COL], df_press_avg[PRESSURE_COL], color=color, label=" Avg Pressure")

                ax4.set_title(
                    "Pressure per Date - " + str(df_press_avg[TANK_COL][0].replace("_", " ").upper()),
                    fontsize=16)
                ax4.set_xlabel("Date", fontsize=14)
                ax4.set_ylabel("Average Pressure[PSI]", fontsize=14)
                ax4.legend(loc='upper left', fontsize=12)

                plt.gcf().autofmt_xdate()
                plt.grid(True)
                plt.show()

            # Both pressures
            elif option == "both":
                fig5, ax5 = plt.subplots(figsize=(10, 6))
                ax5.plot(df_press[DATE_COL], df_press[PRESSURE_COL], color="green", label="Pressure")
                ax5.plot(df_press_avg[DATE_COL], df_press_avg[PRESSURE_COL], color="red", label="Avg Pressure")

                ax5.set_title("Pressure per Date - " + str(df_press[TANK_COL][0].replace("_", " ").upper()),)
                ax5.set_ylabel("Pressure[PSI]", fontsize=14)
                ax5.legend(loc='upper left', fontsize=12)

                plt.gcf().autofmt_xdate()
                plt.grid(True)
                plt.show()

        # Pressure per Cumulative Production
        if method == "pressure_per_cumulative_production":
            # Observed Pressure
            if option == "observed":
                pass

            # Average Pressure
            elif option == "avg":
                pass

