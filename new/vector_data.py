import pandas as pd
from datetime import datetime, timedelta
from typing import Any
from pydantic import BaseModel, validator, PrivateAttr
from pandera import DataFrameSchema
import pandera as pa
from new.utilities import add_date_index_validation, add_pressure_validation
import matplotlib.pyplot as plt
import numpy as np
from new.constants import (
    well_col,
    oil_cum_col,
    water_cum_col,
    gas_cum_col,
    press_col,
    injection_water,
    PROD_SCHEMA,
    INJ_SCHEMA,
)


class VectorData(BaseModel):
    is_result: bool = False
    data_schema: DataFrameSchema = DataFrameSchema()
    freq: str
    use_pressure: bool = False
    data: Any
    _start_date: datetime = PrivateAttr(None)
    _end_date: datetime = PrivateAttr(None)

    class Config:
        arbitrary_types_allowed = True

    @validator("data")
    def validate_data(cls, v, values):
        new_schema = add_date_index_validation(values["data_schema"], values["freq"])

        if values["use_pressure"]:
            new_schema = add_pressure_validation(new_schema)

        cls.data_schema = new_schema
        return new_schema.validate(v)

    @property
    def start_date(self):
        if self._start_date is None:
            self._start_date = self.data.index.min()
        return self._start_date

    @property
    def end_date(self):
        if self._end_date is None:
            self._end_date = self.data.index.max()
        return self._end_date

    def equal_date_index(self, other) -> bool:
        return all(
            [
                self.start_date == other.start_date,
                self.end_date == other.end_date,
                self.freq == other.freq,
            ]
        )

    def get_date_index(self) -> pd.DatetimeIndex:
        return self.data.index

    def _eq_(self, other):
        return all(
            [
                self.data_schema == other.data_schema,
                self.start_date == other.start_date,
                self.end_date == other.end_date,
            ]
        )

    def _len_(self):
        return len(self.data)

    def _add_(self, other):
        if isinstance(other, VectorData):
            if self == other:
                """If the two VectorData have the same schema, then we can just add
                them together using a groupby sum on the date index"""
                new_data = pd.concat([self.data, other.data]).groupby(level=0).sum()
                return VectorData(
                    data_schema=self.data_schema,
                    freq=self.freq,
                    use_pressure=self.use_pressure,
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
                    use_pressure=self.use_pressure,
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
                use_pressure=self.use_pressure,
                data=new_data,
            )
        elif isinstance(other, pd.Series):
            if len(self) == len(other):
                new_data = self.data + other
                return VectorData(
                    data_schema=self.data_schema,
                    freq=self.freq,
                    use_pressure=self.use_pressure,
                    data=new_data,
                )

    def _radd_(self, other):
        return self._add_(other)


class ProdVector(VectorData):
    data_schema: DataFrameSchema = PROD_SCHEMA

    def get_well_name(self) -> pd.Series:
        return self.data[well_col]

    def get_oil_cum(self) -> pd.Series:
        return self.data[oil_cum_col]

    def get_water_cum(self) -> pd.Series:
        return self.data[water_cum_col]

    def get_gas_cum(self) -> pd.Series:
        return self.data[gas_cum_col]

    def plot_oil_cum(self, ax=None, **kwards):
        if ax is None:
            ax = plt.gca()

        self.get_oil_cum().plot(ax=ax, **kwards)
        ax.set_ylabel("Oil Cumulative (STB)")
        ax.set_xlabel("Date")

    def calculate_rates_oil(self):
        dates = self.data.index
        cumulative_production = self.data[oil_cum_col].diff()

        # changes in dates
        time_change = dates.to_series().diff() / timedelta(days=1)

        # Calculate oil rate
        rate = cumulative_production / time_change

        return rate

    def plot_water_cum(self, ax=None, **kwards):
        if ax is None:
            ax = plt.gca()

        self.get_water_cum().plot(ax=ax, **kwards)
        ax.set_ylabel("Water Cumulative (STB)")
        ax.set_xlabel("Date")

    # Dentro de esta clase, tambien se ponen las columnas que nosotros esperamos obtener?


class PressVector(VectorData):
    data_schema: DataFrameSchema = press_col

    def get_pressure_datum(self) -> pd.Series:
        return self.data[press_col]

    def plot_pressure_vs_date(self, ax=None, **kwargs):
        if ax is None:
            ax = plt.gca()

        self.get_pressure_datum().plot(ax=ax, **kwargs)
        ax.set_ylabel("Pressure (PSI)")
        ax.set_xlabel("Date")


class InjVector(VectorData):
    data_schema: DataFrameSchema = INJ_SCHEMA

    def get_well_inj_name(self) -> pd.Series:
        return self.data[well_col]

    def get_water_volume(self) -> pd.Series:
        return self.data[injection_water]