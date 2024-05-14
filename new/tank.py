import pandas as pd
from pydantic import BaseModel
from well import Well
from new.vector_data import VectorData, ProdVector, InjVector, PressVector
from typing import Optional,List
class Tank(BaseModel):
    #name: str
    wells: List[Well]


    def calc_prod(self):
        pass

    def calc_uw(self):
        pass

    def calc_press_avg(self):
        pass

