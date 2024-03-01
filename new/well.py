from pydantic import BaseModel
from new.vector_data import VectorData, ProdVector, InjVector


class WellBase(BaseModel):
    name: str
    vector_data: VectorData


class ProdWell(WellBase):
    vector_data = ProdVector


class InjWell(WellBase):
    vector_data = InjVector
