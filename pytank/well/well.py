"""
well.py

This module defines the Well Class to group production and pressure
information per well.

The logic is structured using classes and methods.

"""
import pandas as pd
from pydantic import BaseModel
from typing import Optional
from pytank.constants.constants import (OIL_CUM_COL, WATER_CUM_COL,
                                        GAS_CUM_COL, LIQ_CUM, PRESSURE_COL,
                                        DATE_COL)
from pytank.vector_data.vector_data import ProdVector, PressVector
from pandera.errors import SchemaError
from pytank.functions.utilities import normalize_date_freq
import warnings


class _Well(BaseModel):
    """
    PRIVATE Class used to handle pressure and production vectors
    """
    name: str
    prod_data: Optional[ProdVector] = None
    press_data: Optional[PressVector] = None


class Wells(BaseModel):
    """
    Class to assign the respective production and pressure data to each well
    Attributes
    ----------
    freq_prod : Optional[str]
        Frequency of the production data. Can be None if the frequency is
        correct.
    freq_press : Optional[str]
        Frequency of the pressure data. It is not necessary.
    df_prod : pandas.DataFrame
        pd.Dataframe containing the production data.
    df_press : pandas.DataFrame
        pd.Dataframe containing the pressure data.
    """
    freq_prod: Optional[str] = None
    freq_press: Optional[str] = None
    df_prod: pd.DataFrame
    df_press: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True

    warnings.filterwarnings(
        "ignore", message="DataFrame.fillna with 'method' "
                          "is deprecated")

    def __init__(self,
                 df_prod: pd.DataFrame,
                 df_press: pd.DataFrame,
                 freq_prod: str = None,
                 freq_press: str = None):
        """
        Initializes the attributes of the Wells class.

        Parameters
        ----------
        df_prod : pandas.DataFrame
            pd.DataFrame containing the production data.
        df_press : pandas.DataFrame
            pd.DataFrame containing the pressure data.
        freq_prod : str, optional
            Frequency of the production data. Can be None if the frequency
            is correct.
        freq_press : str, optional
            Frequency of the pressure data. It is not necessary.
        """
        super().__init__(df_prod=df_prod,
                         df_press=df_press,
                         freq_prod=freq_prod,
                         freq_press=freq_press)

    def _process_data(self):
        """
        PRIVATE internal method to handle the production and pressure
        data (dates)
        :return:
            - Production DataFrame
            - Pressure DataFrame
        """
        prod_data = self.df_prod
        prod_data[DATE_COL] = pd.to_datetime(prod_data[DATE_COL])
        prod_data.set_index(prod_data[DATE_COL], inplace=True)

        press_data = self.df_press
        press_data[DATE_COL] = pd.to_datetime(press_data["DATE"])
        press_data = press_data.drop("DATE", axis=1)

        return prod_data, press_data

    def get_wells(self) -> list:
        """
        Creates a list of wells with corresponding pressure and production
        data (vectors).

        Returns
        -------
        List[Wells]
            A list of `Wells` objects, where each object represents a well
            with its associated pressure and production data.
        """
        prod_data, press_data = self._process_data()
        cols_fills_na = [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM]
        all_wells = set(prod_data["ITEM_NAME"]).union(press_data["WELLBORE"])
        list_wells = []

        for name in all_wells:
            prod_vector = None
            press_vector = None

            if name in prod_data["ITEM_NAME"].unique():
                group_prod = prod_data[prod_data["ITEM_NAME"] == name]

                group_prod = group_prod.rename(
                    columns={
                        OIL_CUM_COL: OIL_CUM_COL,
                        WATER_CUM_COL: WATER_CUM_COL,
                        GAS_CUM_COL: GAS_CUM_COL,
                    })
                group_prod[LIQ_CUM] = group_prod[OIL_CUM_COL] + group_prod[
                    WATER_CUM_COL]
                group_prod = group_prod[[
                    OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM
                ]]

                # Normalize the frequency
                if self.freq_prod is not None:
                    group_prod_norm = normalize_date_freq(
                        df=group_prod,
                        freq=self.freq_prod,
                        cols_fill_na=cols_fills_na,
                        method_no_cols="ffill")
                    try:
                        prod_vector = ProdVector(freq=self.freq_prod,
                                                 data=group_prod_norm)
                    except SchemaError as e:
                        expected_error_msg = \
                            ('ValueError("Need at least 3 dates to '
                             'infer frequency")')
                        if str(e) == expected_error_msg:
                            group_prod.index.freq = self.freq_prod

                            # Create a production vector
                            prod_vector = ProdVector(freq=None,
                                                     data=group_prod_norm)
                    # tank_name = group_prod_norm[TANK_COL].iloc[0]

                else:
                    prod_vector = ProdVector(freq=self.freq_prod,
                                             data=group_prod)
                    # tank_name = group_prod[TANK_COL].iloc[0]

            if name in press_data["WELLBORE"].unique():
                group_press = press_data[press_data["WELLBORE"] == name]

                group_press = group_press.rename(columns={
                    PRESSURE_COL: PRESSURE_COL,
                })
                group_press.set_index(DATE_COL, inplace=True)

                # Create a pressure vector
                press_vector = PressVector(freq=self.freq_press,
                                           data=group_press)
                # if prod_vector is None and TANK_COL in group_press.columns:
                # tank_name = group_press[TANK_COL].iloc[0]

            # Create well lists
            info_well = _Well(name=name,
                              prod_data=prod_vector,
                              press_data=press_vector)

            # Add wells list to tanks dict
            list_wells.append(info_well)

        return list_wells

    def search_wells(self, your_wells: list) -> list:
        """
        Searches for wells in the list of all wells based on the provided well
        names.

        Parameters
        ----------
        your_wells : List[str]
            A list of well names to search for.

        Returns
        -------
        List[Wells]
            A list of `Wells` objects that match the provided well names.
        """
        well_base = self.get_wells()
        result = [well for well in well_base if well.name in your_wells]
        return result
