import pandas as pd
from typing import Optional, List
from pytank.constants.constants import (OIL_CUM_COL, WATER_CUM_COL,
                                        GAS_CUM_COL, LIQ_CUM, PRESSURE_COL,
                                        DATE_COL)
from pytank.vector_data import ProdVector, PressVector
from pandera.errors import SchemaError
from pytank.functions.utilities import normalize_date_freq
import warnings
from pytank.well import Well


def create_wells(df_prod: pd.DataFrame,
                 df_press: pd.DataFrame,
                 freq_prod: Optional[str] = None,
                 freq_press: Optional[str] = None) -> List[Well]:
    """
    Parameters
    ----------
    df_prod : pandas.DataFrame
        pd.DataFrame containing the production data.
    df_press : pandas.DataFrame
        pd.DataFrame containing the pressure data.
    freq_prod : str
        Frequency of the production data. Can be None if the frequency
        is correct.
    freq_press : str
        Frequency of the pressure data. It is not necessary.

    Returns
        -------
        List[Wells]
            A list of `Wells` objects, where each object represents a well
            with its associated pressure and production data.
    """
    warnings.filterwarnings(
        "ignore", message="DataFrame.fillna with 'method' "
                          "is deprecated")

    def _process_data(df_prod: pd.DataFrame, df_press: pd.DataFrame):
        """
        PRIVATE internal method to handle the production and pressure
        data (dates)
        :return:
            - Production DataFrame
            - Pressure DataFrame
        """
        prod_data = df_prod
        prod_data[DATE_COL] = pd.to_datetime(prod_data[DATE_COL])
        prod_data.set_index(prod_data[DATE_COL], inplace=True)

        press_data = df_press
        press_data[DATE_COL] = pd.to_datetime(press_data["DATE"])
        press_data = press_data.drop("DATE", axis=1)

        return prod_data, press_data

    prod_data, press_data = _process_data(df_prod, df_press)
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
            if freq_prod is not None:
                group_prod_norm = normalize_date_freq(
                    df=group_prod,
                    freq=freq_prod,
                    cols_fill_na=cols_fills_na,
                    method_no_cols="ffill")
                try:
                    prod_vector = ProdVector(freq=freq_prod,
                                             data=group_prod_norm)
                except SchemaError as e:
                    expected_error_msg = \
                        ('ValueError("Need at least 3 dates to '
                         'infer frequency")')
                    if str(e) == expected_error_msg:
                        group_prod.index.freq = freq_prod

                        # Create a production vector
                        prod_vector = ProdVector(freq=None,
                                                 data=group_prod_norm)

            else:
                prod_vector = ProdVector(freq=freq_prod,
                                         data=group_prod)

        if name in press_data["WELLBORE"].unique():
            group_press = press_data[press_data["WELLBORE"] == name]

            group_press = group_press.rename(columns={
                PRESSURE_COL: PRESSURE_COL,
            })
            group_press.set_index(DATE_COL, inplace=True)

            # Create a pressure vector
            press_vector = PressVector(freq=freq_press,
                                       data=group_press)

        # Create well lists
        info_well = Well(name=name,
                         prod_data=prod_vector,
                         press_data=press_vector)

        # Add wells list to tanks dict
        list_wells.append(info_well)

    return list_wells


def search_wells(wells: List[Well], well_names: List[str]) -> List[Well]:
    """
    Searches for wells in the list of all wells based on the provided well
    names.

    Parameters
    ----------
    wells: List of all wells
    well_names: List of well names to search for.

    Returns
    -------
    List[Wells]
        A list of `Wells` objects that match the provided well names.
    """
    result = [well for well in wells if well.name in well_names]

    # Well no found
    found_well_names = [well.name for well in result]
    not_found_wells = [name for name in well_names if name
                       not in found_well_names]
    # Warning
    if not_found_wells:
        warnings.warn(f"The following wells were not found in the list: "
                      f"{', '.join(not_found_wells)}")

    return result
