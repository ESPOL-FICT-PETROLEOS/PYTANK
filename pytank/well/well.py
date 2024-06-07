from pydantic import BaseModel
from pytank.vector_data.vector_data import ProdVector, PressVector
from typing import Optional


class Well(BaseModel):
    name: str
    prod_data: Optional[ProdVector] = None
    press_data: Optional[PressVector] = None

