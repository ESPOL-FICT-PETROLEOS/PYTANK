import pytest
from pandas import DataFrame

from pytank.well.well import Well
from pytank.vector_data.vector_data import ProdVector, PressVector
import pandas as pd
import sys

prod = pd.DataFrame({
    'START_DATETIME': ['2022-01-01', '2022-02-01', '2022-03-01'],
    'OIL_CUM': [100, 150, 200],
    'WATER_CUM': [50, 75, 100],
    'GAS_CUM': [100, 150, 200],
    'LIQ_CUM': [150, 225, 300]
})
press = pd.DataFrame({
    'START_DATETIME': ["2022-01-05", "2022-01-26", "2022-02-12"],
    'PRESSURE_DATUM': [3000, 2930, 2900]
})

prod.set_index(prod['START_DATETIME'], inplace=True)
press.set_index(press['START_DATETIME'], inplace=True)


def test_well_creation():
    well = Well(name="Test Well")
    assert well.name == "Test Well"
    assert well.prod_data is None
    assert well.press_data is None


def test_well_with_prod_data():
    prod_data = ProdVector(freq="MS", data=prod)
    well = Well(name="Test Well", prod_data=prod_data)
    assert well.prod_data == prod_data


def test_well_with_press_data():
    press_data = PressVector(freq=None, data=press)
    well = Well(name="Test Well", press_data=press_data)
    assert well.press_data == press_data