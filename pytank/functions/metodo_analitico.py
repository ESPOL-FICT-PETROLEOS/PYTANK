import pandas as pd
from pytank.constants.constants import (OIL_FVF_COL,
                                        PRESSURE_COL,
                                        DATE_COL)
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve
import math
from pytank.functions.pvt_interp import interp_pvt_matbal
from pytank.functions.pvt_correlations import Bo_bw, comp_bw_nogas

# %%
df_ta2 = pd.read_csv("../tank/mbal_tank.csv")
df_pvt = pd.read_csv("../resources/data_csv/pvt.csv")
#df_pvt = df_pvt.fillna(method="ffill")

ppvt_col = "Pressure"
oil_fvf_col = "Bo"
gas_fvf_col = "Bg"
gas_oil_rs_col = "GOR"
df_ta2["GAS_CUM_TANK"] = df_ta2["GAS_CUM_TANK"] * 89

def mbal(p, pi, Np, wp, bo, cf, cw, sw0, boi, N, we, bw):
    # if rsi == rs:
    Eo = bo - boi
    Efw = boi * (((cw * sw0) + cf) / (1 - sw0)) * (pi - p)
    F = (Np * bo) + (wp * bw)
    funcion_P = (N * (Eo + Efw)) + (we * bw) - F
    # else:
    # Eo = (bo - boi) + (rsi-rs)*bg
    # Efw = (1+m) * boi * (((cw * sw0) + cf) / (1 - sw0)) * (pi - p)
    # Eg = boi*((bg/bgi)-1)
    # Gp= (gp-(Np*rs))*bg
    # F = (Np * bo) + (wp * bw) + Gp
    # funcion_P = (N * (Eo + Efw + m*Eg)) + (we * bw) - F

    return funcion_P


def aquifer_fetkovich(
    aq_radius,
    res_radius,
    aq_thickness,
    aq_por,
    ct,
    p,
    theta,
    k,
    water_visc,
    p_anterior,
    cum,
    pi,
):
    delta_t = 365
    wi = (math.pi / 5.615) * (aq_radius**2 - res_radius**2) * aq_thickness * aq_por
    f = theta / 360
    wei = ct * wi * pi * f
    rd = aq_radius / res_radius
    j = (0.00708 * k * aq_thickness * f) / (water_visc * (math.log(abs(rd))))
    pa = pi * (1 - (cum / wei))
    pr_avg = (p_anterior + p) / 2
    we = (wei / pi) * (1 - np.exp((-1 * j * pi * delta_t) / wei)) * (pa - pr_avg)
    cum_water_influx = cum + we
    return cum_water_influx


def press(
    p,
    Np,
    wp,
    cf,
    t,
    salinity,
    df_pvt,
    aq_radius,
    res_radius,
    aq_thickness,
    aq_por,
    theta,
    k,
    water_visc,
    p_anterior,
    cum,
    pi,
    sw0,
    N,
    boi,
):
    if p < 0:
        return 1e10

    bo = interp_pvt_matbal(df_pvt, ppvt_col, oil_fvf_col, p)

    bw = Bo_bw(p, t, salinity, unit=1)
    cw = comp_bw_nogas(p, t, salinity, unit=1)
    ct = cw + cf
    we = aquifer_fetkovich(
        aq_radius,
        res_radius,
        aq_thickness,
        aq_por,
        ct,
        p,
        theta,
        k,
        water_visc,
        p_anterior,
        cum,
        pi,
    )
    return mbal(p, pi, Np, wp, bo, cf, cw, sw0, boi, N, we, bw)


cf = 4.5e-6
t = 200
salinity = 30000
aq_radius = 15000
res_radius = 2000
aq_thickness = 14
aq_por = 0.25
theta = 300
k = 25
water_visc = 0.35
cum = 0
pi = 4500
sw0 = 0.25
boi = interp_pvt_matbal(df_pvt, ppvt_col, oil_fvf_col, pi)
N = 70e6
x0 = 3600

P_calculada = [pi]
for i in range(len(df_ta2[PRESSURE_COL])):
    Np = df_ta2["OIL_CUM_TANK"][i]
    wp = df_ta2["WATER_CUM_TANK"][i]
    gp = df_ta2["GAS_CUM_TANK"][i]
    p_anterior = P_calculada[i]
    # Calculate current reservoir pressure given all other material balance variables through numeric solving.
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
            aq_radius,
            res_radius,
            aq_thickness,
            aq_por,
            theta,
            k,
            water_visc,
            p_anterior,
            cum,
            pi,
            sw0,
            N,
            boi,
        ),
    )[0]
    print(f"Calculated Reservoir Pressure: {presion}")
    x0 = presion

    P_calculada.append(presion)
    cw = comp_bw_nogas(presion, t, salinity, unit=1)
    ct = cf + cw
    cum = aquifer_fetkovich(
        aq_radius,
        res_radius,
        aq_thickness,
        aq_por,
        ct,
        presion,
        theta,
        k,
        water_visc,
        p_anterior,
        cum,
        pi,
    )
    print(f"Wei:{cum}")

nueva_fila = pd.DataFrame(
    {DATE_COL: "1987-09-01", PRESSURE_COL: 4000.00, OIL_FVF_COL: 1.1}, index=[0]
)
df_ta2 = pd.concat([nueva_fila, df_ta2]).reset_index(drop=True)
df_ta2[DATE_COL] = pd.to_datetime(df_ta2[DATE_COL])
df_ta2.iloc[0] = df_ta2.iloc[0].fillna(0)
# %%
fig, ax = plt.subplots(figsize=(15, 10))
ax.scatter(df_ta2[DATE_COL].dt.year, df_ta2[PRESSURE_COL], label="Presion Observada")
plt.plot(df_ta2[DATE_COL].dt.year, P_calculada, c="g", label="Presion Calculada")
# plt.plot(df_ta2['Date'], P4, c='r', label='Presion Calculada')
plt.title("Gráfico P vs t ", fontsize=15)
plt.xlabel("Tiempo (Años)", fontsize=15)
plt.ylabel("Presion (psia)", fontsize=15)
ax.set_ylim([400, 4000])
# plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
ax.grid(axis="both", color="gray", linestyle="dashed")
plt.legend(fontsize=15)
plt.show()
