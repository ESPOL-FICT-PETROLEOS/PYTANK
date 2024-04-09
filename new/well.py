import pandas as pd
from pydantic import BaseModel
from new.vector_data import VectorData, ProdVector, InjVector, PressVector
from typing import Optional


class Well(BaseModel):
    name: str
    prod_data: ProdVector
    press_data: Optional[PressVector] = None

"""class FluidModel(BaseModel):
    data: pd.DataFrame

    def interp_table(self):
        pass

    def get_bo_at_press(self, pressure):
        pass"""

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


