"""
pvt_interp.py

This module containing a function that allows interpolated some column of
PVT properties

libraries:
    - pandas
    - scipy
"""

import pandas as pd
from scipy import interpolate


def interp_pvt_matbal(
    pvt: pd.DataFrame,
    press_col_name: str,
    prop_col_name: str,
    press_target: float
) -> float:
    """Calculate PVT properties using linear interpolation.

    This function performs linear interpolation on PVT properties based on the
    provided pressure target. It uses the specified columns in the DataFrame to
    find the corresponding property value for the given pressure.

    Parameters:
        pvt (pd.DataFrame):
            DataFrame containing PVT data.
        press_col_name (str):
            String indicating the column name_tank of pressure values.
        prop_col_name (str):
            String indicating the column name_tank of PVT property values to be
            interpolated.
        press_target (float):
            Numeric value indicating the reservoir pressure target to
            interpolate to.

    Returns:
        interp_pvt (float):
            Interpolated PVT property value that matches the pressure target.
    """
    x = pvt[press_col_name]
    y = pvt[prop_col_name]
    function = interpolate.interp1d(x, y, fill_value="extrapolate")
    return float(function(press_target))
