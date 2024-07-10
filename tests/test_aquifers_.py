import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pytank.aquifer.aquifer_model import Fetkovich, CarterTracy
import pytest


class TestFetkovich(unittest.TestCase):
    def setUp(self):
        self.aq_radius = 14000
        self.res_radius = 2000
        self.aq_thickness = 20
        self.phi = 0.25
        self.ct = 0.000007
        self.theta = 290
        self.k = 25
        self.water_visc = 0.6
        self.pr = [3000, 2800, 2500, 2300, 2000]
        self.time_step = [365, 730, 1095, 1460, 1825]

    def test_we(self):
        fet = Fetkovich(
            aq_radius=self.aq_radius,
            res_radius=self.res_radius,
            aq_thickness=self.aq_thickness,
            aq_por=self.phi,
            ct=self.ct,
            theta=self.theta,
            k=self.k,
            water_visc=self.water_visc,
            pr=self.pr,
            time_step=self.time_step
        )

        result = fet.we()

        # Verify that the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)

        # Verify that the DataFrame has the expected columns
        self.assertIn("Delta We", result.columns)
        self.assertIn("Cumulative We", result.columns)
        self.assertIn("Elapsed time", result.columns)

        # Assertions to verify the values
        self.assertGreater(result["Delta We"].sum(), 0)
        self.assertGreater(result["Cumulative We"].max(), 0)
        self.assertGreater(result["Elapsed time"].max(), 0)

    def test_negative_pressure(self):
        pr = [2740, 2500, 2290, 2109, -1949]
        time_step = [0, 365, 730, 1095, 1460]
        with pytest.raises(ValueError, match="Pressure must be greater than zero"):
            fetkovich = Fetkovich(self.aq_radius, self.res_radius, self.aq_thickness, self.phi,
                                  self.ct, self.theta, self.k, self.water_visc,
                                  boundary_type='no_flow', flow_type='radial',
                                  pr=pr, time_step=time_step,
                                  )
            results = fetkovich.we()

    """def test_pressure_descendent_order(self):
        pr = [2408, 2444, 2472, 2490, 2500]
        time_step = [0, 182.5, 365.0, 547.5, 730.0]
        with pytest.raises(ValueError, match="Pressure array must be in descendant order"):
            fetkovich = Fetkovich(self.aq_radius, self.res_radius, self.aq_thickness, self.phi,
                                  self.ct, self.theta, self.k, self.water_visc,
                                  boundary_type='no_flow', flow_type='radial',
                                  pr=pr, time_step=time_step,
                                  )
            results = fetkovich.we()"""

    def test_pr_and_time_dimension(self):
        pr = [3000, 2800, 2500, 2300, 2000]
        time_step = [365, 730, 1095, 1460]
        with pytest.raises(ValueError, match="Dimensions of pressure array and time array "
                                             "should be equal,"
                                             "please verify your input"):
            fetkovich = Fetkovich(self.aq_radius, self.res_radius, self.aq_thickness, self.phi,
                                  self.ct, self.theta, self.k, self.water_visc,
                                  boundary_type='no_flow', flow_type='radial',
                                  pr=pr, time_step=time_step,
                                  )
            results = fetkovich.we()


class TestCarterTracy(unittest.TestCase):
    def setUp(self):
        self.aq_por = 0.2
        self.ct = 0.000007
        self.res_radius = 2000
        self.aq_thickness = 20
        self.theta = 290
        self.aq_perm = 25
        self.water_visc = 0.6
        self.pr = [3000, 2800, 2500, 2300, 2000]
        self.time_step = [365, 730, 1095, 1460, 1825]

    def test_we(self):
        ct = CarterTracy(
            aq_por=self.aq_por,
            ct=self.ct,
            res_radius=self.res_radius,
            aq_thickness=self.aq_thickness,
            theta=self.theta,
            aq_perm=self.aq_perm,
            water_visc=self.water_visc,
            pr=self.pr,
            time_step=self.time_step
        )

        result = ct.we()

        # Verify that the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)

        # Verify that the DataFrame has the expected columns
        self.assertIn("Cumulative We", result.columns)
        self.assertIn("Elapsed time, days", result.columns)

        # Assertions to verify the values
        self.assertGreater(result["Cumulative We"].max(), 0)

    def test_negative_pressure(self):
        pr = [2740, 2500, 2290, 2109, -1949]
        time_step = [0, 365, 730, 1095, 1460]
        with pytest.raises(ValueError, match="Pressure must be greater than zero"):
            ct = CarterTracy(
                aq_por=self.aq_por,
                ct=self.ct,
                res_radius=self.res_radius,
                aq_thickness=self.aq_thickness,
                theta=self.theta,
                aq_perm=self.aq_perm,
                water_visc=self.water_visc,
                pr=pr,
                time_step=time_step
            )
            results = ct.we()

    """def test_pressure_descendent_order(self):
        pr = [2408, 2444, 2472, 2490, 2500]
        time_step = [0, 182.5, 365.0, 547.5, 730.0]
        with pytest.raises(ValueError, match="Pressure array must be in descendant order"):
            ct = CarterTracy(
                aq_por=self.aq_por,
                ct=self.ct,
                res_radius=self.res_radius,
                aq_thickness=self.aq_thickness,
                theta=self.theta,
                aq_perm=self.aq_perm,
                water_visc=self.water_visc,
                pr=pr,
                time_step=time_step
            )
            results = ct.we()"""

    def test_pr_and_time_dimension(self):
        pr = [3000, 2800, 2500, 2300, 2000]
        time_step = [365, 730, 1095, 1460]
        with pytest.raises(ValueError, match="Dimensions of pressure array and time array "
                                             "should be equal,"
                                             "please verify your input"):
            ct = CarterTracy(
                aq_por=self.aq_por,
                ct=self.ct,
                res_radius=self.res_radius,
                aq_thickness=self.aq_thickness,
                theta=self.theta,
                aq_perm=self.aq_perm,
                water_visc=self.water_visc,
                pr=pr,
                time_step=time_step
            )
            results = ct.we()


if __name__ == '__main__':
    unittest.main()
