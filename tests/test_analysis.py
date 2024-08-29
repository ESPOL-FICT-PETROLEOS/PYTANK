import unittest
import pandas as pd
from pytank.analysis import Analysis, Tank
from pytank.fluid_model import OilModel, WaterModel
from pytank.well import Well, ProdVector, PressVector
from pytank.constants.constants import DATE_COL
from matplotlib import pyplot as plt


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        # Create sample data for wells
        well1 = Well(
            name_well="A-1-P",
            prod_data=ProdVector(
                freq="MS",
                data=pd.DataFrame(
                    {
                        "OIL_CUM": [3522, 4236, 6735, 11120, 15494],
                        "WATER_CUM": [3466, 6105, 7254, 9280, 12474],
                        "GAS_CUM": [3522, 4236, 6735, 11120, 15494],
                        "LIQ_CUM": [6988, 10341, 13989, 20400, 27968],
                    },
                    index=pd.date_range(
                        "2022-01-01", periods=5, freq="MS", name=DATE_COL
                    ),
                ),
            ),
            press_data=PressVector(
                freq=None,
                data=pd.DataFrame(
                    {"PRESSURE_DATUM": [884.696858, 884.696858]},
                    index=pd.date_range(
                        "2022-01-01", periods=2, freq="D", name=DATE_COL
                    ),
                ),
            ),
        )

        well2 = Well(
            name_well="A-2-P",
            prod_data=ProdVector(
                freq="MS",
                data=pd.DataFrame(
                    {
                        "OIL_CUM": [6214, 19301, 19309, 27440, 35066],
                        "WATER_CUM": [126, 962, 1548, 2395, 3637],
                        "GAS_CUM": [6214, 19301, 19309, 27440, 35066],
                        "LIQ_CUM": [6341, 20264, 20857, 29836, 38703],
                    },
                    index=pd.date_range(
                        "2022-01-01", periods=5, freq="MS", name=DATE_COL
                    ),
                ),
            ),
            press_data=PressVector(
                freq=None,
                data=pd.DataFrame(
                    {"PRESSURE_DATUM": [1214.652407, 926.493133]},
                    index=pd.date_range(
                        "2010-12-05", periods=2, freq="D", name=DATE_COL
                    ),
                ),
            ),
        )

        df_pvt = pd.DataFrame(
            {
                "Pressure": [
                    14.7,
                    214.7,
                    414.7,
                    644.7,
                    714.7,
                    814.7,
                    914.7,
                    1014.7,
                    1514.7,
                ],
                "Bo": [
                    1.037016316,
                    1.119258006,
                    1.130922092,
                    1.1414,
                    1.139779212,
                    1.138957404,
                    1.138363876,
                    1.137599138,
                    1.133330302,
                ],
                "Bg": [1.230913626, 0.081075184, 0.041712745, 0, 0, 0, 0, 0, 0],
                "GOR": [0, 33.64501602, 62.31098987, 89, 89, 89, 89, 89, 89],
            }
        )

        # Create the OilModel and WaterModel object
        self.oil_model = OilModel(
            data_pvt=df_pvt,
            temperature=25,
        )

        self.water_model = WaterModel(salinity=3000, temperature=200, unit=1)

        # Create the Tank object with the sample data
        self.tank1 = Tank(
            name_tank="tank_center",
            wells=[well1, well2],
            oil_model=self.oil_model,
            water_model=self.water_model,
            pi=3700,
            swo=0.25,
            cw=3.5e-6,
            cf=4.6e-6,
            aquifer=None,
        )

        self.analysis = Analysis(tank_class=self.tank1, freq="12M",
                                 position="end")

    def test_calc_uw(self):
        df_uw = self.analysis._calc_uw()
        self.assertIsInstance(df_uw, pd.DataFrame)

    def test_pressure_vol_avg(self):
        df_press_avg = self.analysis._pressure_vol_avg()
        self.assertIsInstance(df_press_avg, pd.DataFrame)

    def test_mat_bal_df(self):
        df_mbal = self.analysis.mat_bal_df()
        self.assertIsInstance(df_mbal, pd.DataFrame)

    def test_campbell_plot(self):
        camp = self.analysis.campbell_plot()
        self.assertIsInstance(camp, plt.Figure)

    def test_havlena_odeh_plot(self):
        ho = self.analysis.havlena_odeh_plot()
        self.assertIsInstance(ho, plt.Figure)

    def test_analytic_method_invalid_option(self):
        with self.assertRaises(ValueError):
            self.analysis.analytic_method(poes=1000, option="invalid")


if __name__ == "__main__":
    unittest.main()
