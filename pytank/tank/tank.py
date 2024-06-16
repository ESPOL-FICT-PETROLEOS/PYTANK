import pandas as pd
from matplotlib import pyplot as plt
from pydantic import BaseModel
from pytank.constants.constants import (OIL_FVF_COL,
                                        GAS_FVF_COL,
                                        RS_COL,
                                        PRESSURE_COL,
                                        OIL_CUM_COL,
                                        GAS_CUM_COL,
                                        WATER_CUM_COL,
                                        OIL_CUM_TANK,
                                        WATER_CUM_TANK,
                                        GAS_CUM_TANK,
                                        DATE_COL,
                                        WELL_COL,
                                        WATER_FVF_COL,
                                        RS_W_COL,
                                        TANK_COL,
                                        LIQ_CUM,
                                        UW_COL,
                                        PRESSURE_PVT_COL,
                                        OIL_EXP,
                                        RES_EXP
                                        )
from pytank.fluid_model.fluid import OilModel, WaterModel
from pytank.functions.utilities import interp_dates_row
from pytank.functions.pvt_interp import interp_pvt_matbal
from pytank.functions.pvt_correlations import RS_bw, Bo_bw
from pytank.notebooks.get_wells import tank_wells
from pytank.functions.material_balance import underground_withdrawal, pressure_vol_avg, gas_expansion, oil_expansion, \
    fw_expansion, campbell_function
from pytank.aquifer.we import Aquifer
from pytank.functions.pvt_correlations import comp_bw_nogas


class Tank(BaseModel):
    tanks:  dict
    name: str
    wells: list
    oil_model: OilModel
    water_model: WaterModel

    def _press_df_int(self):
        """
        Private method that internally manages the pressure vector for use in the UW method

        Parameters
        ----------

        Returns
        -------
        A pressure DataFrame with properties PVT of oil and water
        """
        df_press = pd.DataFrame()
        for tank_name, wells in self.tanks.items():
            for well in wells:
                press_vector = well.press_data
                if press_vector is not None:
                    well_name = well.name
                    well_date = press_vector.data.index
                    well_oil_fvf = self.oil_model.get_bo_at_press(press_vector.data[PRESSURE_COL])
                    well_gas_fvf = self.oil_model.get_bg_at_press(press_vector.data[PRESSURE_COL])
                    well_rs = self.oil_model.get_rs_at_press(press_vector.data[PRESSURE_COL])

                    # In case properties are calculated using correlations
                    if (self.water_model.correlation_bw and self.water_model.correlation_rs
                            and self.water_model.salinity is not None
                            and self.water_model.temperature is not None
                            and self.water_model.unit is not None):
                        well_bw = self.water_model.get_bw_at_press(press_vector.data[PRESSURE_COL])
                        well_rs_w = self.water_model.get_rs_at_press(press_vector.data[PRESSURE_COL])

                    # In case there are default values for Bw and Rs_w
                    else:
                        well_bw = self.water_model.get_default_bw()
                        well_rs_w = self.water_model.get_default_rs()

                    # Create a copy of data from press_vector
                    temp_df_press = press_vector.data.copy()

                    # Add columns to DataFrame
                    temp_df_press[WELL_COL] = well_name
                    temp_df_press[DATE_COL] = well_date
                    temp_df_press[OIL_FVF_COL] = well_oil_fvf
                    temp_df_press[GAS_FVF_COL] = well_gas_fvf
                    temp_df_press[RS_COL] = well_rs
                    temp_df_press[WATER_FVF_COL] = well_bw
                    temp_df_press[RS_W_COL] = well_rs_w
                    temp_df_press[TANK_COL] = tank_name

                    df_press = pd.concat([df_press, temp_df_press], ignore_index=True)
        return df_press

    def _prod_df_int(self) -> pd.DataFrame:
        """
        Private method that internally manages production vector for use in the UW method

        Parameters
        ----------

        Returns
        -------
        A production DataFrame

        """
        df_prod = pd.DataFrame()
        for tank_name, wells in self.tanks.items():
            for well in wells:
                prod_vector = well.prod_data
                if prod_vector is not None:
                    well_name = well.name
                    well_date = prod_vector.data.index
                    well_oil_cum = prod_vector.data[OIL_CUM_COL]
                    well_water_cum = prod_vector.data[WATER_CUM_COL]
                    well_gas_cum = prod_vector.data[GAS_CUM_COL]
                    well_liq_cum = prod_vector.data[LIQ_CUM]

                    # Create a copy of data from prod_vector
                    temp_df_prod = prod_vector.data.copy()

                    temp_df_prod[WELL_COL] = well_name
                    temp_df_prod[DATE_COL] = well_date
                    temp_df_prod[OIL_CUM_COL] = well_oil_cum
                    temp_df_prod[WATER_CUM_COL] = well_water_cum
                    temp_df_prod[GAS_CUM_COL] = well_gas_cum
                    temp_df_prod[LIQ_CUM] = well_liq_cum
                    temp_df_prod[TANK_COL] = tank_name

                    df_prod = pd.concat([df_prod, temp_df_prod], ignore_index=True)
        return df_prod

    def _calc_uw(self) -> pd.DataFrame:
        df_press = self._press_df_int()
        df_prod = self._prod_df_int()
        df_press = df_press.loc[df_press[TANK_COL] == self.name]

        # Calculate the accumulated production in the pressure dataframe, based on the production dataframe
        for col in [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]:
            df_press[col] = df_press.apply(
                lambda x: interp_dates_row(
                    x, DATE_COL, df_prod, DATE_COL, col, WELL_COL, WELL_COL, left=0.0
                ),
                axis=1,
            )
            # For wells not available in the production data frame, fill nans with 0
            df_press[col].fillna(0)

        uw_well = []
        for well, group in df_press.groupby(WELL_COL):
            group[UW_COL] = underground_withdrawal(
                group,
                OIL_CUM_COL,
                WATER_CUM_COL,
                GAS_CUM_COL,
                OIL_FVF_COL,
                WATER_FVF_COL,
                GAS_FVF_COL,
                RS_COL,
                RS_W_COL,
            )
            uw_well.append(group)

        df_press = pd.concat(uw_well, ignore_index=True)
        return df_press

    def _pressure_vol_avg(self, avg_freq: str, position: str) -> pd.DataFrame:
        df_press = self._calc_uw()
        df_press_avg = (
            df_press.groupby(TANK_COL).apply(
                lambda g: pressure_vol_avg(
                    g,
                    WELL_COL,
                    DATE_COL,
                    PRESSURE_COL,
                    UW_COL,
                    avg_freq,
                    position
                )
            ).reset_index(0)
        )
        return df_press_avg

    def mat_bal_df(self, avg_freq: str, position: str) -> pd.DataFrame:
        """
        Obtain material balance parameters at a certain frequency

        Parameters
        ----------
        avg_freq: str
            Frequency for averaging
        position: str
            Position for averaging

        Returns
        -------
        pd.DataFrame

            Dataframe with data to calculate material balance

        """
        avg = self._pressure_vol_avg(avg_freq, position)
        prod = self._prod_df_int()

        avg[PRESSURE_COL] = avg[PRESSURE_COL].interpolate(method="linear")

        cols_input = [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]
        cols_output = ["oil_vol", "water_vol", "gas_vol"]
        prod[cols_output] = (prod.groupby(WELL_COL)[cols_input]).diff().fillna(prod[cols_input])
        cols_group = [DATE_COL, TANK_COL, "oil_vol", "water_vol", "gas_vol"]
        df_tank = (
            prod[cols_group]
            .groupby(cols_group[0:2])
            .sum()
            .groupby(TANK_COL)
            .cumsum()
            .reset_index()
        )

        df_tank.rename(columns={
            "oil_vol": OIL_CUM_COL,
            "water_vol": WATER_CUM_COL,
            "gas_vol": GAS_CUM_COL
        }, inplace=True)

        oil_cum_per_tank = OIL_CUM_TANK
        water_cum_per_tank = WATER_CUM_TANK
        gas_cum_per_tank = GAS_CUM_TANK

        for col, cum_col in zip([oil_cum_per_tank, water_cum_per_tank, gas_cum_per_tank],
                                [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]):
            avg[col] = avg.apply(
                lambda g: interp_dates_row(
                    g, DATE_COL, df_tank, DATE_COL, cum_col, TANK_COL, TANK_COL
                ),
                axis=1
            )

        df_mbal = avg.sort_values(DATE_COL)

        for col, prop in zip([OIL_FVF_COL, GAS_FVF_COL, RS_COL],
                             [OIL_FVF_COL, GAS_FVF_COL, RS_COL]):
            df_mbal[col] = df_mbal[PRESSURE_COL].apply(
                lambda press: interp_pvt_matbal(df_pvt, PRESSURE_PVT_COL, prop, press)
            )
        df_mbal[RS_W_COL] = water_model.get_rs_at_press(df_mbal[PRESSURE_COL])
        df_mbal[WATER_FVF_COL] = water_model.get_bw_at_press(df_mbal[PRESSURE_COL])

        df_mbal["Time_Step"] = 365.0
        df_mbal.loc[df_mbal.index[1:], "Time_Step"] = (df_mbal[DATE_COL].diff().dt.days.iloc[1:]).cumsum() + 365.0

        return df_mbal

    def initializa_mbal_with_data(self, avg_freq: str, position: str, swo: float, cw, cf):
        mbal = self.mat_bal_df(avg_freq, position)
        mbal[UW_COL] = underground_withdrawal(mbal, OIL_CUM_TANK,
                                              WATER_CUM_TANK,
                                              GAS_CUM_TANK,
                                              OIL_FVF_COL,
                                              WATER_FVF_COL,
                                              GAS_FVF_COL,
                                              RS_COL,
                                              RS_W_COL)
        mbal[OIL_EXP] = mbal[OIL_FVF_COL] - mbal[OIL_FVF_COL][0]
        mbal[RES_EXP] = fw_expansion(mbal, OIL_FVF_COL, PRESSURE_COL, swo, cw, cf, mbal[OIL_FVF_COL][0],
                                     mbal[PRESSURE_COL][0])

        return mbal


# Quicktest
df_pvt = pd.read_csv("../resources/data_csv/pvt.csv")
#df_pvt[GAS_FVF_COL].fillna(0)

tank_dict = tank_wells
tank_name = "tank_center"
oil_model = OilModel(
    data_pvt=df_pvt,
    temperature=25,
)

water_model = WaterModel(
    correlation_bw=Bo_bw,
    correlation_rs=RS_bw,
    salinity=3000,
    temperature=200,
    unit=1
)

# Uw calc
"""uw = Tank(
    tanks=tank_dict,
    name=tank_name,
    wells=tank_dict[tank_name],
    oil_model=oil_model,
    water_model=water_model
)
print(uw._calc_uw())
# Average Pressure
avg = Tank(
    tanks=tank_dict,
    name=tank_name,
    wells=tank_dict[tank_name],
    oil_model=oil_model,
    water_model=water_model
)._pressure_vol_avg(
    avg_freq="12MS",
    position="end"
)
print(avg)"""
tank = Tank(
    tanks=tank_dict,
    name=tank_name,
    wells=tank_dict[tank_name],
    oil_model=oil_model,
    water_model=water_model
)

mbal = tank.mat_bal_df("12MS", "end")


mbal_a = tank.initializa_mbal_with_data("12MS", "end", 0.15, 3.5e-6, 0.0003)
mbal_a.to_csv("mbal_tank.csv", index=False)

from pytank.functions.function2 import G_method, G_method2, Campbell
from pytank.aquifer.influx_of_water import Fetkovich

pr = mbal["PRESSURE_DATUM"].tolist()
ts = mbal["Time_Step"].tolist()

df_we = Aquifer(
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

print(df_we["Cumulative We"])
df_we.to_csv("we_tank.csv", index=False)

# Plot Campbell
"""import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from scipy import stats
plt.scatter(ho["Eo + Efw"],ho["F-We"],)

x=ho[["Eo + Efw"]]
x1=ho["Eo + Efw"]
y=ho["F-We"]

model = LinearRegression()
model.fit(x,y)

pendiente = model.coef_[0]
intercepto = model.intercept_
slope, intercept, r, p, se = stats.linregress(x1, y)
print(f'Pendiente: {pendiente/1000000}')
print(f'Intercepto: {intercepto}')
print(f"N [MMStb]: {intercepto / 1000000:.4f}")
print(f"N [MMStb]: {intercept / 1000000:.4f}")


y_pred = model.predict(x)

plt.scatter(ho["Eo + Efw"],ho["F-We"], color='blue', label='Datos')
plt.plot(ho["Eo + Efw"], y_pred, color='red', label='Recta de regresión')


plt.title("HAVLENA")
plt.legend()

plt.show()"""


# Ellos"""

"""we = df_we["Cumulative We"]

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
from sktlearn.linear_model import LinearRegression
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
print(f"N [MMStb]: {intercept / 1000000:.4f}")

# Generar los valores predichos para la recta de regresión
y_pred = model.predict(x)

# Graficar los puntos y la recta de regresión
plt.scatter(poes["We*Bw/Et"],poes["F/Eo+Efw"], color='blue', label='Datos')
plt.plot(poes["We*Bw/Et"], y_pred, color='red', label='Recta de regresión')

# Añadir etiquetas y título
plt.title("HAVLENA")
plt.legend()

# Mostrar el gráfico
plt.show()"""
