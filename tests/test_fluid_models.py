import unittest
import pandas as pd
from pytank.fluid_model import OilModel, WaterModel


class TestOilModel(unittest.TestCase):
    def setUp(self):
        self.df_pvt = pd.DataFrame(
            {
                "Pressure": [100, 200, 300],
                "Bo": [1.2, 1.1, 1.0],
                "Bg": [0.01, 0.02, 0.03],
                "GOR": [50, 60, 70],
            }
        )
        self.oil_model = OilModel(data_pvt=self.df_pvt, temperature=25)

    def test_get_bo_at_press(self):
        pressure = 150
        actual_bo = self.oil_model.get_bo_at_press(pressure)
        self.assertGreater(actual_bo, 0)

    def test_get_bg_at_press(self):
        pressure = 250
        actual_bg = self.oil_model.get_bg_at_press(pressure)
        self.assertGreater(actual_bg, 0)

    def test_get_rs_at_press(self):
        pressure = 150
        actual_rs = self.oil_model.get_rs_at_press(pressure)
        self.assertGreater(actual_rs, 0)


class TestWaterModel(unittest.TestCase):
    def test_get_bw_at_press(self):
        water_model = WaterModel(salinity=3000, temperature=200, unit=1)
        pressure = 2000
        actual_bw = water_model.get_bw_at_press(pressure)
        self.assertGreater(actual_bw, 0)

    def test_get_rs_at_press(self):
        water_model = WaterModel(salinity=3000, temperature=200, unit=1)
        pressure = 2000
        actual_rs = water_model.get_rs_at_press(pressure)
        self.assertGreater(actual_rs, 0)


if __name__ == "__main__":
    unittest.main()
