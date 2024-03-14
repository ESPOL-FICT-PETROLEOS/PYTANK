from pydantic import BaseModel
from new.vector_data import VectorData, ProdVector, InjVector


class Well(BaseModel):
    name: str
    vector_data: VectorData



