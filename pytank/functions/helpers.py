"""
helpers.py

This module provides two functions that help create wells for analysis
purposes.

The functions in this module process production and pressure data, convert them
into appropriate formats, and create Well objects that encapsulate the data.

Libraries used:
    - pandas: For data manipulation and analysis.
    - pydantic: For data validation and settings management using Python type
    annotations.
    - pandera: For validating pandas DataFrames against schemas.
    - typing: For type hinting and annotations.
    - warnings: For issuing warnings when necessary.

Main Functions are:
    - create_wells: Creates a list of Well objects from production and pressure
    data.
    - search_wells: Searches for wells in the list based on provided well names.
"""
import pandas as pd
from typing import Optional, List
from pytank.constants.constants import (
    OIL_CUM_COL,
    WATER_CUM_COL,
    GAS_CUM_COL,
    LIQ_CUM,
    PRESSURE_COL,
    DATE_COL,
)
from pytank.vector_data import ProdVector, PressVector
from pandera.errors import SchemaError
from pytank.functions.utilities import normalize_date_freq
import warnings
from pytank.well import Well


def create_wells(
        df_prod: pd.DataFrame,
        df_press: pd.DataFrame,
        freq_prod: Optional[str] = None,
        freq_press: Optional[str] = None,
) -> List[Well]:
    """Creates a list of Well objects from production and pressure data.

    This function takes production and pressure data in the form of pandas
    DataFrames and converts them into Well objects. It also allows for
    optional frequency specifications for the data.

    Args:
        df_prod (pd.DataFrame): A DataFrame containing the production data,
            which should include relevant columns such as cumulative oil, water,
            and gas production.
        df_press (pd.DataFrame): A DataFrame containing the pressure data, which
            should include relevant pressure measurements.
        freq_prod (Optional[str]): Frequency of the production data
            (e.g., 'D' for daily). Can be None if the frequency is already
            correct.
        freq_press (Optional[str]): Frequency of the pressure data
            (e.g., 'D' for daily). This parameter is not necessary if the data
            is already at the correct frequency.

    Returns:
        List_Well:
            A list of Well objects, where each object represents a well with
            its associated pressure and production data.

    Raises:
        SchemaError:
            If the provided DataFrames do not conform to the expected schema
            for production or pressure data.
    """
    warnings.filterwarnings(
        "ignore", message="DataFrame.fillna with 'method' is deprecated"
    )

    def _process_data(df_prod: pd.DataFrame, df_press: pd.DataFrame) -> tuple:
        """Private internal method to handle production and pressure data.

        This method processes the provided production and pressure DataFrames,
        converting date columns to datetime format, setting the date as the
        index, and preparing the data for further analysis.

        Args:
            df_prod (pd.DataFrame): A DataFrame containing production data with
                date information.
            df_press (pd.DataFrame): A DataFrame containing pressure data with
                date information.

        Returns:
            Tuple_prod_press: :
                - pd.DataFrame: The processed production DataFrame with dates as
                the index.
                - pd.DataFrame: The processed pressure DataFrame with dates as
                the index.
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
                }
            )
            group_prod[LIQ_CUM] = group_prod[OIL_CUM_COL] + group_prod[
                WATER_CUM_COL]
            group_prod = group_prod[
                [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM]]

            # Normalize the frequency
            if freq_prod is not None:
                group_prod_norm = normalize_date_freq(
                    df=group_prod,
                    freq=freq_prod,
                    cols_fill_na=cols_fills_na,
                    method_no_cols="ffill",
                )
                try:
                    prod_vector = ProdVector(freq=freq_prod,
                                             data=group_prod_norm)
                except SchemaError as e:
                    expected_error_msg = (
                        'ValueError("Need at least 3 dates to ' 
                        'infer frequency")'
                    )
                    if str(e) == expected_error_msg:
                        group_prod.index.freq = freq_prod

                        # Create a production vector
                        prod_vector = ProdVector(freq=None,
                                                 data=group_prod_norm)

            else:
                prod_vector = ProdVector(freq=freq_prod, data=group_prod)

        if name in press_data["WELLBORE"].unique():
            group_press = press_data[press_data["WELLBORE"] == name]

            group_press = group_press.rename(
                columns={
                    PRESSURE_COL: PRESSURE_COL,
                }
            )
            group_press.set_index(DATE_COL, inplace=True)

            # Create a pressure vector
            press_vector = PressVector(freq=freq_press, data=group_press)

        # Create well lists
        info_well = Well(name_well=name, prod_data=prod_vector,
                         press_data=press_vector)

        # Add wells list to tanks dict
        list_wells.append(info_well)

    return list_wells


def search_wells(wells: List[Well], well_names: List[str]) -> List[Well]:
    """Searches for wells in the list based on the provided well names.

    This function filters the list of wells to return only those that match
    the specified well names. It also issues a warning for any well names
    that are not found in the provided list.

    Args:
        wells (List[Well]): A list of Well objects representing all available
            wells.
        well_names (List[str]): A list of well names to search for in the wells
            list.

    Returns:
        List_Well: A list of Well objects that match the provided well names.

    Raises:
        Warning:If any of the specified well names are not found in the list of
            wells.
    """
    result = [well for well in wells if well.name_well in well_names]

    # Well no found
    found_well_names = [well.name_well for well in result]
    not_found_wells = [name for name in well_names if
                       name not in found_well_names]
    # Warning
    if not_found_wells:
        warnings.warn(
            f"The following wells were not found in the list: "
            f"{', '.join(not_found_wells)}"
        )

    return result
