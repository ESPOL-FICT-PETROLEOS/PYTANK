from pytank.aquifer.influx_of_water import Fetkovich
from pytank.functions.utilities import variable_type
import math
import numpy as np
import pandas as pd

# ellos
def aquifer_fetkovich(aq_radius, res_radius, aq_thickness, aq_por, ct, pr, theta, k,
                      water_visc, time_step,
                      boundary_type='no_flow', flow_type='radial',
                      width=None, length=None):
    """
        To estimate water influx using the Fetkovich's method we need to estimate:
        Wi, Wei and J.
        :param aq_radius: radius of the aquifer, ft
        :param res_radius: radius of the reservoir, ft
        :param aq_thickness: thickness of the aquifer, ft
        #param fi: changed by phi
        :param aq_por: porosity of the aquifer
        :param ct: total compressibility coefficient, psi-1
        :param pr: measured reservoir pressure, may be an integer, a float, list or
        numpy array, psi
        :param theta: encroachment angle
        :param k: permeability of the aquifer, md
        :param water_visc: viscosity of water, cp
        :param time_step: time step may be an integer, a float, list or
        numpy array, days
        :param boundary_type: default value = 'no_flow',
        options are: 'no_flow', 'constant_pressure', 'infinite'
        :param flow_type: default value = 'radial', options are: 'radial', 'linear'
        :param width: width of the linear aquifer,
        * parameter required only for linear flow, ft
        :param length: length of the linear aquifer,
        * parameter required only for linear flow, ft
        :return: a DataFrame containing the cumulative water influx, bbl
    """
    global j
    if flow_type == 'linear' and (width is None or length is None):
        raise ValueError("When using linear flow, "
                         "width and length are required arguments")
    # Check if pressure and time step are arrays, list or floats
    pr_array = variable_type(pr)
    delta_t = variable_type(time_step)
    # Check if pressure array is not in descendant order throw an error
    # order = pd.Series(pr_array).is_monotonic_decreasing
    # if order is False:
    #     raise ValueError("Pressure array must be in descendant order")
    # Check if time step and pressure dimensions are equal
    # this can be done if time step is entered as array
    if not all(pr_array > 0):
        raise ValueError("Pressure must be greater than zero")
    if isinstance(pr_array, np.ndarray) and isinstance(delta_t, np.ndarray):
        dim_pr = np.size(pr_array)
        dim_time = np.size(delta_t)
        if dim_pr != dim_time:
            raise ValueError("Dimensions of pressure array and time array "
                             "should be equal,"
                             " please verify your input")
    # Calculate the initial volume of water in the aquifer (Wi)
    wi = (math.pi / 5.615) * (aq_radius**2 - res_radius ** 2) * aq_thickness * aq_por
    # Calculate the maximum possible water influx (Wei)
    f = theta / 360
    wei = ct * wi * pr_array[0] * f
    # Calculate the aquifer productivity index
    # based on the boundary_type conditions and aquifer geometry (J)
    rd = aq_radius / res_radius

    if boundary_type == "no_flow" and flow_type == "radial":
        j = (0.00708 * k * aq_thickness * f) / (water_visc * (math.log(rd) - 0.75))
    elif boundary_type == "constant_pressure" and flow_type == "radial":
        j = (0.00708 * k * aq_thickness * f) / (water_visc * math.log(rd))
    elif boundary_type == "no_flow" and flow_type == "linear":
        j = (0.003381 * k * width * aq_thickness) / (water_visc * length)
    elif boundary_type == "constant_pressure" and flow_type == "linear":
        j = (0.001127 * k * width * aq_thickness) / (water_visc * length)
    elif boundary_type == "infinite" and flow_type == "radial":
        a = math.sqrt((0.0142 * k * 365)/ (f * water_visc * ct) )
        j = (0.00708 * k * aq_thickness * f) / (water_visc * math.log(a/res_radius))

    # Calculate the incremental water influx (We)n during the nth time interval
    # Calculate cumulative water influx
    cum_water_influx = 0
    pr = pr_array[0]
    # Average aquifer pressure after removing We bbl of water from the aquifer
    pa = pr_array[0]
    elapsed_time = np.empty((1, 0))
    time_steps = np.array(0)
    df = pd.DataFrame(columns=['Delta We'])
    for ip in range(len(pr_array)):
        pr_avg = (pr + pr_array[ip]) / 2
        if isinstance(delta_t, np.ndarray):
            diff_pr = np.diff(delta_t)
            time_steps = np.append(time_steps, diff_pr)
            we = (wei / pr_array[0]) * \
                 (1 - math.exp((-1 * j * pr_array[0] * time_steps[ip]) / wei)) * \
                 (pa - pr_avg)
            elapsed_time = delta_t
        else:
            we = (wei / pr_array[0]) * \
                 (1 - math.exp((-1 * j * pr_array[0] * delta_t) / wei)) * \
                 (pa - pr_avg)
            elapsed_time = np.append(elapsed_time, delta_t * ip)
        pr = pr_array[ip]
        cum_water_influx = cum_water_influx + we
        pa = pr_array[0] * (1 - (cum_water_influx / wei))
        df = df._append({'Delta We': we, 'Cumulative We': cum_water_influx}, ignore_index=True)
    df['Elapsed time'] = elapsed_time
    df = df.set_index('Elapsed time')
    return df


aq_radius = 46000
res_radius = 9200
aq_thickness = 100
# -fi = 0.25
# +phi = 0.25
phi = 0.25
ct = 0.000007
pr = [2740, 2500, 2290, 2109, 1949]
theta = 140
k = 200
water_visc = 0.55
time_step = [0, 365, 730, 1095, 1460]

df_we = Fetkovich(aq_radius, res_radius, aq_thickness, phi, ct, pr, theta, k, water_visc, time_step).we()
df_we1 = aquifer_fetkovich(aq_radius, res_radius, aq_thickness, phi, ct, pr, theta, k, water_visc, time_step)
print("Nuestro", df_we)
print("Ellos", df_we1)