import pandas as pd
from pydantic import BaseModel
from well import Well
from new.vector_data import VectorData, ProdVector, InjVector, PressVector
from typing import Optional


class Tank(BaseModel):
    name: str
    wells: list[Well]
    # aquifer: Aquifer
    # fluid_model: FluidModel

    def calc_oil_cum(self):
        pass

    def calc_uw(self):
        pass

    def calc_press_avg(self):
        pass