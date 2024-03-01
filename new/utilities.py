import numpy as np
from pandera import Column, Check, DataFrameSchema
import pandas as pd

# from new.constants import date_col, VALID_FREQS, press_col

date_col = "date_col"
VALID_FREQS = ["D", "W", "M", "Q", "A"]


def add_date_index_validation(
    base_schema: DataFrameSchema, freq: str
) -> DataFrameSchema:
    """Add a date index validation to a base schema."""
    if freq not in VALID_FREQS:
        raise ValueError(f"freq must be one of {VALID_FREQS}, not {freq}")

    new_schema = base_schema.add_columns(
        {
            date_col: Column(
                # Use a lambda function for coercion
                lambda s: pd.to_datetime(s),
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
    ).set_index([date_col])

    return new_schema


# Definir el vector de fechas
date_vector = [
    "9/8/2005",
    "9/24/1987",
    "9/21/2006",
    "9/19/2006",
    "8/9/1995",
    "8/28/2018",
    "8/15/1981",
    "8/10/2011",
    "8/1/1988",
    "7/31/2008",
    "7/29/2008",
    "6/30/2018",
    "6/22/1997",
    "6/21/1995",
    "6/11/2019",
    "5/29/2019",
    "5/27/2019",
    "5/25/2002",
    "5/15/2012",
    "5/13/1993",
    "4/9/2019",
    "4/25/2019",
    "4/23/2019",
    "3/8/2019",
    "3/8/2019",
    "3/30/1993",
    "3/24/2019",
    "3/21/2019",
    "3/14/2019",
    "3/13/2019",
    "3/12/1998",
    "3/10/1998",
    "2/9/2019",
    "2/2/1987",
    "2/17/2019",
    "2/13/1996",
    "12/5/2010",
    "12/3/2002",
    "12/26/2011",
    "12/23/2006",
    "11/6/2002",
    "11/26/2005",
    "11/16/2003",
    "10/8/2018",
    "10/6/2018",
    "10/24/1981",
    "1/7/2011",
    "1/6/2019",
    "1/30/2019",
    "1/27/1994",
    "1/21/2019",
    "1/19/1984",
    "1/18/2012",
    "1/11/2012",
]

df = pd.DataFrame({date_col: date_vector})
base_schema = DataFrameSchema({date_col: Column(pd.Timestamp)})
freq = "M"
new_schema = add_date_index_validation(base_schema, freq)

validated_df = new_schema.validate(df)
print(validated_df)
