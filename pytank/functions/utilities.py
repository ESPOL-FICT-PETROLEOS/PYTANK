"""
utilities.py

This module contains several functions that are helpful for other functions
and classes in the library.

Libraries:
    - calendar: Provides functions related to the calendar.
    - datetime: Supplies classes for manipulating dates and times.
    - pandera: A library for validating pandas DataFrames.
    - pandas: For data manipulation and analysis.
    - numpy: For numerical operations and handling arrays.
    - typing: Supports type hints for better code clarity.
"""

import datetime
import pandas as pd
import numpy as np
from pandera import Column, Check, DataFrameSchema
from pytank.constants.constants import DATE_COL, VALID_FREQS, PRESSURE_COL
from typing import Union, Optional, Sequence
from calendar import monthrange


def days_in_month(date):
    if isinstance(date, datetime.datetime):
        return monthrange(date.year, date.month)[1]
    else:
        raise ValueError("Argument is not of type datetime")


def interp_from_dates(
    date_interp: datetime.datetime,
    x_dates: list,
    y_values: list,
    left: float = None,
    right: float = None
):
    """Interpolation function that accepts dates as x to interpolate between y_values, given a datetime object between x_dates.

    This function performs linear interpolation on y_values based on the provided x_dates and a specified date to interpolate.

    Parameters:
        date_interp (datetime.datetime or array-like):
            The datetime object or array of datetime objects to interpolate.
        x_dates (array-like of datetime objects):
            The x_dates values to use for interpolation.
        y_values (array-like):
            The y_values to use for interpolation.
        left (float or complex):
            Value to return for x < x_dates[0]. Default is y_values[0].
        right (float or complex):
            Value to return for x > x_dates[-1]. Default is y_values[-1].

    Returns:
        dates (float or ndarray):
            An interpolated value or values between y_values.
    """

    # Type checking before proceeding with operations
    permitted_arrays = (list, np.ndarray, pd.Series)
    if isinstance(date_interp, permitted_arrays):
        is_array = True
        if not all(isinstance(x, datetime.datetime) for x in date_interp):
            raise ValueError("date_interp should only contain datetime objects")
    else:
        is_array = False
        if not isinstance(date_interp, datetime.datetime):
            raise ValueError(f"{date_interp} is not a datetime object")

    if isinstance(x_dates, permitted_arrays):
        if not all(isinstance(x, datetime.datetime) for x in x_dates):
            raise ValueError("x_dates should only contain datetime objects")
    else:
        raise ValueError("x_dates should be a list, numpy array or pandas Series")

    if not isinstance(y_values, permitted_arrays):
        raise ValueError("y_values should be a list, numpy array or pandas Series")

    # The handling of numeric values in y_values should be handled by np
    # itself in the interpolation function

    # Get the minimum date in x_dates as the reference
    start_date = x_dates.min()
    # Calculate time deltas using x_dates and the start dates,
    # then convert to seconds
    time_deltas = pd.Series(x_dates - start_date).dt.total_seconds()

    if is_array:
        # do the same for date_interp values
        new_time_delta = pd.Series(date_interp - start_date).dt.total_seconds()
    else:
        new_time_delta = (date_interp - start_date).total_seconds()

    return np.interp(new_time_delta, time_deltas, y_values, left=left, right=right)


def interp_dates_row(
    row: pd.Series,
    x_result_col: str,
    df_input: pd.DataFrame,
    x_input_col: str,
    y_input_col: str,
    input_cond_col_name: str,
    result_cond_col_name: str,
    left: float = None,
    right: float = None
):
    """A helper function that works on data frame rows using the apply method.
    This function creates an interpolation using interp_from_dates whose input
    values would change based on a condition specified in the target data frame.

    Parameters:
        row (pd.Series): A row from the DataFrame, usually used with apply
            method, axis=1.
        x_result_col (str): The x value column name to interpolate in the target
            row.
        df_input (pd.DataFrame): The input DataFrame that will be used for
            regression.
        x_input_col (str): The x column name in the input DataFrame.
        y_input_col (str): The y column name in the input DataFrame.
        input_cond_col_name (str): The condition column name in the input
            DataFrame.
        result_cond_col_name (str): The condition column name in the result
            DataFrame.
        left (optional, float): Value to return for x < x_dates[0], default is
            y_values[0].
        right (optional, float): Value to return for x > x_dates[-1], default is
            y_values[-1].

    Returns:
        dates_row (float): Returns an interpolated value of float type.
    """

    # Filter the input data frame according to group name
    df_input_filt = df_input.loc[
        df_input[input_cond_col_name] == row[result_cond_col_name]
    ]

    if len(df_input_filt) == 0:
        return np.nan
    else:
        return interp_from_dates(
            row[x_result_col],
            df_input_filt[x_input_col],
            df_input_filt[y_input_col],
            left=left,
            right=right,
        )


def material_bal_var_type(data: pd.DataFrame, numb_or_column: dict) -> (
        pd.DataFrame):
    """Function to check the data types of the material balance equation terms.

    This function takes a pandas DataFrame and a dictionary containing column
    names to check their data types. It ensures that the specified columns have
    numeric data types.

    Parameters:
        data (pd.DataFrame): A pandas DataFrame containing the production
            information for a single entity.
        numb_or_column (dict): A Python dictionary containing the names of some
            columns of the DataFrame to check their data types.

    Returns:
        mb_type: The original pandas DataFrame.
    """
    # Make a copy of the original dataframe
    df = data.copy()
    if not isinstance(data, pd.DataFrame):
        raise TypeError("The input data should be a pandas dataframe")

    # Define internal names for column in the DataFrame
    for col, arg in numb_or_column.items():
        if isinstance(arg, (int, float)):
            df[col] = arg
            numb_or_column[col] = col
        elif isinstance(arg, str):
            df.rename(columns={arg: col}, inplace=True)
        else:
            raise TypeError(
                f"{arg} should be either a numeric value or string "
                f"indicating a column in the DataFrame"
            )

    return df


def material_bal_numerical_data(vector) -> None:
    """Function to check the numerical data types of the arguments of the
    material balance dataframes.

    This function checks whether each element in the provided list or array is
    of type int or float. If any element is not of the correct type, a TypeError
    is raised.

    Parameters:
        vector (list or numpy.ndarray): A list or array of numerical arguments
            for each function, containing the production information for a
            single entity.

    Raises:
        TypeError: If any element in the vector is not an int or float.
    """
    for value in vector:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{value} should be either an int or float")


def variable_type(obj) -> np.ndarray:
    """Converts the input variable to a NumPy array.

    This function checks the type of the input variable and converts it to a
    NumPy array if it is a list or a float. If the input is already a NumPy
    array, it is returned as is. If the input is of an unsupported type, a
    ValueError is raised.

    Attributes:
        obj: Variable to be converted to an array. It may be a list, float, or
            a NumPy array.

    Returns:
        var_type: A NumPy array if obj is entered in the correct data format.

    Raises:
        ValueError: If obj is not a float, list, or NumPy array.
    """
    if isinstance(obj, np.ndarray):
        array = obj
    elif isinstance(obj, list):
        array = np.array(obj)
    elif isinstance(obj, float):
        array = np.array(obj)
    else:
        raise ValueError("Please enter measured values as float, list or array")
    return array


def add_date_index_validation(
    base_schema: DataFrameSchema,
    freq: str = None
) -> DataFrameSchema:
    """Add a date index validation to a base schema.

    This function adds a date column to the provided base schema and sets it as
    the index. If a frequency is specified, it validates that the date column
    has the specified frequency. If no frequency is provided, it adds the date
    column without validation.

    Parameters:
        base_schema (DataFrameSchema):
            The base schema to which the date index validation will be added.
        freq (str, optional):
            The frequency that the date index should have. If None, no
            validation is applied.

    Returns:
        DataFrameSchema:
            The updated DataFrame schema with the date index validation added.

    Raises:
        ValueError:
            If freq is provided and is not one of the valid frequencies.
    """
    if freq is None:
        # iF freq is None, we just add a date column without validation
        new_schema = base_schema.add_columns(
            {
                DATE_COL: Column(
                    pd.Timestamp,
                    coerce=True,
                    nullable=False,
                    name=None,
                )
            }
        ).set_index([DATE_COL])

        return new_schema

    if freq not in VALID_FREQS:
        raise ValueError(f"freq must be one of {VALID_FREQS}, not {freq}")

    new_schema = base_schema.add_columns(
        {
            DATE_COL: Column(
                pd.Timestamp,
                Check(
                    lambda s: pd.infer_freq(s) == freq,
                    name="DateTimeIndex frequency check",
                    error=f"DateTimeIndex must have frequency '{freq}'",
                ),
                coerce=True,
                nullable=False,
                name=None,
            )
        }
    ).set_index([DATE_COL])

    return new_schema


def add_pressure_validation(base_schema: DataFrameSchema) -> DataFrameSchema:
    """Add a pressure column validation to a base schema.

    This function adds a pressure column to the provided base schema and
    validates that the values in this column are non-negative. The pressure
    column is specified to be of type float and is marked as non-nullable.

    Parameters:
        base_schema (DataFrameSchema):
            The base schema to which the pressure column validation will be
            added.

    Returns:
        DataFrameSchema:
            The updated DataFrame schema with the pressure column validation
            added.
    """
    new_schema = base_schema.add_columns(
        {
            PRESSURE_COL: Column(
                float,
                Check(lambda s: s >= 0),
                coerce=True,
                nullable=False,
                name=None,
                title="Bottom hole pressure",
            )
        }
    )

    return new_schema
    pass


def normalize_date_freq(
    df: Union[pd.DataFrame, pd.Series],
    freq: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    cols_fill_na: Optional[Sequence[str]] = None,
    method_no_cols: Optional[str] = None,
    fill_na: Union[int, float] = np.nan,
):
    """Returns a DataFrame or Series with a DateTimeIndex that has a predefined
    frequency.

    This function ensures that the index of the input DataFrame or Series has a
    consistent frequency. It re-indexes the DataFrame or Series to the specified
    frequency, filling missing values as needed.

    Parameters:
        df (pd.DataFrame or pd.Series):
            A pandas DataFrame or Series whose index is of type DateTimeIndex.
        freq (str):
            A string representing the target frequency for the DataFrame or
            Series.
        start_date (str, optional):
            Specify the start date to reindex the dates. If not specified, the
            earliest date in the index will be used.
        end_date (str, optional):
            Specify the end date to reindex the dates. If not specified, the
            latest date in the index will be used.
        cols_fill_na (Sequence[str], optional):
            Columns to fill with values specified in the fill_na argument.
        method_no_cols (str, optional):
            The method to use for columns not specified in cols_fill_na. The
            options are passed to the pandas.reindex method.
        fill_na (int or float, default nan):
            Value to use for missing values after the reindexing.

    Returns:
        norm_dates (pd.DataFrame or pd.Series):
            The DataFrame or Series with the index re-indexed to the specified
            frequency.
    """

    if isinstance(df, (pd.DataFrame, pd.Series)):
        if isinstance(df.index, pd.DatetimeIndex):
            # Check for duplicate values in index
            if len(df.index) != len(set(df.index)):
                error_message = (
                    f"The DateTimeIndex contains duplicate "
                    f"values\n Please, provide dates that are "
                    f"unique for each production information\n "
                    f"Printing the first rows of the dataframe:\n"
                    f" {df.head()}"
                )
                raise IndexError(error_message)
            # First we need to sort the dataframe based on its index
            # to get the start and end dates, just in case.
            sorted_df: pd.DataFrame = df.sort_index()
            start_date_n = (
                sorted_df.index[0] if start_date is None else pd.to_datetime(start_date)
            )
            end_date_n = (
                sorted_df.index[-1] if end_date is None else pd.to_datetime(end_date)
            )
        else:
            raise IndexError(
                "The index in the DataFrame or Series should be a "
                "DateTimeIndex object"
            )
    else:
        raise TypeError("First argument should be a pandas DataFrame or Series")

    new_index = pd.date_range(start_date_n, end_date_n, freq=freq, name=df.index.name)
    if cols_fill_na is not None:
        # First reindex the columns that are specified in the cols_fill_na
        # argument
        # These columns will default to nan where pytank dates appear,
        # and will be replaced with the fill_na value
        df_cols = (
            sorted_df[cols_fill_na]
            .reindex(new_index, fill_value=fill_na)
            .fillna(method=method_no_cols)
            .reset_index()
        )
        # Reindex the remaining columns, this time by using the method_co_cols
        # argument as input argument to reindex 'method' argument.
        df_no_cols = (
            sorted_df[sorted_df.columns.difference(cols_fill_na)]
            .reindex(new_index, method=method_no_cols)
            .reset_index(drop=True)
        )

        df_concat = pd.concat([df_cols, df_no_cols], axis=1)
        df_concat.set_index(df.index.name, inplace=True)
        # Use the same column order as the original dataframe
        df_concat = df_concat[df.columns]
        return df_concat
    else:
        return sorted_df.reindex(new_index, fill_value=fill_na)
