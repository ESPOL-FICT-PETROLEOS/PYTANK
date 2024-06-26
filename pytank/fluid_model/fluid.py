"""
fluid.py

This archive.py is to calculate the PVT properties of oil and water using linear interpolated.

libraries:
    - pydantic
    - scipy
    - pandera
"""

from pydantic import BaseModel
from scipy.interpolate import interp1d
import pandera as pa
from pandera.typing import DataFrame, Series
from pytank.constants.constants import (PRESSURE_PVT_COL,
                                        OIL_FVF_COL,
                                        GAS_FVF_COL,
                                        RS_COL
                                        )
from pytank.functions.pvt_correlations import RS_bw, Bo_bw


class _PVTSchema(pa.DataFrameModel):
    """
    Private Class to validate the values in the columns of PVT data
    """
    Pressure: Series[float] = pa.Field(ge=0, unique=True, coerce=True, nullable=False)
    Bo: Series[float] = pa.Field(ge=0, coerce=True)
    Bg: Series[float] = pa.Field(ge=0, coerce=True, nullable=True)
    GOR: Series[float] = pa.Field(ge=0, coerce=True)


class OilModel(BaseModel):
    """
    :parameter:
        - data_pvt: A DataFrame with the Oil PVT information that has been validated.
        - temperature (float): Temperature value [F].
    """
    data_pvt: DataFrame[_PVTSchema]
    temperature: float

    class Config:
        arbitrary_types_allowed = True

    def _interpolated_column_at_pressure(self, column_name: str, pressure: float) -> float:
        """

        :param:
            - column_name: Column name of PVT property of PVT DataFrame.
            - pressure: Pressure value to which the PVT property will be interpolated.

        :return:
            - float: Value of interpolated PVT property
        """
        df_pvt_local = self.data_pvt
        interp_func = interp1d(df_pvt_local[PRESSURE_PVT_COL], df_pvt_local[column_name], fill_value="extrapolate")
        return interp_func(pressure)

    def get_bo_at_press(self, pressure) -> float:
        """
        Method to interpolate oil volumetric factor Bo

        :param:
        pressure: Pressure value to which the PVT property will be interpolated.

        :return:
            - float: Value of Bo interpolated
        """
        return self._interpolated_column_at_pressure(OIL_FVF_COL, pressure)

    def get_bg_at_press(self, pressure) -> float:
        """
        Method to interpolate gas volumetric factor Bg

        :param:
        pressure: Pressure value to which the PVT property will be interpolated.

        :return:
            - float: Value of Bg interpolated
        """
        return self._interpolated_column_at_pressure(GAS_FVF_COL, pressure)

    def get_rs_at_press(self, pressure) -> float:
        """
        Method to interpolate oil solubility Rs

        :param:
        pressure: Pressure value to which the PVT property will be interpolated.

        :return:
            - float: Value of Rs interpolated
        """
        return self._interpolated_column_at_pressure(RS_COL, pressure)


class WaterModel(BaseModel):
    """

    :param:
        - salinity (float): Value of salinity [ppm]
        - temperature (float): Temperature value [F]
        - unit (int): 1 to Fields unit, 2 to Metric units

    """
    salinity: float = None
    temperature: float = None
    unit: int = None

    def get_bw_at_press(self, pressure: float) -> float:
        """
        Method to calculate the water volumetric factor Bw using correlation

        :param:
        pressure: Pressure value to calculate Bw

        :return:
            - float: Value of Bw
        """
        bw = Bo_bw(pressure, self.temperature, self.salinity, self.unit)
        return bw

    def get_rs_at_press(self, pressure: float) -> float:
        """
        Method to calculate the water solubility RS_bw using correlation

        :param:
        pressure: Pressure value to calculate RS_bw

        :return:
            - float: Value of RS_bw
        """
        rs = RS_bw(pressure, self.temperature, self.salinity, self.unit)
        return rs

    @staticmethod
    def get_default_bw() -> float:
        """
        Static method to calculate the Bw value per default.
        :return:
        float: 1
        """
        return float(1)

    @staticmethod
    def get_default_rs() -> float:
        """
        Static method to calculate the RS_bw value per default.
        :return:
        float: 0
        """
        return float(0)
