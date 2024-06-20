from pytank.constants.constants import PRESSURE_COL
from pytank.aquifer.we import Aquifer
from pytank.notebooks.quick_test_tank import mbal, mbal2
from pytank.poes.poes import POES
from pytank.functions.material_balance import campbell_function
from pytank.functions.function2 import G_method2

pr = mbal["PRESSURE_DATUM"].tolist()
ts = mbal["Time_Step"].tolist()

df_we1 = Aquifer(
    aq_por=0.25,
    ct=7e-6,
    res_radius=2000,
    aq_thickness=25,
    theta=360,
    aq_perm=100,
    water_visc=0.8,
    pr=pr,
    time_step=ts
).fetkovich(4600)

camp_nosotros = POES(
    we_df=df_we1,
    mbal_df=mbal,
).campbell()

camp_oscar = campbell_function(mbal2,
                               "OIL_CUM_TANK",
                               "WATER_CUM_TANK",
                               "GAS_CUM_TANK",
                               "PRESSURE_DATUM",
                               "UW",
                               "Eo",
                               "Efw",
                               "Bo",
                               "Bg",
                               "GOR",
                               "Bw",
                               "RS_bw",
                               0.15,
                               3.4e-6,
                               3.62e-6,
                               1.119,
                               mbal2["Bg"][0],
                               mbal2["Bo"][0],
                               mbal2["GOR"][0],
                               3700)
print(camp_nosotros)
print(camp_oscar)


# HAVLENA
# Ellos
"""hyo = POES(
    we_df=df_we1,
    mbal_df=mbal,
).havlena_odeh()

# Nosotros
hyo2 = POES(
    we_df=df_we1,
    mbal_df=mbal,
).havlena_odeh2()

#print(hyo)
#print(hyo2)"""

# Ellos
"""
cf = 3.2e-6
swo = 0.15
boi = mbal["Bo"][0]
pi = mbal[PRESSURE_COL][0]
t = 200
salinity = 30000
we = df_we1["Cumulative We"]

poes = G_method2(
    pr=mbal[PRESSURE_COL],
    np=mbal["OIL_CUM_TANK"],
    wp=mbal["WATER_CUM_TANK"],
    bo=mbal["OIL_CUM_TANK"],
    cf=cf,
    sw0=swo,
    boi=boi,
    we=we,
    pi=pi,
    t=t,
    salinity=salinity
)
print(poes)

import matplotlib.pyplot as plt
from scipy import stats

plt.scatter(poes["We*Bw/Et"],poes["F/Eo+Efw"])
plt.title("ELLOS")
plt.show()

x1 = poes["We*Bw/Et"]
y = poes["F/Eo+Efw"]

slope, intercept, r, p, se = stats.linregress(x1, y)

print(f"N [MMStb]: {intercept / 1000000:.4f}")"""