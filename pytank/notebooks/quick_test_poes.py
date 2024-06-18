from pytank.constants.constants import PRESSURE_COL
from pytank.aquifer.we import Aquifer
from pytank.notebooks.quick_test_tank import mbal

cf = 0.00000362
swo = 0.15
boi = 86
pi = mbal[PRESSURE_COL][0]
t = 200
salinity = 30000

pr = mbal["PRESSURE_DATUM"].tolist()
ts = mbal["Time_Step"].tolist()

df_we1 = Aquifer(

    aq_por=0.25,
    ct=0.000007,
    res_radius=920,
    aq_thickness=100,
    theta=140,
    aq_perm=200,
    water_visc=0.55,
    pr=pr,
    time_step=ts
).fetkovich(4600)

# Ellos

"""
df_we = Fetkovich(
    aq_radius=4600,
    res_radius=920,
    aq_thickness=100,
    aq_por=0.25,
    ct=0.000007,
    pr=pr,
    theta=140,
    k=200,
    water_visc=0.55,
    time_step=ts,
).we()

we = df_we["Cumulative We"]

poes = G_method2(
    pr=mbal[PRESSURE_COL],
    np=mbal["OIL_CUM_TANK"],
    wp=mbal["WATER_CUM_TANK"],
    bo=mbal[OIL_FVF_COL],
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
from sklearn.linear_model import LinearRegression
from scipy import stats
plt.scatter(poes["We*Bw/Et"],poes["F/Eo+Efw"],)

x=poes[["We*Bw/Et"]]
x1=poes["We*Bw/Et"]
y=poes["F/Eo+Efw"]

model = LinearRegression()
model.fit(x,y)

# Obtener la pendiente (coeficiente) y el intercepto
pendiente = model.coef_[0]
intercepto = model.intercept_
slope, intercept, r, p, se = stats.linregress(x1, y)
print(f'Pendiente: {pendiente}')
print(f'Intercepto: {intercepto}')
print(f"N [MMStb]: {intercepto / 1000000:.4f}")
print(f"N [MMStb]: {intercept / 1000000:.4f}")"""