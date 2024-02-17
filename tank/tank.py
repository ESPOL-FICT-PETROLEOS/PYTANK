from data_processing.processor import _DataProcessor
import pandas as pd
from material_balance.material_balance import pressure_vol_avg

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

class Tank(_DataProcessor):
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


    def calculate_pressure_avg(self) -> pd.DataFrame:
        """
        Calculate the average pressure per tank over a specified frecuency.

        Returns:
            DataFrame containing average pressure per tank

        """
        avg_freq = "12MS"
        df_press_avg = self.df_press.groupby(TANK_NAME_COL).apply(
            lambda g: pressure_vol_avg(g, WELL_NAME_COL, DATE_COL, PRESS_COL, UW_COL, avg_freq, "end")
        ).reset_index(0)

        # Chose only columns
        press_avg = df_press_avg[[TANK_NAME_COL, PRESS_COL]]
        press_avg.columns = [TANK_NAME_COL, 'press_avg']

        return press_avg

# Test
production = "../tests/data_for_tests/full_example_1/production.csv"
pressure = "../tests/data_for_tests/full_example_1/pressures.csv"
pvt = "../tests/data_for_tests/full_example_1/pvt.csv"

pro = pd.read_csv(production)
pre = pd.read_csv(pressure)
pt = pd.read_csv(pvt)

df1 = Tank(pro, pre, pt).calculate_pressure_avg()

print(df1)