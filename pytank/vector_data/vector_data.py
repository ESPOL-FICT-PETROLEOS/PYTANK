"""
vector_data.py

This module defines the VectorData Class for handling vector data with specific validations schemas /
and date indices.

The logic is structured using classes and methods.

libraries:
    - pandas
    - datetime
    - typing
    - pydantic
    - pandera
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
    """
    Class used to handle vector data with a specific validation scheme and date index.

    :parameter:
        - is_result: Indicates whether the vector is a result.
        - data_schema: Validation scheme for the data.
        - freq (str): Frequency of the data.
        - use_pressure: Indicates whether the pressure is used.
        - data: Data container.
        - _start_date and _end_date: Private start and end dates.
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
    def validate_data(cls, v, values):
        """
        Validate the dates with the specific scheme
        :param
            - v:
            - values:
        :return:
            - data_schema
        """
        new_schema = add_date_index_validation(values["data_schema"], values["freq"])

        cls.data_schema = new_schema
        return new_schema.validate(v)

    @property
    def start_date(self):
        """
        :return:
            - start date
        """
        if self._start_date is None:
            self._start_date = self.data.index.min()
        return self._start_date

    @property
    def end_date(self):
        """
        :return:
            - end date
        """
        if self._end_date is None:
            self._end_date = self.data.index.max()
        return self._end_date

    def equal_date_index(self, other) -> bool:
        """
        Compare the vector_data objects

        :param other:

        :return:
        A comparative
        """
        return all(
            [
                self.start_date == other.start_date,
                self.end_date == other.end_date,
                self.freq == other.freq,
            ]
        )

    def get_date_index(self) -> pd.DatetimeIndex:
        """
        :return:
            - Date index of data
        """
        return self.data.index

    def _eq_(self, other):
        """
        Compare two VectorDara Objects
        """
        return all(
            [
                self.data_schema == other.data_schema,
                self.start_date == other.start_date,
                self.end_date == other.end_date,
            ]
        )

    def _len_(self):
        """
        :return:
            - The length of the data
        """
        return len(self.data)

    def _add_(self, other):
        """
        Allows the addition of two VectorData objects or a VectorData with a number or a series.
        """
        if isinstance(other, VectorData):
            if self == other:
                """If the two VectorData have the same schema, then we can just add
                them together using a groupby sum on the date index"""
                new_data = pd.concat([self.data, other.data]).groupby(level=0).sum()
                return VectorData(
                    data_schema=self.data_schema,
                    freq=self.freq,
                    # use_pressure=self.use_pressure,
                    data=new_data,
                )
            elif self.equal_date_index(other):
                """If the two VectorData have the same date index, but different
                schemas, then we need to add them together using a concat on the
                columns that are in neither dataframe and a groupby sum on the columns
                that are in both dataframes"""
                common_cols = self.data.columns.intersection(other.data.columns)
                left_cols = self.data.columns.difference(other.data.columns)
                right_cols = other.data.columns.difference(self.data.columns)
                new_data_common = pd.DataFrame()
                new_data_left = pd.DataFrame()
                new_data_right = pd.DataFrame()
                if len(common_cols) > 0:
                    new_data_common = (
                        pd.concat([self.data[common_cols], other.data[common_cols]])
                        .groupby(level=0)
                        .sum()
                    )
                if len(left_cols) > 0:
                    new_data_left = self.data[left_cols]
                if len(right_cols) > 0:
                    new_data_right = other.data[right_cols]

                new_data = pd.concat(
                    [new_data_common, new_data_left, new_data_right], axis=1
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
        """
        Reverse addition to allow addition of a number with a VectorData.
        """
        return self.add(other)


class ProdVector(VectorData):
    """
    This class is used to handle production data with a specific scheme.
    """
    data_schema: DataFrameSchema = PROD_SCHEMA


class PressVector(VectorData):
    """
    This class is used to handle pressure data with a specific scheme.
    """
    data_schema: DataFrameSchema = PRESS_SCHEMA


class InjVector(VectorData):
    """
    This class is used to handle injection data with a specific scheme.
    """
    data_schema: DataFrameSchema = INJ_SCHEMA
