"""
well.py

Defines the Well class to group production and pressure information per well.

This module provides the Well class, which is designed to encapsulate
production and pressure data for individual wells. The class is structured
using methods to facilitate data management related to well performance and
reservoir behavior.

Libraries used:
    - pydantic: For data validation and settings management.
    - typing: For type hinting and annotations.
"""

from pydantic import BaseModel
from typing import Optional
from pytank.vector_data import ProdVector, PressVector


class Well(BaseModel):
    """
    Represents a well with production and pressure data.

    This class is used to handle pressure and production vectors for a well.
    It inherits from the BaseModel class, which provides data validation and
    serialization functionality.

    Attributes:
        name_well (str): The name_tank of the well.
        prod_data (Optional[ProdVector]): The production data vector for the
            well. Defaults to None.
        press_data (Optional[PressVector]): The pressure data vector for the
            well. Defaults to None.
    """

    name_well: str
    prod_data: Optional[ProdVector] = None
    press_data: Optional[PressVector] = None
