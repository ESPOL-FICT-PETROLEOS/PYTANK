"""
vector_data.py

This module defines the VectorData class for handling vector data with
specific validation schemas and date indices.

The logic is structured using classes and methods to provide a robust
framework for managing and validating vector data.

Libraries:
    - pandas: For data manipulation and analysis.
    - datetime: For handling date and time objects.
    - typing: For type hinting and annotations.
    - pydantic: For data validation and settings management using Python type
    annotations.
    - pandera: For validating pandas DataFrames against schemas.

The main Classes are:
    - VectorData: A class that encapsulates vector data handling, including
    validation and processing methods.

Usage:
    Import the VectorData class and create an instance with the appropriate
    data to leverage its functionalities for vector data management.
"""

import pandas as pd
from datetime import datetime
from typing import Any
from pydantic import BaseModel, PrivateAttr, validator
from pandera import DataFrameSchema
import pandera as pa
from pytank.functions.utilities import add_date_index_validation
from pytank.constants.constants import (
    PROD_SCHEMA,
    PRESS_SCHEMA,
    INJ_SCHEMA,
)


class VectorData(BaseModel):
    """Handles vector data with a specific validation scheme and date index.

    This class is designed to manage vector data, providing validation
    according to a defined schema and maintaining a date index. It includes
    parameters to indicate the nature of the data and its usage.

    Attributes:
        is_result (bool): Indicates whether the vector represents a result.
            Defaults to False.
        data_schema (DataFrameSchema): Validation scheme for the data, ensuring
            data integrity and structure.
        freq Optional(str|None): Frequency of the data, which can be a string
            representing time intervals.
        use_pressure (bool): Indicates whether pressure data is utilized.
            Defaults to False.
        data (Any): Container for the actual vector data.
        _start_date (datetime): Private attribute representing the start date of
            the data.
        _end_date (datetime): Private attribute representing the end date of the
            data.
    """

    is_result: bool = False
    data_schema: DataFrameSchema = DataFrameSchema()
    freq: str | None
    use_pressure: bool = False
    data: Any
    _start_date: datetime = PrivateAttr(None)
    _end_date: datetime = PrivateAttr(None)

    class Config:
        arbitrary_types_allowed = True

    @validator("data")
    def validate_data(cls, v, values) -> data_schema:
        """Validates the dates against the specified schema.

        This class method ensures that the input data conforms to the expected
        schema. It performs validations on the dates and other relevant fields
        to maintain data integrity.

        Args:
            v (Any): The value to be validated.
            values (dict): A dictionary containing the field values.

        Returns:
            DataSchema: The validated data schema.

        Raises:
            ValueError: If the input data does not match the expected schema.
        """
        new_schema = add_date_index_validation(values["data_schema"],
                                               values["freq"])

        cls.data_schema = new_schema
        return new_schema.validate(v)

    @property
    def start_date(self) -> datetime:
        """Gets the start date.

        This property method returns the start date associated with the vector
        data.

        Returns:
            date: The start date of the vector data.
        """
        if self._start_date is None:
            self._start_date = self.data.index.min()
        return self._start_date

    @property
    def end_date(self) -> datetime:
        """Gets the end date.

        This property method returns the end date associated with the vector
        data.
        If the end date is not explicitly set, it is calculated as the maximum
        date from the data index.

        Returns:
            date: The end date of the vector data.
        """
        if self._end_date is None:
            self._end_date = self.data.index.max()
        return self._end_date

    def equal_date_index(self, other) -> bool:
        """Compares the date indices of two VectorData objects.

        This method checks if the date indices of the current VectorData object
        and the provided `other` VectorData object are equal. It ensures that
        both objects have the same date range and frequency.

        Args:
            other (VectorData): The VectorData object to compare with.

        Returns:
            bool: True if the date indices are equal, False otherwise.
        """
        return all(
            [
                self.start_date == other.start_date,
                self.end_date == other.end_date,
                self.freq == other.freq,
            ]
        )

    def get_date_index(self) -> pd.DatetimeIndex:
        """Retrieves the date index of the data.

        This method returns the date index associated with the vector data.

        Returns:
            DatetimeIndex: The date index of the data.
        """
        return self.data.index

    def _eq_(self, other):
        """Compares two VectorData objects for equality.

        This method checks if two VectorData objects have the same data schema,
        start date, and end date.

        Args:
            other (VectorData): The VectorData object to compare with.

        Returns:
            bool: True if the VectorData objects are equal, False otherwise.
        """
        return all(
            [
                self.data_schema == other.data_schema,
                self.start_date == other.start_date,
                self.end_date == other.end_date,
            ]
        )

    def _len_(self):
        """Gets the length of the data.

        This method returns the number of entries in the vector data.

        Returns:
            int: The length of the data.
        """
        return len(self.data)

    def _add_(self, other):
        """Allows the addition of two VectorData objects or a VectorData with a
        number or a series.

        This method handles the addition of two VectorData objects, ensuring
        that the data is combined correctly based on the type of the other
        operand.

        Args:
            other (Union[VectorData, int, float, pd.Series]): The object to add
                to the current VectorData.

        Returns:
            VectorData: A new VectorData object containing the result of the
                addition.

        Raises:
            ValueError: If the date indices of the two VectorData objects are
                not equal.
        """
        if isinstance(other, VectorData):
            if self == other:
                # If the two VectorData have the same schema, then we
                # can just add them together using a groupby sum on
                # the date index
                new_data = (pd.concat([self.data, other.data]).groupby(level=0)
                            .sum())
                return VectorData(
                    data_schema=self.data_schema,
                    freq=self.freq,
                    # use_pressure=self.use_pressure,
                    data=new_data,
                )
            elif self.equal_date_index(other):
                # If the two VectorData have the same date index, but different
                # schemas, then we need to add them together using a concat
                # on thecolumns that are in neither dataframe and a groupby
                # sum on the columnsthat are in both dataframes
                common_cols = self.data.columns.intersection(other.data.columns)
                left_cols = self.data.columns.difference(other.data.columns)
                right_cols = other.data.columns.difference(self.data.columns)
                new_data_common = pd.DataFrame()
                new_data_left = pd.DataFrame()
                new_data_right = pd.DataFrame()
                if len(common_cols) > 0:
                    new_data_common = (
                        pd.concat([self.data[common_cols], other
                                  .data[common_cols]])
                        .groupby(level=0)
                        .sum()
                    )
                if len(left_cols) > 0:
                    new_data_left = self.data[left_cols]
                if len(right_cols) > 0:
                    new_data_right = other.data[right_cols]

                new_data = pd.concat(
                    [new_data_common, new_data_left, new_data_right],
                    axis=1
                )
                return VectorData(
                    data_schema=pa.infer_schema(new_data),
                    freq=self.freq,
                    # use_pressure=self.use_pressure,
                    data=new_data,
                )
            else:
                raise ValueError(
                    "The date index of the two VectorData objects are not equal"
                )
        elif isinstance(other, (int, float)):
            new_data = self.data + other
            return VectorData(
                data_schema=self.data_schema,
                freq=self.freq,
                # use_pressure=self.use_pressure,
                data=new_data,
            )
        elif isinstance(other, pd.Series):
            if len(self) == len(other):
                new_data = self.data + other
                return VectorData(
                    data_schema=self.data_schema,
                    freq=self.freq,
                    # use_pressure=self.use_pressure,
                    data=new_data,
                )

    def _radd_(self, other):
        """Reverse addition to allow addition of a number with a VectorData.

        This method enables the addition of a number to a VectorData object,
        allowing for expressions like `number + vector_data`.

        Args:
            other (Union[int, float]): The number to add to the VectorData.

        Returns:
            VectorData: A new VectorData object resulting from the addition.
        """
        return self.add(other)


class ProdVector(VectorData):
    """Handles production data with a specific schema.

    This class extends the VectorData class to manage production data,
    ensuring that the data adheres to the defined production schema.

    Attributes:
        data_schema (DataFrameSchema): The schema that defines the structure
            and validation rules for the production data.
    """

    data_schema: DataFrameSchema = PROD_SCHEMA


class PressVector(VectorData):
    """Handles pressure data with a specific schema.

    This class extends the VectorData class to manage pressure data,
    ensuring that the data adheres to the defined pressure schema.

    Attributes:
        data_schema (DataFrameSchema): The schema that defines the structure
            and validation rules for the pressure data.
    """

    data_schema: DataFrameSchema = PRESS_SCHEMA


class InjVector(VectorData):
    """Handles injection data with a specific schema.

    This class extends the VectorData class to manage injection data,
    ensuring that the data adheres to the defined injection schema.

    Attributes:
        data_schema (DataFrameSchema): The schema that defines the structure
            and validation rules for the injection data.
    """

    data_schema: DataFrameSchema = INJ_SCHEMA
