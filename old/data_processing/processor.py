# Libraries
import pandas as pd
from old.utilities import days_in_month, interp_from_dates, interp_dates_row
from scipy.interpolate import interp1d
from material_balance.material_balance import underground_withdrawal, pressure_vol_avg

# Constants for column names
DATE_COL = "START_DATETIME"
WELL_NAME_COL = "ITEM_NAME"
TANK_NAME_COL = "Tank"
OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL = "OIL_CUM", "WATER_CUM", "GAS_CUM"
OIL_RATE_COL, WATER_RATE_COL, GAS_RATE_COL = "oil_rate", "water_rate", "gas_rate"
LIQUID_RATE_COL, LIQUID_CUM_COL = "liquid_rate", "liquid_cum"
PRESS_COL, PRESS_TYPE_COL = "PRESSURE_DATUM", "TEST_TYPE"
LIQUID_VOL_COL = "liquid_vol"
OIL_FVF_COL, GOR_COL, GAS_FVF_COL = "Bo", "GOR", "Bg"
CAL_DAY_COL = "cal_day"
UW_COL = "UW"


class _DataProcessor:
    """
    Private class that processes the data so that it can use the public methods of the Tank and Well classes.
    """

    def __init__(
        self,
        production: pd.DataFrame,
        pressure: pd.DataFrame = None,
        pvt: pd.DataFrame = None,
    ):
        self.df_prod = production
        self.df_press = pressure
        self.df_pvt = pvt

    def _process_data(self):
        """
        Process production data.
        """
        self._cast_date_column()
        self._calculate_rates()
        self._create_dataframe()
        self._interpolate_pvt_info()
        self._interpolate_cumulatives_into_press_df()
        self._calculate_underground_withdrawal()

    def _cast_date_column(self):
        """
        Convert the date columns in self.df_prod and self.df_press DataFrames to datetime format.
        Also, rename specific columns in self.df_press DataFrame.
        """
        # Convert date columns to datetime format
        self.df_prod[DATE_COL] = pd.to_datetime(self.df_prod[DATE_COL])

        # Rename columns in the pressure file
        self.df_press = self.df_press.rename(
            columns={"WELLBORE": WELL_NAME_COL, "DATE": DATE_COL}
        )
        self.df_press[DATE_COL] = pd.to_datetime(self.df_press[DATE_COL])

    def _create_dataframe(self):
        """
        Private function for creation of dataframes
        """
        df_tank_cols = ["START_DATETIME", "Tank", "liquid_vol"]
        self.df_tank = (
            self.df_prod[df_tank_cols]
            .groupby(df_tank_cols[:-1])
            .sum()
            .groupby("Tank")
            .cumsum()
            .reset_index()
        )
        self.df_tank.rename(columns={"liquid_vol": "liquid_cum"}, inplace=True)

    def _calculate_rates(self):
        """
        Private function for calculate oil and water production rates.
        """
        # Calculate production rates
        self.df_prod[CAL_DAY_COL] = self.df_prod[DATE_COL].map(
            lambda date: days_in_month(date)
        )

        cols_input = [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]
        cols_output = [OIL_RATE_COL, WATER_RATE_COL, GAS_RATE_COL]

        df_input = self.df_prod[[WELL_NAME_COL, *cols_input]]
        self.df_prod[cols_output] = (
            df_input.groupby(WELL_NAME_COL)
            .diff()
            .fillna(df_input)
            .div(self.df_prod[CAL_DAY_COL], axis=0)
        )

        self.df_prod[LIQUID_RATE_COL] = (
            self.df_prod[OIL_RATE_COL] + self.df_prod[WATER_RATE_COL]
        )
        self.df_prod[LIQUID_CUM_COL] = (
            self.df_prod[OIL_CUM_COL] + self.df_prod[WATER_CUM_COL]
        )

        self.df_prod[LIQUID_VOL_COL] = (
            self.df_prod[LIQUID_RATE_COL] * self.df_prod[CAL_DAY_COL]
        )
        df_field = (
            self.df_prod.groupby(DATE_COL)[LIQUID_VOL_COL].sum().cumsum().reset_index()
        )
        df_field.rename(columns={LIQUID_VOL_COL: LIQUID_CUM_COL}, inplace=True)

        self.df_press[LIQUID_VOL_COL] = interp_from_dates(
            self.df_press[DATE_COL], df_field[DATE_COL], df_field[LIQUID_CUM_COL]
        )

    def _interpolate_pvt_info(self):
        """
        Private functions to interpolate PVT information.

        Interpolates the PVT information for oil, gas, and gas-oil ratio (GOR)
        from the PVT DataFrame and applies the interpolated values to the pressure DataFrame.
        """
        # self.df_pvt = self.df_pvt.drop_duplicates(subset=PRESS_COL)
        oil_fvf_interp = interp1d(
            self.df_pvt["Pressure"], self.df_pvt[OIL_FVF_COL], fill_value="extrapolate"
        )
        gas_oil_rs_interp = interp1d(
            self.df_pvt["Pressure"], self.df_pvt[GOR_COL], fill_value="extrapolate"
        )
        gas_fvf_interp = interp1d(
            self.df_pvt["Pressure"], self.df_pvt[GAS_FVF_COL], fill_value="extrapolate"
        )

        # Apply the functions to the pressure DataFrame
        self.df_press[OIL_FVF_COL] = oil_fvf_interp(self.df_press[PRESS_COL])
        self.df_press[GOR_COL] = gas_oil_rs_interp(self.df_press[PRESS_COL])
        self.df_press[GAS_FVF_COL] = gas_fvf_interp(self.df_press[PRESS_COL])

    def _interpolate_cumulatives_into_press_df(self):
        """
        Interpolate oil, gas, and water cumulatives into the pressure DataFrame.
        """
        for col in [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]:
            self.df_press[col] = self.df_press.apply(
                lambda x: interp_dates_row(
                    x,
                    DATE_COL,
                    self.df_prod,
                    DATE_COL,
                    col,
                    WELL_NAME_COL,
                    WELL_NAME_COL,
                    left=0.0,
                ),
                axis=1,
            )
            # For wells not available in the production DataFrame, fill NaNs with 0
            self.df_press[col].fillna(0, inplace=True)

    def _calculate_underground_withdrawal(self):
        """
        Private function to calculate underground withdrawal for each well

        Calculates the underground withdrawal using the 'underground_withdrawal' function from the material_balance
        module.
        The calculates values are assigned to the 'UW_COL' column in the pressure DataFrame.
        """
        self.df_press[UW_COL] = underground_withdrawal(
            self.df_press,
            OIL_CUM_COL,
            WATER_CUM_COL,
            GAS_CUM_COL,
            OIL_FVF_COL,
            1,
            GAS_FVF_COL,
            GOR_COL,
            0,
        )

    def _calculate_pressure_avg(self) -> pd.DataFrame:
        """
        Calculate the average pressure per tank over a specified frecuency.

        Returns:
            DataFrame containing average pressure per tank

        """
        avg_freq = "12MS"
        df_press_avg = (
            self.df_press.groupby(TANK_NAME_COL)
            .apply(
                lambda g: pressure_vol_avg(
                    g, WELL_NAME_COL, DATE_COL, PRESS_COL, UW_COL, avg_freq, "end"
                )
            )
            .reset_index(0)
        )

        # Chose only columns
        press_avg = df_press_avg[[TANK_NAME_COL, PRESS_COL]]
        press_avg.columns = [TANK_NAME_COL, "press_avg"]
        self.avg = press_avg

        return self.avg
