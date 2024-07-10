# PYTANK/__init__.py
import pandas as pd
from .pytank.vector_data import ProdVector, PressVector
from .pytank.functions.helpers import create_wells, search_wells
from .pytank.well import Well
from .pytank.fluid_model import OilModel, WaterModel
from .pytank.tank import Tank
from .pytank.analysis import Analysis
from .examples_data.read_data import production_data, pressure_data, pvt_data

__all__ = [
    'ProdVector',
    'PressVector',
    'create_wells',
    'search_wells',
    'Well',
    'OilModel',
    'WaterModel',
    'Tank',
    'Analysis',
    'production_data',
    'pressure_data',
    'pvt_data'
]
