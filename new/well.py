import pandas as pd
from pydantic import BaseModel
from new.vector_data import ProdVector, PressVector
from typing import Optional


class Well(BaseModel):
    name: str
    prod_data: Optional[ProdVector] = None
    press_data: Optional[PressVector] = None

