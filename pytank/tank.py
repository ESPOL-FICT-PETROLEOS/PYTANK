"""
tank.py

Defines the Tank class for processing reservoir data internally.

This module provides the Tank class, which serves as a container for
reservoir properties and manages associated well data. The Tank class
includes methods for handling pressure and production data, allowing
for efficient calculations and data management within reservoir
simulations.

The main methods of the Tank class are:
    - get_pressure_df: Returns a DataFrame with pressure data and PVT
    properties.
    - get_production_df: Returns a DataFrame with cumulative production data.

Libraries used:
    - pandas: For data manipulation and analysis.
    - pydantic: For data validation and settings management.
    - typing: For type hinting and annotations.
"""

import pandas as pd
from pydantic import BaseModel
from typing import Union, Optional
from pytank.constants.constants import (
    OIL_FVF_COL,
    GAS_FVF_COL,
    RS_COL,
    PRESSURE_COL,
    OIL_CUM_COL,
    GAS_CUM_COL,
    WATER_CUM_COL,
    DATE_COL,
    WELL_COL,
    WATER_FVF_COL,
    RS_W_COL,
    TANK_COL,
    LIQ_CUM,
)
from pytank.fluid_model import OilModel, WaterModel
from pytank.aquifer_model import Fetkovich, CarterTracy


class Tank(BaseModel):
    """
    Represents a reservoir tank with associated properties and methods.

    This class serves as a container for the reservoir (tank) properties and
    provides methods to manage pressure and production data. It inherits from
    the BaseModel class, which provides data validation and serialization
    functionality.
    """

    name_tank: str
    wells: list
    oil_model: OilModel
    water_model: WaterModel
    pi: float
    swo: float
    cw: float
    cf: float
    aquifer: Optional[Union[None, Fetkovich, CarterTracy]]

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        name_tank: str,
        wells: list,
        oil_model: OilModel,
        water_model: WaterModel,
        pi: float,
        swo: float,
        cw: float,
        cf: float,
        aquifer: Optional[Union[None, Fetkovich, CarterTracy]],
    ):
        """Initializes a Tank instance with the given parameters.

        Args:
            name_tank (str): The name_well of the tank (reservoir).
            wells (list): A list of Well instances associated with the tank.
            oil_model (BaseModel): An instance of the OilModel class for the
                tank.
            water_model (BaseModel): An instance of the WaterModel class for the
                tank.
            pi (float): The initial pressure of the tank [Psi].
            swo (float): The initial water saturation of the tank [decimal].
            cw (float): The water compressibility of the tank.
            cf (float): The total compressibility of the tank.
            aquifer (Optional[Union[None, Fetkovich, CarterTracy]]): An instance
                of an aquifer class (Fetkovich or CarterTracy) or None.
        """
        super().__init__(
            name_tank=name_tank,
            wells=wells,
            oil_model=oil_model,
            water_model=water_model,
            pi=pi,
            swo=swo,
            cw=cw,
            cf=cf,
            aquifer=aquifer,
        )

    def _press_df_internal(self) -> pd.DataFrame:
        """Internally manages the pressure vector for use in the UW method.

        This is a private method that creates a DataFrame containing pressure
        data and associated PVT properties for each well in the tank.

        Returns:
            df_press: A DataFrame with pressure data and PVT properties.
        """
        df_press = pd.DataFrame()
        for well in self.wells:
            press_vector = well.press_data
            well_name = well.name_well
            tank_name = self.name_tank
            if press_vector is not None:

                well_date = press_vector.data.index
                well_oil_fvf = self.oil_model.get_bo_at_press(
                    press_vector.data[PRESSURE_COL]
                )
                well_gas_fvf = self.oil_model.get_bg_at_press(
                    press_vector.data[PRESSURE_COL]
                )
                well_rs = self.oil_model.get_rs_at_press(
                    press_vector.data[PRESSURE_COL]
                )

                # In case properties are calculated using correlations
                if (
                    self.water_model.salinity is not None
                    and self.water_model.temperature is not None
                    and self.water_model.unit is not None
                ):
                    well_bw = self.water_model.get_bw_at_press(
                        press_vector.data[PRESSURE_COL]
                    )
                    well_rs_w = self.water_model.get_rs_at_press(
                        press_vector.data[PRESSURE_COL]
                    )

                    # In case there are default values for Bw and Rs_w
                else:
                    well_bw = self.water_model.get_default_bw()
                    well_rs_w = self.water_model.get_default_rs()

                # Create a copy of data from press_vector
                temp_df_press = press_vector.data.copy()

                # Add columns to DataFrame
                temp_df_press[WELL_COL] = well_name
                temp_df_press[DATE_COL] = well_date
                temp_df_press[OIL_FVF_COL] = well_oil_fvf
                temp_df_press[GAS_FVF_COL] = well_gas_fvf
                temp_df_press[RS_COL] = well_rs
                temp_df_press[WATER_FVF_COL] = well_bw
                temp_df_press[RS_W_COL] = well_rs_w
                temp_df_press[TANK_COL] = tank_name

                df_press = pd.concat([df_press, temp_df_press],
                                     ignore_index=True)
        return df_press

    def get_pressure_df(self) -> pd.DataFrame:
        """Gets a DataFrame with pressure data using the private
        _press_df_internal method.

        This method is marked private for internal use only.

        Returns:
            df_press: A DataFrame with pressure data and PVT properties.
        """
        return self._press_df_internal()

    def _prod_df_internal(self) -> pd.DataFrame:
        """Internally manages the production vector for use in the UW method.

        This is a private method that creates a DataFrame containing production
        data for each well in the tank.

        Returns:
            df_prod: A DataFrame with production data.
        """
        df_prod = pd.DataFrame()
        for well in self.wells:
            prod_vector = well.prod_data
            well_name = well.name_well
            tank_name = self.name_tank
            if prod_vector is not None:
                well_date = prod_vector.data.index
                well_oil_cum = prod_vector.data[OIL_CUM_COL]
                well_water_cum = prod_vector.data[WATER_CUM_COL]
                well_gas_cum = prod_vector.data[GAS_CUM_COL]
                well_liq_cum = prod_vector.data[LIQ_CUM]

                # Create a copy of data from prod_vector
                temp_df_prod = prod_vector.data.copy()

                temp_df_prod[WELL_COL] = well_name
                temp_df_prod[DATE_COL] = well_date
                temp_df_prod[OIL_CUM_COL] = well_oil_cum
                temp_df_prod[WATER_CUM_COL] = well_water_cum
                temp_df_prod[GAS_CUM_COL] = well_gas_cum
                temp_df_prod[LIQ_CUM] = well_liq_cum
                temp_df_prod[TANK_COL] = tank_name

                df_prod = pd.concat([df_prod, temp_df_prod],
                                    ignore_index=True)
        return df_prod

    def get_production_df(self) -> pd.DataFrame:
        """Gets a DataFrame with production data using the private
        _prod_df_internal method.

        This method is marked private for internal use only.

        Returns:
            df_prod: A DataFrame with cumulative production data.
        """
        return self._prod_df_internal()
