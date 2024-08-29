"""
fluid_model.py

Calculates the PVT properties of oil and water using linear interpolation.

This module provides classes and methods to manage oil and water PVT data,
validate the data using Pydantic and Pandera, and interpolate PVT properties
at specific pressures using SciPy's `interp1d` function.

The main classes and their purposes are:
    - `_PVTSchema`: A private class that defines the schema for validating PVT
    data using Pandera.
    - `OilModel`: A class that represents an oil model and provides methods to
      interpolate oil PVT properties (Bo, Bg, Rs) at specific pressures.
    - `WaterModel`: A class that represents a water model and provides methods
      to calculate water PVT properties (Bw, Rsw) at specific pressures using
      correlations.

Libraries used:
    - pydantic: For data validation and serialization.
    - scipy: For linear interpolation using `interp1d`.
    - pandera: For defining and validating DataFrame schemas.
"""

from pydantic import BaseModel
from scipy.interpolate import interp1d
import pandera as pa
from pandera.typing import DataFrame, Series
from pytank.constants.constants import (
    PRESSURE_PVT_COL,
    OIL_FVF_COL,
    GAS_FVF_COL,
    RS_COL,
)
from pytank.functions.pvt_correlations import RS_bw, Bo_bw


class _PVTSchema(pa.DataFrameModel):
    """Private class to validate the values in the columns of PVT data.

    This class is used to define the schema for the PVT data DataFrame. It
    inherits from the DataFrameModel class provided by the Pydantic library.

    Attributes:
        Pressure (Series[float]): The pressure column. Values must be greater
            than or equal to 0, unique, coerced to float, and not nullable.
        Bo (Series[float]): The oil volumetric factor (Bo) column. Values must
            be greater than or equal to 0 and coerced to float.
        Bg (Series[float]): The gas volumetric factor (Bg) column. Values must
            be greater than or equal to 0, coerced to float, and nullable.
        GOR (Series[float]): The gas-oil ratio (GOR) column. Values must be
            greater than or equal to 0 and coerced to float.
    """

    Pressure: Series[float] = pa.Field(ge=0, unique=True, coerce=True,
                                       nullable=False)
    Bo: Series[float] = pa.Field(ge=0, coerce=True)
    Bg: Series[float] = pa.Field(ge=0, coerce=True, nullable=True)
    GOR: Series[float] = pa.Field(ge=0, coerce=True)


class OilModel(BaseModel):
    """Represents an oil model with PVT data.

    This class is used to manage oil PVT data and provide methods to
    interpolate PVT properties at specific pressures.

    Attributes:
        data_pvt (DataFrame[_PVTSchema]): A DataFrame containing validated
            oil PVT data.
        temperature (float): The temperature value in degrees Fahrenheit.
    """

    data_pvt: DataFrame[_PVTSchema]
    temperature: float

    class Config:
        arbitrary_types_allowed = True

    def _interpolated_column_at_pressure(
        self, column_name: str, pressure: float
    ) -> float:
        """Interpolates a PVT property column at the given pressure.

        Args:
            column_name (str): The name_tank of the PVT property column.
            pressure (float): The pressure value at which to interpolate.

        Returns:
            float: The interpolated value of the PVT property.
        """
        df_pvt_local = self.data_pvt
        interp_func = interp1d(
            df_pvt_local[PRESSURE_PVT_COL],
            df_pvt_local[column_name],
            fill_value="extrapolate",
        )
        return interp_func(pressure)

    def get_bo_at_press(self, pressure) -> float:
        """Interpolates the oil volumetric factor (Bo) at the given pressure.

        Args:
            pressure (float): The pressure value at which to interpolate Bo.

        Returns:
            Bo (float): The interpolated value of Bo.
        """
        return self._interpolated_column_at_pressure(OIL_FVF_COL, pressure)

    def get_bg_at_press(self, pressure) -> float:
        """Interpolates the gas volumetric factor (Bg) at the given pressure.

        Args:
            pressure (float): The pressure value at which to interpolate Bg.

        Returns:
            Bg (float): The interpolated value of Bg.
        """
        return self._interpolated_column_at_pressure(GAS_FVF_COL, pressure)

    def get_rs_at_press(self, pressure) -> float:
        """Interpolates the oil solubility (Rs) at the given pressure.

        Args:
            pressure (float): The pressure value at which to interpolate Rs.

        Returns:
            Rs (float): The interpolated value of Rs.
        """
        return self._interpolated_column_at_pressure(RS_COL, pressure)


class WaterModel(BaseModel):
    """Represents a water model with salinity and temperature properties.

    This class is used to manage water properties and provide methods to
    calculate water volumetric factor (Bw) and water solubility (RS_bw) at
    specific pressures using correlations.

    Attributes:
        salinity (float): The salinity value in parts per million (ppm).
        temperature (float): The temperature value in degrees Fahrenheit.
        unit (int): The unit system, 1 for Field units or 2 for Metric units.
    """

    salinity: float = None
    temperature: float = None
    unit: int = None

    def get_bw_at_press(self, pressure: float) -> float:
        """Calculates the water volumetric factor (Bw) at the given pressure.

        Args:
            pressure (float): The pressure value at which to calculate Bw.

        Returns:
            Bw (float): The calculated value of Bw.
        """
        bw = Bo_bw(pressure, self.temperature, self.salinity, self.unit)
        return bw

    def get_rs_at_press(self, pressure: float) -> float:
        """Calculates the water solubility (RS_bw) at the given pressure.

        Args:
            pressure (float): The pressure value at which to calculate RS_bw.

        Returns:
            Rsw (float): The calculated value of RS_bw.
        """
        rs = RS_bw(pressure, self.temperature, self.salinity, self.unit)
        return rs

    @staticmethod
    def get_default_bw() -> float:
        """Returns the default value for Bw.

        Returns:
            Default Bw (float): The default value of Bw, which is 1.
        """
        return float(1)

    @staticmethod
    def get_default_rs() -> float:
        """Returns the default value for Bw.

        Returns:
            Default Rsw (float): The default value of Bw, which is 1.
        """
        return float(0)
