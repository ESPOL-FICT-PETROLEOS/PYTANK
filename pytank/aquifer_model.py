"""
aquifer_model.py

This module provides the Fetkovich and CarterTracy classes, which are
designed to calculate the cumulative influx of water into a reservoir. These
classes implement specific methodologies for modeling water influx based on
reservoir characteristics and pressure conditions.

Libraries used:
    - pandas: For data manipulation and analysis.
    - numpy: For numerical operations and array handling.
    - math: For mathematical functions and constants.
    - datetime: For handling date and time operations.
    - typing: For type hinting and annotations.
"""

import pandas as pd
import numpy as np
import math
from pytank.functions.utilities import variable_type
from datetime import datetime
from typing import Optional

# Fetkovich
class Fetkovich:
    """This class implements Fetkovich's method for calculating water influx
    into a reservoir. It requires the estimation of initial water volume (Wi),
    maximum water influx (Wei), and the productivity index (J) based on
    reservoir and aquifer properties.
    """

    def __init__(
            self,
            aq_radius: float,
            res_radius: float,
            aq_thickness: float,
            aq_por: float,
            ct: float,
            theta: float,
            k: float,
            water_visc: float,
            boundary_type: str = "no_flow",
            flow_type: str = "radial",
            pr: Optional[list] = None,
            time_step: Optional[list] = None,
            width: float = None,
            length: float = None,
    ):
        """Initializes the attributes of the Fetkovich's class.

        Args:
            aq_radius (float): Radius of the aquifer [ft].
            res_radius (float): Radius of the reservoir [ft].
            aq_thickness (float): Thickness of the aquifer [ft].
            aq_por (float): Porosity of the aquifer.
            ct (float): Total compressibility coefficient [psi^-1].
            theta (float): Encroachment angle [degrees].
            k (float): Permeability of the aquifer [md].
            water_visc (float): Viscosity of water [cp].
            boundary_type (Optional[str]): Type of aquifer boundary, default is
                'no_flow'. Options are 'no_flow', 'constant_pressure',
                'infinite'.
            flow_type (Optional[str]): Type of flow, default is 'radial'.
                Options are 'radial', 'linear'.
            pr (Optional[list, numpy array]): Measured reservoir pressure [Psi].
            time_step (Optional[list, numpy array]): Time step [days].
            width (Optional[float]): Width of the linear aquifer [ft]. Required
                only for linear flow.
            length (Optional[float]): Length of the linear aquifer [ft].
                Required only for linear flow.
        """
        self.aq_radius = aq_radius
        self.res_radius = res_radius
        self.aq_thickness = aq_thickness
        self.aq_por = aq_por
        self.ct = ct
        self.theta = theta
        self.k = k
        self.water_visc = water_visc
        self.boundary_type = boundary_type
        self.flow_type = flow_type
        self.pr = pr
        self.time_step = time_step
        self.width = width
        self.length = length

    def _set_pr_and_time_step(self, pr, time_step):
        """Assigns values to the pr and time_step properties of the Fetkovich
        aquifer.

        This is a private method used internally to set the reservoir pressure
        and time step values for the Fetkovich aquifer model.

        Args:
            pr (list): A list of measured reservoir pressure values in psi.
            time_step (list): A list of time-lapse values in days.
        """

        self.pr = pr
        self.time_step = time_step

        # Check if the time list is in datetime format
        if all(isinstance(t, datetime) for t in time_step):
            # If all elements are already datetime objects, convert -
            # to cumulative days
            self.time_step = [(t - time_step[0]).days for t in time_step]
        elif all(isinstance(t, pd.Timestamp) for t in time_step):
            # If elements are Timestamp objects, convert to datetime and -
            # then to cumulative days
            datetime_list = [pd.to_datetime(t) for t in time_step]
            self.time_step = [(t - datetime_list[0].days
                               for t in datetime_list)]
        elif all(isinstance(t, str) for t in time_step):
            # If all elements are strings, convert to datetime and then -
            # to cumulative days
            datetime_list = [
                datetime.strptime(t, "%Y-%m-%d") for t in time_step
            ]
            self.time_step = [(t - datetime_list[0]).days
                              for t in datetime_list]
        else:
            # Convert dates to cumulative days using variable_types
            self.time_step = variable_type(time_step)

        # Automatically influx of water data upon object creation
        self.we()

    def we(self) -> pd.DataFrame:
        """Calculates cumulative influx of water and returns the values in a
        DataFrame.

        This method computes the cumulative influx of water into the aquifer
        based on the specified flow type and boundary conditions. It generates
        a DataFrame containing the delta water influx ('We'), cumulative water
        influx, and elapsed time for each time step.

        Raises:
            ValueError: If using linear flow without specified width and length.
            ValueError: If the pressure array is not in descending order.
            ValueError: If any pressure value is less than or equal to zero.
            ValueError: If the dimensions of the pressure array and time array
                are not equal.

        Returns:
            df: A DataFrame with columns for delta We, cumulative We,
                and elapsed time.
        """
        if self.flow_type == "linear" and (self.width is None
                                           or self.length is None):
            raise ValueError("When using linear flow, "
                             "width and length are required arguments")
        # Check if pressure and time step are arrays, list or floats
        pr_array = variable_type(self.pr)
        delta_t = variable_type(self.time_step)

        # if not all(pr_array[i] >= pr_array[i + 1]
        #           for i in range(len(pr_array) - 1)):
        #    raise ValueError("Pressure array must be in descendant order")

        # Check if pressure array is not in descendant order throw an error
        if not all(pr_array > 0):
            raise ValueError("Pressure must be greater than zero")
        if isinstance(pr_array, np.ndarray) and isinstance(
                delta_t, np.ndarray):
            dim_pr = np.size(pr_array)
            dim_time = np.size(delta_t)
            if dim_pr != dim_time:
                raise ValueError("Dimensions of pressure array and time array "
                                 "should be equal,"
                                 "please verify your input")

        # Calculate the initial volume of water in the aquifers (Wi)
        wi = ((math.pi / 5.615) * (self.aq_radius ** 2 - self.res_radius ** 2)
              * self.aq_thickness * self.aq_por)

        # Calculate the maximum possible water influx (Wei)
        f = self.theta / 360
        wei = self.ct * wi * pr_array[0] * f

        # Calculate the aquifers productivity index
        # based on the boundary_type conditions and aquifers geometry (J)
        rd = self.aq_radius / self.res_radius

        j = None

        if self.boundary_type == "no_flow" and self.flow_type == "radial":
            j = (0.00708 * self.k * self.aq_thickness *
                 f) / (self.water_visc * (math.log(rd) - 0.75))
        elif (self.boundary_type == "constant_pressure" and self.flow_type ==
              "radial"):
            j = (0.00708 * self.k * self.aq_thickness * f) / (self.water_visc *
                                                              math.log(rd))
        elif self.boundary_type == "no_flow" and self.flow_type == "linear":
            j = (0.003381 * self.k * self.width *
                 self.aq_thickness) / (self.water_visc * self.length)
        elif (self.boundary_type == "constant_pressure" and self.flow_type ==
              "linear"):
            j = (0.001127 * self.k * self.width *
                 self.aq_thickness) / (self.water_visc * self.length)
        elif self.boundary_type == "infinite" and self.flow_type == "radial":
            a = math.sqrt(
                (0.0142 * self.k * 365) / (f * self.water_visc * self.ct))
            j = (0.00708 * self.k * self.aq_thickness *
                 f) / (self.water_visc * math.log(a / self.res_radius))

        # Calculate the incremental water influx (We)n during the nth -
        # time interval

        # Calculate cumulative water influx
        cum_water_influx = 0
        pr = pr_array[0]

        # Average aquifers pressure after removing We bbl of water from -
        # the aquifers
        pa = pr_array[0]
        elapsed_time = np.empty((1, 0))
        time_steps = np.array(0)
        df_list = []
        for ip in range(len(pr_array)):
            pr_avg = (pr + pr_array[ip]) / 2
            if isinstance(delta_t, np.ndarray):
                diff_pr = np.diff(delta_t)
                time_steps = np.append(time_steps, diff_pr)
                we = ((wei / pr_array[0]) * (1 - math.exp(
                    (-1 * j * pr_array[0] * time_steps[ip]) / wei)) *
                      (pa - pr_avg))
                elapsed_time = delta_t
            else:
                we = ((wei / pr_array[0]) * (1 - math.exp(
                    (-1 * j * pr_array[0] * delta_t) / wei)) * (pa - pr_avg))
                elapsed_time = np.append(elapsed_time, delta_t * ip)
            pr = pr_array[ip]
            cum_water_influx = cum_water_influx + we
            pa = pr_array[0] * (1 - (cum_water_influx / wei))

            # Creation values for each key of the list df_list that will -
            # have a dictionary
            df_list.append({
                "Delta We": we,
                "Cumulative We": cum_water_influx,
                "Elapsed time": elapsed_time[ip],
            })

        # Creation of the dataframe that will be return for users
        df = pd.DataFrame(df_list)
        # df = df.set_index("Elapsed time")
        return df

    def get_we(self) -> pd.Series:
        """Encapsulates the DataFrame to return only the cumulative water
        influx.

        This method retrieves the cumulative water influx (Cumulative We) from
        the DataFrame generated by the `we` method and returns it as a Series.

        Returns:
            We: A Series containing the values of cumulative water
                influx (Cumulative We).
        """
        # Encapsulation of DataFrame using method We.
        we = self.we()
        return we["Cumulative We"]


class CarterTracy:
    """This class implements the Carter-Tracy method for modeling water influx
    into a reservoir. It calculates the cumulative water influx based on the
    aquifer's properties and reservoir conditions.
    """

    def __init__(
            self,
            aq_por: float,
            ct: float,
            res_radius: float,
            aq_thickness: float,
            theta: float,
            aq_perm: float,
            water_visc: float,
            pr: Optional[list] = None,
            time_step: Optional[list] = None,
    ):
        """Initializes the attributes of the CarterTracy class.

        Args:
            aq_por (float): Porosity of the aquifer [decimal].
            ct (float): Total compressibility [psi^-1].
            res_radius (float): Radius of the reservoir [ft].
            aq_thickness (float): Thickness of the aquifer [ft].
            theta (float): Encroachment angle [degrees].
            aq_perm (float): Permeability of the aquifer [md].
            water_visc (float): Viscosity of water [cp].
            pr (Optional[list]): Measured reservoir pressure [Psi].
            time_step (Optional[list]): Time lapses [days].
        """
        self.aq_por = aq_por
        self.ct = ct
        self.res_radius = res_radius
        self.aq_thickness = aq_thickness
        self.theta = theta
        self.aq_perm = aq_perm
        self.water_visc = water_visc
        self.time = time_step
        self.pr = pr

    def _set_pr_and_time_step(self, pr, time_step):
        """Assigns values to the pr and time_step properties of the Carter-Tracy
        aquifer.

        This is a private method used internally to set the reservoir pressure
        and time step values for the Carter-Tracy aquifer model.

        Args:
            pr (list): A list of measured reservoir pressure values in psi.
            time_step (list): A list of time-lapse values in days.
        """

        self.pr = pr
        self.time_step = time_step
        # Check if the time list is in datetime format
        if all(isinstance(t, datetime) for t in time_step):
            # If all elements are already datetime objects, convert to -
            # cumulative days
            self.time = [(t - time_step[0]).days for t in time_step]
        elif all(isinstance(t, pd.Timestamp) for t in time_step):
            # If elements are Timestamp objects, convert to datetime and then -
            # to cumulative days
            datetime_list = [pd.to_datetime(t) for t in time_step]
            self.time = [(t - datetime_list[0].days for t in datetime_list)]
        elif all(isinstance(t, str) for t in time_step):
            # If all elements are strings, convert to datetime and then -
            # to cumulative days
            datetime_list = [
                datetime.strptime(t, "%Y-%m-%d") for t in time_step
            ]
            self.time = [(t - datetime_list[0]).days for t in datetime_list]
        else:
            # Convert dates to cumulative days using variable_types
            self.time = variable_type(time_step)

        # Automatically influx of water data upon object creation
        self.we()

    def we(self) -> pd.DataFrame:
        """Calculates cumulative influx of water and returns the values in a
        DataFrame.

        This method computes the cumulative influx of water into the aquifer
        based on the specified parameters and conditions. It generates a
        DataFrame containing the cumulative water influx and elapsed time for
        each time step.

        Raises:
            ValueError: If any pressure value is less than or equal to zero.
            ValueError: If the dimensions of the pressure array and time array
                are not equal.

        Returns:
            df: A DataFrame with columns for cumulative water influx
                (Cumulative We) and elapsed time (Elapsed time, days).
        """
        # Check if pressure and time are arrays, lists or floats
        pr_array = variable_type(self.pr)
        t_array = variable_type(self.time)

        # Check if pressure array is not in descendant order throw an error
        # if not all(pr_array[i] >= pr_array[i + 1]
        #           for i in range(len(pr_array) - 1)):
        #    raise ValueError("Pressure array must be in descendant order")

        # Check if pressure array is not in descendant order throw an error
        if not all(pr_array > 0):
            raise ValueError("Pressure must be greater than zero")

        # Check if time step and pressure dimensions are equal
        # this can be done if time step is entered as array
        if isinstance(pr_array, np.ndarray) and isinstance(
                t_array, np.ndarray):
            dim_pr = np.size(pr_array)
            dim_time = np.size(t_array)
            if dim_pr != dim_time:
                raise ValueError("Dimensions of pressure array and time array "
                                 "should be equal,"
                                 "please verify your input")
        # Calculate the van Everdingen-Hurst water influx constant
        f = self.theta / 360
        b = 1.119 * self.aq_por * self.ct * (self.res_radius **
                                             2) * self.aq_thickness * f
        # Estimate dimensionless time (tD)
        cte = (0.006328 * self.aq_perm /
               (self.aq_por * self.water_visc * self.ct *
                (self.res_radius ** 2)))
        td = np.where(t_array > 0, t_array * cte, 0)

        # Calculate the total pressure drop (Pi-Pn) as an array, for each  -
        # time step n.
        pr_drop = np.where(pr_array > 0, pr_array[0] - pr_array, 1)

        # Estimate the dimensionless pressure
        pr_d = np.where(
            td > 100,
            0.5 * (np.log(np.maximum(td, 1e-15)) + 0.80907),
            ((370.529 * np.sqrt(td)) + (137.582 * td) +
             (5.69549 * (td ** 1.5))) / (328.834 + (265.488 * np.sqrt(td)) +
                                         (45.2157 * td) + (td ** 1.5)),
        )
        # Estimate the dimensionless pressure derivative
        e = 716.441 + (46.7984 * (td * 0.5)) + (270.038 * td) + (71.0098 *
                                                                 (td * 1.5))
        d = ((1296.86 * (td ** 0.5)) + (1204.73 * td) + (618.618 * (td * 1.5))
             + (538.072 * (td * 2)) + (142.41 * (td ** 2.5)))
        pr_deriv = np.where(td > 100, 1 / (2 * np.maximum(td, 1e-15)),
                            e / np.maximum(d, 1e-15))

        # Calculate the cumulative water influx at any time, ti
        df = {"Cumulative We": [0]}
        we = 0

        for i in np.arange(1, len(td)):
            a1 = td[i] - td[i - 1]
            a2 = b * pr_drop[i]
            a3 = we * pr_deriv[i]
            a4 = pr_d[i]
            a5 = td[i - 1] * pr_deriv[i]
            cum_influx_water = we + (a1 * ((a2 - a3) / (a4 - a5)))
            we = cum_influx_water
            df["Cumulative We"].append(we)

        df["Elapsed time, days"] = t_array

        # Concatenation of the DataFrames in a unique final DataFrame
        df = pd.concat([pd.DataFrame(df)], ignore_index=True)

        return df

    def get_we(self) -> pd.Series:
        """Encapsulates the DataFrame to return only the cumulative water
        influx.

        This method retrieves the cumulative water influx (Cumulative We) from
        the DataFrame generated by the `we` method and returns it as a Series.

        Returns:
            We: A Series containing the values of cumulative water
                influx (Cumulative We).
        """
        we = self.we()
        return we["Cumulative We"]
