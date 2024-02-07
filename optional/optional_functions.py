# libraries
from utilities.Utilities import variable_type
import math
import numpy as np
import pandas as pd

# File to code aquifer-related functions or classes
def schilthuis_aq(pi, p, k, h, uw, ra, re):
    """
    This function calculates the aquifer water influx according to schilthuis equation
    :param pi: Initial reservoir pressure (psi)
    :param p: Current reservoir pressure, might be scalar, list or numpy array (psi)
    :param k: effective permeability to water (mili darcy)
    :param h: Estimated reservoir thickness in the aquifer zone (ft)
    :param uw: Water viscosity (cp)
    :param ra: aquifer radius (ft)
    :param re: hydrocarbon zone radius (ft)
    :return: a single or array-like value of aquifer influx (bbl)
    """

    # Convert to numpy array in case the user has input a scalar or list
    # TODO Check only for numerical values and lists, otherwise throw an Exception
    if isinstance(p, np.ndarray):
        p_np = p
    else:
        p_np = np.array(p)

    # Calculate water influx (Field units)
    # TODO handle different units
    c = 0.00708 * k * h / (uw * np.log(ra / re))
    ew = c * (pi - p_np)

    return ew