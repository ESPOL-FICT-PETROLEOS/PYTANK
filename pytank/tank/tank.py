"""
tank.py

This module defines the Tank CLass is to process data internally.

Also, it works as a container for the reservoir properties.

libraries:
    - pandas
    - pydantic
    - typing
"""

import pandas as pd
from pydantic import BaseModel
from typing import Union, Optional
from pytank.constants.constants import (OIL_FVF_COL,
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
from pytank.fluid_model.fluid import OilModel, WaterModel
from pytank.aquifer.aquifer_model import Fetkovich, CarterTracy


class Tank(BaseModel):
    """
    Class that functions as a container for the reservoir (tank) properties.
    """
    name: str
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

    def __init__(self, name: str,
                 wells: list,
                 oil_model: OilModel,
                 water_model: WaterModel,
                 pi: float,
                 swo: float,
                 cw: float,
                 cf: float,
                 aquifer: Optional[Union[None, Fetkovich, CarterTracy]]):
        """
        Init Method
        :param
            - name: Name of tank (reservoir)
            - wells: Instance of Well Class (list)
            - oil_model: Instance of OilModel Class
            - water_model: Instance of WaterModel CLass
            - pi: Initial Pressure [Psi]
            - swo: Water initial saturation [decimal]
            - cw: Water compressibility
            - cf: Total compressibility
            - aquifer: Instance of Aquifer Class
        """
        super().__init__(name=name,
                         wells=wells,
                         oil_model=oil_model,
                         water_model=water_model,
                         pi=pi,
                         swo=swo,
                         cw=cw,
                         cf=cf,
                         aquifer=aquifer)

    def _press_df_internal(self) -> pd.DataFrame:
        """
        Private method that internally manages the pressure vector for use in the UW method.

        :return:
            - pd.Dataframe: A pressure DataFrame with properties PVT of oil and water
        """
        df_press = pd.DataFrame()
        for well in self.wells:
            press_vector = well.press_data
            well_name = well.name
            tank_name = self.name
            if press_vector is not None:

                well_date = press_vector.data.index
                well_oil_fvf = self.oil_model.get_bo_at_press(press_vector.data[PRESSURE_COL])
                well_gas_fvf = self.oil_model.get_bg_at_press(press_vector.data[PRESSURE_COL])
                well_rs = self.oil_model.get_rs_at_press(press_vector.data[PRESSURE_COL])

                # In case properties are calculated using correlations
                if (self.water_model.salinity is not None
                        and self.water_model.temperature is not None
                        and self.water_model.unit is not None):
                    well_bw = self.water_model.get_bw_at_press(press_vector.data[PRESSURE_COL])
                    well_rs_w = self.water_model.get_rs_at_press(press_vector.data[PRESSURE_COL])

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

                df_press = pd.concat([df_press, temp_df_press], ignore_index=True)
        return df_press

    def get_pressure_df(self) -> pd.DataFrame:
        """
        Gets a DatFrame with pressure data using the private _press_df_internal method
        THIS METHOD IS MARKED PRIVATE FOR INTERNAL USE ONLY.

        :return:
            pd.Dataframe: DataFrame with PVT properties.
        """
        return self._press_df_internal()

    def _prod_df_internal(self) -> pd.DataFrame:
        """
        Private method that internally manages production vector for use in the UW method.

        :return:
            - pd.Dataframe: A production DataFrame

        """
        df_prod = pd.DataFrame()
        for well in self.wells:
            prod_vector = well.prod_data
            well_name = well.name
            tank_name = self.name
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

                df_prod = pd.concat([df_prod, temp_df_prod], ignore_index=True)
        return df_prod

    def get_production_df(self):
        """
        Gets a DataFrame with production data using the private _prod_df_internal method
        THIS METHOD IS MARKED PRIVATE FOR INTERNAL USE ONLY.

        :return:
            pd.DataFrame: A DataFrame with cumulative production
        """
        return self._prod_df_internal()
