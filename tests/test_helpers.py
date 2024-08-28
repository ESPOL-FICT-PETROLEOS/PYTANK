import pytest
import pandas as pd
from pytank.functions.helpers import create_wells, search_wells
from pytank.vector_data import ProdVector, PressVector
from pytank.well import Well


# Test function create_wells
def test_create_wells_with_valid_data():
    df_prod = pd.DataFrame({
        'START_DATETIME': ['2022-01-01', '2022-02-01', '2022-03-01'],
        'ITEM_NAME': ['Well1', 'Well1', 'Well1'],
        'OIL_CUM': [100, 150, 200],
        'WATER_CUM': [50, 75, 100],
        'GAS_CUM': [100, 150, 200],
        'LIQ_CUM': [150, 225, 300]
    })
    df_press = pd.DataFrame({
        'DATE': ['2022-01-05', '2022-01-26', '2022-02-12'],
        'WELLBORE': ['Well1', 'Well1', 'Well1'],
        'PRESSURE_DATUM': [3000, 2930, 2900]
    })

    wells = create_wells(df_prod, df_press, freq_prod='MS', freq_press=None)

    assert len(wells) == 1
    assert wells[0].name == 'Well1'
    assert isinstance(wells[0].prod_data, ProdVector)
    assert isinstance(wells[0].press_data, PressVector)


def test_create_wells_with_missing_data():
    df_prod = pd.DataFrame({
        'START_DATETIME': ['2022-01-01', '2022-02-01', '2022-03-01'],
        'ITEM_NAME': ['Well1', 'Well1', 'Well1'],
        'OIL_CUM': [100, 150, 200],
        'WATER_CUM': [50, 75, 100],
        'GAS_CUM': [100, 150, 200],
        'LIQ_CUM': [150, 225, 300]
    })
    df_press = pd.DataFrame({
        'DATE': ['2022-01-05', '2022-01-26'],
        'WELLBORE': ['Well1', 'Well1'],
        'PRESSURE_DATUM': [3000, 2930]
    })

    wells = create_wells(df_prod, df_press, freq_prod='MS')

    assert len(wells) == 1
    assert wells[0].name == 'Well1'
    assert isinstance(wells[0].prod_data, ProdVector)
    assert isinstance(wells[0].press_data, PressVector)


def test_create_wells_with_multiple_wells():
    df_prod = pd.DataFrame({
        'START_DATETIME': ['2022-01-01', '2022-02-01', '2022-03-01',
                           '2022-01-01', '2022-02-01', '2022-03-01'],
        'ITEM_NAME': ['Well1', 'Well1', 'Well1', 'Well2', 'Well2', 'Well2'],
        'OIL_CUM': [100, 150, 200, 50, 75, 100],
        'WATER_CUM': [50, 75, 100, 25, 40, 50],
        'GAS_CUM': [100, 150, 200, 75, 100, 125],
        'LIQ_CUM': [150, 225, 300, 75, 115, 150]
    })
    df_press = pd.DataFrame({
        'DATE': ['2022-01-05', '2022-01-26', '2022-02-12',
                 '2022-01-10', '2022-01-30', '2022-02-15'],
        'WELLBORE': ['Well1', 'Well1', 'Well1', 'Well2', 'Well2', 'Well2'],
        'PRESSURE_DATUM': [3000, 2930, 2900, 2800, 2750, 2700]
    })

    wells = create_wells(df_prod, df_press, freq_prod='MS')

    assert len(wells) == 2
    assert 'Well1' in [well.name for well in wells]
    assert 'Well2' in [well.name for well in wells]
    for well in wells:
        assert isinstance(well.prod_data, ProdVector)
        assert isinstance(well.press_data, PressVector)


# Test function search wells
def test_search_wells_found():
    wells = [
        Well(name='Well1', prod_data=None, press_data=None),
        Well(name='Well2', prod_data=None, press_data=None),
        Well(name='Well3', prod_data=None, press_data=None)
    ]
    well_names = ['Well1', 'Well3']

    result = search_wells(wells, well_names)

    assert len(result) == 2
    assert all(well.name in well_names for well in result)


def test_search_wells_not_found():
    wells = [
        Well(name='Well1', prod_data=None, press_data=None),
        Well(name='Well2', prod_data=None, press_data=None),
        Well(name='Well3', prod_data=None, press_data=None)
    ]
    well_names = ['Well1', 'Well4', 'Well3']

    with pytest.warns(UserWarning) as record:
        result = search_wells(wells, well_names)

    assert len(result) == 2
    assert all(well.name in ['Well1', 'Well3'] for well in result)
    assert len(record) == 1
    assert 'Well4' in str(record[0].message)


def test_search_wells_empty_list():
    wells = []
    well_names = ['Well1', 'Well2']

    result = search_wells(wells, well_names)

    assert len(result) == 0