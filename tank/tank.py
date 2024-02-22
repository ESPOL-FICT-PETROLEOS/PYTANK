from data_processing.processor import _DataProcessor
import pandas as pd
from material_balance.material_balance import pressure_vol_avg


class Tank:
    def __init__(self, list_well: list):
        """
        Initialize the Well object.

        Parameters
        production: DataFrame containing production data.
        pressure:
        pvt:
        """
        try:
            self.list_well = list_well

        except pd.errors.EmptyDataError:
            print("Error: Dataframe is empty.")
        except pd.errors.ParserError as pe:
            print(f"Error parsing DataFrame. Details: {pe}")
        except Exception as ex:
            print(f"Unexpected error: {ex}")


    def production_per_tank(self):
        pass


