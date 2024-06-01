import pandas as pd
from pydantic import BaseModel
from well import Well
from typing import Optional, List
from new.constants import (OIL_FVF_COL,
                           GAS_FVF_COL,
                           RS_COL,
                           PRESSURE_COL,
                           OIL_CUM_COL,
                           GAS_CUM_COL,
                           WATER_CUM_COL,
                           DATE_COL,
                           WELL_COL,
                           WATER_FVF_COL,
                           RS_W_COL
                           )
from fluid import OilModel, WaterModel
from new.utilities import interp_dates_row
from old.utilities.pvt_correlations import RS_bw, Bo_bw
from get_wells import tank_wells
from old.material_balance import pressure_vol_avg

class Tank(BaseModel):
    name: str
    wells: list
    oil_model: OilModel
    water_model: WaterModel

    def __init__(self, name: str, wells: list, oil_model: OilModel, water_model: WaterModel):
        super().__init__(name=name, wells=wells, oil_model=oil_model, water_model=water_model)

    def _press_pvt(self, press_vector):
        """
        Private method that internally manages the pressure vector for use in the UW method

        Parameters
        ----------
        press_vector: Pressure vector from the well class

        Returns
        -------
        A pressure vector with PVT properties
        """
        if press_vector is not None:
            press_vector.data[OIL_FVF_COL] = self.oil_model.get_bo_at_press(press_vector.data[PRESSURE_COL])
            press_vector.data[GAS_FVF_COL] = self.oil_model.get_bg_at_press(press_vector.data[PRESSURE_COL])
            press_vector.data[RS_COL] = self.oil_model.get_rs_at_press(press_vector.data[PRESSURE_COL])
            press_vector.data[WATER_FVF_COL] = self.water_model.get_bw_at_press(press_vector.data[PRESSURE_COL])
            press_vector.data[RS_W_COL] = self.water_model.get_rs_at_press(press_vector.data[PRESSURE_COL])
        return press_vector

    def _press_prod(self, well, press_vector, prod_vector):
        """
        Private method that internally manages the pressure and production vector for use in the UW method

        Parameters
        ----------
        well: name of each of the wells from the Well class
        press_vector: Pressure vector from the well clas
        prod_vector: Production vector from the well clas

        Returns
        -------
        A modified pressure vector with production interpolation according to the pressures

        """
        if press_vector is None or prod_vector is None:
            return

        for col in [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]:
            prod_vector.data[DATE_COL] = prod_vector.data.index
            prod_vector.data[WELL_COL] = well.name
            press_vector.data[DATE_COL] = press_vector.data.index
            press_vector.data[WELL_COL] = well.name
            press_vector.data[col] = press_vector.data.apply(
                lambda x: interp_dates_row(
                    x, DATE_COL, prod_vector.data, DATE_COL, col, WELL_COL, WELL_COL, left=0.0
                ),
                axis=1,
            )
            press_vector.data[col].fillna(0, inplace=True)
            prod_vector.data.drop([DATE_COL, WELL_COL], axis=1, inplace=True)
            press_vector.data.drop([DATE_COL, WELL_COL], axis=1, inplace=True)
        return press_vector

    def calc_uw(self):

        for well in self.wells:
            press_vector = well.press_data
            prod_vector = well.prod_data

            press_vector = self._press_pvt(press_vector)
            press_vector = self._press_prod(well, press_vector, prod_vector)

            if press_vector is None:
                continue

            oil_vol = press_vector.data[OIL_CUM_COL].diff().fillna(press_vector.data[OIL_CUM_COL])
            water_vol = press_vector.data[WATER_CUM_COL].diff().fillna(press_vector.data[WATER_CUM_COL])
            gas_vol = press_vector.data[GAS_CUM_COL].diff().fillna(press_vector.data[GAS_CUM_COL])

            bo = press_vector.data[OIL_FVF_COL]
            bg = press_vector.data[GAS_FVF_COL]
            gor = press_vector.data[RS_COL]
            bw = press_vector.data[WATER_FVF_COL]
            rs_w = press_vector.data[RS_W_COL]
            gas_withdrawal = (gas_vol - oil_vol * gor - water_vol * rs_w) * bg

            if sum(gas_withdrawal < 0) > 0:
                raise ArithmeticError("Gas withdrawal results in negative values")

            gas_withdrawal.fillna(0, inplace=True)

            uw = (oil_vol * bo + water_vol * bw + gas_withdrawal)

            press_vector.data["UW"] = uw.cumsum().values

            return press_vector.data


    """def pressure_vol_avg(self, avg_freq:str):
        press_vector = self.calc_uw()
        for well in self.wells:
            df_press_avg = pressure_vol_avg(
                press_vector.data,
                well,
                press_vector.data.index,
                press_vector.data[PRESSURE_COL],
                press_vector.data["UW"],
                avg_freq,
                "end"
                    ).reset_index()
        return df_press_avg"""

# Quicktest
df_pvt = pd.read_csv("../old/tests/data_for_tests/full_example_1/pvt.csv")
tank_dict = tank_wells
tank_name = list(tank_wells.keys())[0]
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

uw = Tank(
    name=tank_name,
    wells=tank_dict[tank_name],
    oil_model=oil_model,
    water_model=water_model
).calc_uw()


print(tank_wells["tank_center"][0])

