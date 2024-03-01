import pandas as pd
from old.utilities import interp_pvt_matbal
from data_processing.processor import _DataProcessor


class Fluid:
    def __init__(
        self,
        production: pd.DataFrame,
        pressure_data: pd.DataFrame,
        pvt_data: pd.DataFrame,
    ):
        """
        Class to calculated the interpolation of pvt properties.
        Parameters
        ----------
        pvt_data: pd.DataFrame
            DataFrame containing PVT data.
        pressure_data: pd.DataFrame
            DataFrame cantaining pressure data.
        """

        # Composition class
        self.processor = _DataProcessor(production, pressure_data, pvt_data)
        self.processor._process_data()

        # Initialize the Fluid class with pvt_data
        # self.interpolate_pvt_info()

        self.pvt_data = pvt_data

    def interpolate_pvt_info(self):
        """
        Interpolates missing PVT data using backward-fill method.
        Returns
        -------
        pd.DataFrame:
            DataFrame with interpolated PVT data.

        """
        # instantiate the method to obtain a Dataframe of average pressures from the _DataProcessor class
        self.avg = self.processor._calculate_pressure_avg()

        # Interpolate 'PRESSURE_DATUM' in the pressure_data Dataframe using linear interpolation
        self.avg["press_avg"] = self.avg["press_avg"].interpolate(method="linear")

        # Fill missing values in pvt_data and pressure_data using forward-fill
        self.pvt_data = self.pvt_data.ffill()
        self.avg = self.avg.ffill()

        # Add columns 'Bo', 'uo', 'Bg' and 'press_avg_data'
        for column in ["Bo", "Bg", "GOR"]:
            self.avg[column] = self.avg[column] = pd.NA

        # Iterate over each row in 'press_avg_data'
        for index, row in self.avg.iterrows():

            # Extract the 'PRESSURE_DATUM' value for each row
            pressure_datum = row["press_avg"]

            # Filter data from 'pvt_data' for pressures less than or equal to 'pressure_datum'
            pvt_subset = self.pvt_data[self.pvt_data["Pressure"] <= pressure_datum]

            # Check if there is enough data to perform extrapolation
            if len(pvt_subset) > 1:

                # Perform extrapolation for each property using the interp_pvt_matbal function
                for column in ["Bo", "Bg", "GOR"]:
                    pvt_value = interp_pvt_matbal(
                        pvt_subset, "Pressure", column, pressure_datum
                    )

                    # Assign the extrapolated value to 'press_avg_data'
                    self.avg.at[index, column] = pvt_value

        return self.avg


# Test


production = pd.read_csv("../tests/data_for_tests/full_example_1/production.csv")
pressure = pd.read_csv("../tests/data_for_tests/full_example_1/pressures.csv")
pvt_data = pd.read_csv("../tests/data_for_tests/full_example_1/pvt.csv")

p_interp = Fluid(production, pressure, pvt_data).interpolate_pvt_info()

print(p_interp)
