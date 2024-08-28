"""
well.py

This module defines the Well Class to group production and pressure
information per well.

The logic is structured using classes and methods.

"""
from pydantic import BaseModel
from typing import Optional
from pytank.vector_data import ProdVector, PressVector


class Well(BaseModel):
    """
    Class used to handle pressure and production vectors
    """
    name: str
    prod_data: Optional[ProdVector] = None
    press_data: Optional[PressVector] = None
