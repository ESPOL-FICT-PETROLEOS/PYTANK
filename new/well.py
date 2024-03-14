from pydantic import BaseModel
import pandas as pd
from new.vector_data import VectorData, ProdVector


class Well(BaseModel):
    name: str
    vector_data: VectorData





