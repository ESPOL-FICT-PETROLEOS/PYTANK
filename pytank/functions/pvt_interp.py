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


def interp_pvt_matbal(pvt: pd.DataFrame, press_col_name: str,
                      prop_col_name: str, press_target: float) -> float:
    """
    Function to calculate PVT properties using lineal interpolate.
    :param:
        - pvt: DataFrame for pvt data
        - press_col_name: String indicating the column name of pressure values
        - prop_col_name: String indicating the column name of pvt property
         values to be interpolated
        - press_target: Numeric value indicating the reservoir pressure target
        value to interpolate to

    :return:
        float: Interpolated pvt property value that match with the
        pressure target
    """
    x = pvt[press_col_name]
    y = pvt[prop_col_name]
    function = interpolate.interp1d(x, y, fill_value='extrapolate')
    return float(function(press_target))
