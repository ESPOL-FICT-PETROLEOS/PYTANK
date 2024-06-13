import pandas as pd
import numpy as np
from old.utilities import variable_type
import math
from datetime import datetime
from pandas import Timestamp


# Creation of class to reach cumulate influx of water
# Fetkovich
class Fetkovich:
    def __init__(
        self,
        aq_radius: float,
        res_radius: float,
        aq_thickness: float,
        aq_por: float,
        ct: float,
        pr: list,
        theta: float,
        k: float,
        water_visc: float,
        time_step: list,
        boundary_type="no_flow",
        flow_type="radial",
        width=None,
        length=None,
    ):
        self.aq_radius = aq_radius
        self.res_radius = res_radius
        self.aq_thickness = aq_thickness
        self.aq_por = aq_por
        self.ct = ct
        self.pr = variable_type(pr)
        self.theta = theta
        self.k = k
        self.water_visc = water_visc
        self.boundary_type = boundary_type
        self.flow_type = flow_type
        self.width = width
        self.length = length
        self.time_step = time_step

        # Check if the time list is in datetime format
        if all(isinstance(t, datetime) for t in time_step):
            # If all elements are alreaady datetime objects, convert to cumulative days
            self.time_step = [(t - time_step[0]).days for t in time_step]
        elif all(isinstance(t, pd.Timestamp) for t in time_step):
            # If elements are Timestamp objects, convert to datetime and then to comulative days
            datetime_list = [pd.to_datetime(t) for t in time_step]
            self.time_step = [(t - datetime_list[0].days for t in datetime_list)]
        elif all(isinstance(t, str) for t in time_step):
            # If all elements are strings, convert to datetime and then to cumulative days
            datetime_list = [datetime.strptime(t, "%Y-%m-%d") for t in time_step]
            self.time_step = [(t - datetime_list[0]).days for t in datetime_list]
        else:
            # Convert dates to cumulative days using variable_types
            self.time_step = variable_type(time_step)

        # Automatically influx of water data upon object creation
        self.we

    def we(self) -> pd.DataFrame:
        global j
        if self.flow_type == "linear" and (self.width is None or self.length is None):
            raise ValueError(
                "When using linear flow, " "width and length are required arguments"
            )
        # Check if pressure and time step are arrays, list or floats
        pr_array = variable_type(self.pr)
        delta_t = variable_type(self.time_step)
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
                raise ValueError(
                    "Dimensions of pressure array and time array "
                    "should be equal,"
                    " please verify your input"
                )
        # Calculate the initial volume of water in the aquifers (Wi)
        wi = (
            (math.pi / 5.615)
            * (self.aq_radius**2 - self.res_radius**2)
            * self.aq_thickness
            * self.aq_por
        )
        # Calculate the maximum possible water influx (Wei)
        f = self.theta / 360
        wei = self.ct * wi * pr_array[0] * f
        # Calculate the aquifers productivity index
        # based on the boundary_type conditions and aquifers geometry (J)
        rd = self.aq_radius / self.res_radius

        if self.boundary_type == "no_flow" and self.flow_type == "radial":
            j = (0.00708 * self.k * self.aq_thickness * f) / (
                self.water_visc * (math.log(rd) - 0.75)
            )
        elif self.boundary_type == "constant_pressure" and self.flow_type == "radial":
            j = (0.00708 * self.k * self.aq_thickness * f) / (
                self.water_visc * math.log(rd)
            )
        elif self.boundary_type == "no_flow" and self.flow_type == "linear":
            j = (0.003381 * self.k * self.width * self.aq_thickness) / (
                self.water_visc * self.length
            )
        elif self.boundary_type == "constant_pressure" and self.flow_type == "linear":
            j = (0.001127 * self.k * self.width * self.aq_thickness) / (
                self.water_visc * self.length
            )
        elif self.boundary_type == "infinite" and self.flow_type == "radial":
            a = math.sqrt((0.0142 * self.k * 365) / (f * self.water_visc * self.ct))
            j = (0.00708 * self.k * self.aq_thickness * f) / (
                self.water_visc * math.log(a / self.res_radius)
            )

        # Calculate the incremental water influx (We)n during the nth time interval
        # Calculate cumulative water influx
        cum_water_influx = 0
        pr = pr_array[0]
        # Average aquifers pressure after removing We bbl of water from the aquifers
        pa = pr_array[0]
        elapsed_time = np.empty((1, 0))
        time_steps = np.array(0)
        df_list = []
        for ip in range(len(pr_array)):
            pr_avg = (pr + pr_array[ip]) / 2
            if isinstance(delta_t, np.ndarray):
                diff_pr = np.diff(delta_t)
                time_steps = np.append(time_steps, diff_pr)
                we = (
                    (wei / pr_array[0])
                    * (1 - math.exp((-1 * j * pr_array[0] * time_steps[ip]) / wei))
                    * (pa - pr_avg)
                )
                elapsed_time = delta_t
            else:
                we = (
                    (wei / pr_array[0])
                    * (1 - math.exp((-1 * j * pr_array[0] * delta_t) / wei))
                    * (pa - pr_avg)
                )
                elapsed_time = np.append(elapsed_time, delta_t * ip)
            pr = pr_array[ip]
            cum_water_influx = cum_water_influx + we
            pa = pr_array[0] * (1 - (cum_water_influx / wei))

            # Creation values for each key of the list df_list that will have a dictionary
            df_list.append(
                {
                    "Delta We": we,
                    "Cumulative We": cum_water_influx,
                    "Elapsed time": elapsed_time[ip],
                }
            )

        # Creation of the dataframe that will be return for users
        df = pd.DataFrame(df_list)
        #df = df.set_index("Elapsed time")

        return df


class Carter_Tracy:
    def __init__(
        self,
        aq_por: float,
        ct: float,
        res_radius: float,
        aq_thickness: float,
        theta: float,
        aq_perm: float,
        water_visc: float,
        pr: list,
        time: list,
    ):
        self.aq_por = aq_por
        self.ct = ct
        self.res_radius = res_radius
        self.aq_thickness = aq_thickness
        self.theta = theta
        self.aq_perm = aq_perm
        self.water_visc = water_visc
        self.time = time
        self.pr = variable_type(pr)

        # Check if the time list is in datetime format
        if all(isinstance(t, datetime) for t in time):
            # If all elements are alreaady datetime objects, convert to cumulative days
            self.time = [(t - time[0]).days for t in time]
        elif all(isinstance(t, pd.Timestamp) for t in time):
            # If elements are Timestamp objects, convert to datetime and then to comulative days
            datetime_list = [pd.to_datetime(t) for t in time]
            self.time = [(t - datetime_list[0].days for t in datetime_list)]
        elif all(isinstance(t, str) for t in time):
            # If all elements are strings, convert to datetime and then to cumulative days
            datetime_list = [datetime.strptime(t, "%Y-%m-%d") for t in time]
            self.time = [(t - datetime_list[0]).days for t in datetime_list]
        else:
            # Convert dates to cumulative days using variable_types
            self.time = variable_type(time)

        # Automatically influx of water data upon object creation
        self.we()

    def we(self) -> pd.DataFrame:
        # Check if pressure and time are arrays, lists or floats
        pr_array = variable_type(self.pr)
        t_array = variable_type(self.time)

        # Check if pressure array is not in descendant order throw an error
        if not all(pr_array > 0):
            raise ValueError("Pressure must be greater than zero")

        # Check if time step and pressure dimensions are equal
        # this can be done if time step is entered as array
        if isinstance(pr_array, np.ndarray) and isinstance(t_array, np.ndarray):
            dim_pr = np.size(pr_array)
            dim_time = np.size(t_array)
            if dim_pr != dim_time:
                raise ValueError(
                    "Dimensions of pressure array and time array "
                    "should be equal,"
                    " please verify your input"
                )

        # Calculate the van Everdingen-Hurst water influx constant
        f = self.theta / 360
        b = 1.119 * self.aq_por * self.ct * (self.res_radius**2) * self.aq_thickness * f

        # Estimate dimensionless time (tD)
        cte = (
            0.006328
            * self.aq_perm
            / (self.aq_por * self.water_visc * self.ct * (self.res_radius**2))
        )
        td = np.where(t_array > 0, t_array * cte, 0)

        # Calculate the total pressure drop (Pi-Pn) as an array, for each time step n.
        pr_drop = np.where(pr_array > 0, pr_array[0] - pr_array, 1)

        # Estimate the dimensionless pressure
        pr_d = np.where(
            td > 100,
            0.5 * (np.log(np.maximum(td, 1e-15)) + 0.80907),
            ((370.529 * np.sqrt(td)) + (137.582 * td) + (5.69549 * (td**1.5)))
            / (328.834 + (265.488 * np.sqrt(td)) + (45.2157 * td) + (td**1.5)),
        )
        # Estimate the dimensionless pressure derivative
        e = 716.441 + (46.7984 * (td * 0.5)) + (270.038 * td) + (71.0098 * (td * 1.5))
        d = (
            (1296.86 * (td**0.5))
            + (1204.73 * td)
            + (618.618 * (td * 1.5))
            + (538.072 * (td * 2))
            + (142.41 * (td**2.5))
        )
        pr_deriv = np.where(
            td > 100, 1 / (2 * np.maximum(td, 1e-15)), e / np.maximum(d, 1e-15)
        )

        # Calculate the cumulative water influx at any time, ti
        df = {"Cumulative water influx, bbl": [0]}
        we = 0

        for i in np.arange(1, len(td)):
            a1 = td[i] - td[i - 1]
            a2 = b * pr_drop[i]
            a3 = we * pr_deriv[i]
            a4 = pr_d[i]
            a5 = td[i - 1] * pr_deriv[i]
            cum_influx_water = we + (a1 * ((a2 - a3) / (a4 - a5)))
            we = cum_influx_water
            df["Cumulative water influx, bbl"].append(we)

        df["Elapsed time, days"] = t_array

        # Concatenation of the DataFrames in an unique final DataFrame
        df = pd.concat([pd.DataFrame(df)], ignore_index=True).set_index(
            "Elapsed time, days"
        )

        return df
