import pandas as pd
from data_processing.processor import _DataProcessor

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


# Creation of well class
class Well(_DataProcessor):
    def __init__(self, production: pd.DataFrame, pressure: pd.DataFrame, pvt: pd.DataFrame):
        """
        Initialize the Well object.

        Parameters
        production: DataFrame containing production data.
        pressure:
        pvt:
        """
        try:
            super().__init__(production, pressure, pvt)
            self._process_data()

        except pd.errors.EmptyDataError:
            print("Error: Dataframe is empty.")
        except pd.errors.ParserError as pe:
            print(f"Error parsing DataFrame. Details: {pe}")
        except Exception as ex:
            print(f"Unexpected error: {ex}")


    def rate_oil(self) -> pd.DataFrame:
        """
        Calculates the oil rate per well

        Returns:
            DataFrame containing oil production rates.
        """
        # Group by year and well, then calculate cumulative production for each year
        df = self.df_prod.groupby([self.df_prod[DATE_COL].dt.year, WELL_NAME_COL])[OIL_RATE_COL].sum()
        df = df.groupby(level=WELL_NAME_COL).cumsum()  # Calculate the cumulative sum per well
        df = df.unstack()  # Pivot to have the wells as columns
        return df

    def rate_water(self) -> pd.DataFrame:
        """
        Calculates the water rate per well

        Returns:
            DataFrame containing oli production rates.
        """
        # Group by year and well, then calculate cumulative production for each year
        df = self.df_prod.groupby([self.df_prod[DATE_COL].dt.year, WELL_NAME_COL])[WATER_RATE_COL].sum()
        df = df.groupby(level=WELL_NAME_COL).cumsum()  # Calculate the cumulative sum per well
        df = df.unstack()  # Pivot to have the wells as columns
        return df

    def pressure_and_liquid_accumulation(self) -> pd.DataFrame:
        """
        Create a dataframe with pressure and liquid accumulation data.
        Returns:
            DataFrame Containing liquid cumulative with pressure.
        """

        """# Merge df_press and df_prod on the well name and date columns
        merged_df = pd.merge(self.df_press, self.df_prod[[DATE_COL, WELL_NAME_COL, LIQUID_VOL_COL]],
                             how='left', left_on=[DATE_COL, WELL_NAME_COL], right_on=[DATE_COL, WELL_NAME_COL])

        # Drop duplicate columns (if any)
        merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]

        merged_df = merged_df[[WELL_NAME_COL, PRESS_COL, "liquid_vol_x"]]

        return merged_df"""

        df = self.df_press.pivot_table(PRESS_COL, index=[WELL_NAME_COL, LIQUID_VOL_COL], columns="TEST_TYPE")
        df = df.reset_index()
        return df




# Test
production = "../tests/data_for_tests/full_example_1/production.csv"
pressure = "../tests/data_for_tests/full_example_1/pressures.csv"
pvt = "../tests/data_for_tests/full_example_1/pvt.csv"

pro = pd.read_csv(production)
pre = pd.read_csv(pressure)
pt = pd.read_csv(pvt)

df1 = Well(pro, pre, pt).rate_oil()

print(df1)