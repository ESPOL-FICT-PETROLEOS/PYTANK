import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve
from pytank.functions.pvt_interp import interp_pvt_matbal
from pytank.functions.pvt_correlations import Bo_bw, comp_bw_nogas
from pytank.notebooks.quick_test_analysis import mbal2
from pytank.constants.constants import (OIL_CUM_TANK,
                                        WATER_CUM_TANK,
                                        GAS_CUM_TANK,
                                        LIQ_CUM,
                                        PRESSURE_COL,
                                        TANK_COL,
                                        DATE_COL,
                                        OIL_FVF_COL
                                        )

# %%

df_ta2 = mbal2
df_pvt = pd.read_csv("../resources/data_csv/pvt.csv")


# df_pvt = df_pvt.fillna(method="ffill")
# time_step = time


def ebm(p, pi, Np, wp, bo, cf, cw, sw0, boi, N, we, bw):
    Eo = bo - boi
    Efw = boi * (((cw * sw0) + cf) / (1 - sw0)) * (pi - p)
    F = (Np * bo) + (wp * bw)
    funcion_P = (N * (Eo + Efw)) + (we * bw) - F

    return funcion_P


def carter(
        aq_por,
        ct,
        res_radius,
        aq_thickness,
        theta,
        k,
        water_visc,
        pr,
        time,
        time_anterior,
        we,
        pi,
):
    pr_array = pr

    # Calculate the van Everdingen-Hurst water influx constant
    f = theta / 360
    b = 1.119 * aq_por * ct * (res_radius ** 2) * aq_thickness * f

    # Estimate dimensionless time (tD)
    cte = 0.006328 * k / (aq_por * water_visc * ct * (res_radius ** 2))
    td = time * cte
    td2 = time_anterior * cte
    # Calculate the total pressure drop (Pi-Pn) as an array, for each time step n.
    pr_drop = pi - pr_array
    # Estimate the dimensionless pressure
    pr_d = 0.5 * (np.log(td) + 0.80907)
    # Estimate the dimensionless pressure derivative
    e = 716.441 + (46.7984 * (td ** 0.5)) + (270.038 * td) + (71.0098 * (td ** 1.5))
    d = (
            (1296.86 * (td ** 0.5))
            + (1204.73 * td)
            + (618.618 * (td ** 1.5))
            + (538.072 * (td ** 2))
            + (142.41 * (td ** 2.5))
    )

    pr_deriv = 1 / (2 * td)

    a1 = td - td2
    a2 = b * pr_drop
    a3 = we * pr_deriv
    a4 = pr_d
    a5 = td2 * pr_deriv
    cum_influx_water = we + (a1 * ((a2 - a3) / (a4 - a5)))
    we = cum_influx_water
    return we


def press(
        p,
        np,
        wp,
        cf,
        t,
        salinity,
        df_pvt,
        res_radius,
        aq_thickness,
        aq_por,
        theta,
        k,
        water_visc,
        time,
        time_anterior,
        we,
        pi,
        sw0,
        N,
        boi,
        ppvt_col,
        oil_fvf_col
):
    bo = interp_pvt_matbal(df_pvt, ppvt_col, oil_fvf_col, p)

    bw = Bo_bw(p, t, salinity, unit=1)
    cw = comp_bw_nogas(p, t, salinity, unit=1)
    ct = cw + cf
    we = carter(
        aq_por,
        ct,
        res_radius,
        aq_thickness,
        theta,
        k,
        water_visc,
        p,
        time,
        time_anterior,
        we,
        pi,
    )
    return ebm(p, pi, np, wp, bo, cf, cw, sw0, boi, N, we, bw)


def calculate_pressure(
        np_frame,
        wp_frame,
        cf,
        t,
        salinity,
        df_pvt,
        res_radius,
        aq_thickness,
        aq_por,
        theta,
        k,
        water_visc,
        time_frame,
        pi,
        sw0,
        N,
        ppvt_col,
        oil_fvf_col
):
    boi = interp_pvt_matbal(df_pvt, ppvt_col, oil_fvf_col, pi)
    cum = 0
    x0 = pi
    P_calculada = [pi]
    time_anterior = 0
    for i in range(len(np_frame)):
        Np = np_frame[i]
        wp = wp_frame[i]
        time = time_frame[i]
        presion = fsolve(
            press,
            x0,
            args=(
                Np,
                wp,
                cf,
                t,
                salinity,
                df_pvt,
                res_radius,
                aq_thickness,
                aq_por,
                theta,
                k,
                water_visc,
                time,
                time_anterior,
                cum,
                pi,
                sw0,
                N,
                boi,
                ppvt_col,
                oil_fvf_col
            ),
        )[0]
        x0 = presion
        P_calculada.append(presion)
        cw = comp_bw_nogas(presion, t, salinity, unit=1)
        ct = cf + cw
        cum = carter(
            aq_por,
            ct,
            res_radius,
            aq_thickness,
            theta,
            k,
            water_visc,
            x0,
            time,
            time_anterior,
            cum,
            pi,
        )
        time_anterior = time_frame[i]

    return P_calculada


cf = 3.5e-6
t = 200
salinity = 30000
aq_radius = 10000
res_radius = 1000
aq_thickness = 20
aq_por = 0.25
theta = 135
k = 25
water_visc = 0.6
cum = 0
pi = 3800
sw0 = 0.25
N = 67e6
P_calculada = calculate_pressure(mbal2["WATER_CUM_TANK"], mbal2["OIL_CUM_TANK"], cf, t, salinity, df_pvt, res_radius,
                                 aq_thickness, aq_por, theta, k, water_visc, mbal2["Time_Step"], pi, sw0, N, "Pressure",
                                 "Bo")
print(P_calculada)
# %%
nueva_fila = pd.DataFrame({DATE_COL: '1987-09-01', PRESSURE_COL: pi, OIL_FVF_COL: 1.1},
                          index=[0])
df_ta2 = pd.concat([nueva_fila, df_ta2]).reset_index(drop=True)
df_ta2[DATE_COL] = pd.to_datetime(df_ta2[DATE_COL])
df_ta2.iloc[0] = df_ta2.iloc[0].fillna(0)

# %%
fig, ax = plt.subplots(figsize=(15, 10))
ax.scatter(df_ta2[DATE_COL].dt.year, df_ta2[PRESSURE_COL], label="Presion Observada")
plt.plot(df_ta2[DATE_COL].dt.year, P_calculada, c="g", label="Presion Calculada")
plt.title("Gráfico P vs t ", fontsize=15)
plt.xlabel("Tiempo (Años)", fontsize=15)
plt.ylabel("Presion (psia)", fontsize=15)
plt.yticks(fontsize=15)
ax.grid(axis="both", color="gray", linestyle="dashed")
plt.legend(fontsize=15)
plt.show()
