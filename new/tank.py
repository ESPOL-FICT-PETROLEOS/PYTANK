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
from fluid import FluidModel, WaterFluidModel
from new.utilities import interp_dates_row
from old.utilities.pvt_correlations import RS_bw, Bo_bw
from get_wells import tank_wells

class Tank(BaseModel):
    name: str
    wells: list
    oil_model: FluidModel

    def __init__(self, name: str, wells: list, oil_model: FluidModel):
        super().__init__(name=name, wells=wells, oil_model=oil_model)

    def calc_prod(self):
        pass

    def calc_uw(self):
        uw_values = []

        for well in self.wells:
            press_vector = well.press_data
            prod_vector = well.prod_data
            if press_vector is not None:
                press_vector.data[OIL_FVF_COL] = self.oil_model.get_bo_at_press(press_vector.data[PRESSURE_COL])
                press_vector.data[GAS_FVF_COL] = self.oil_model.get_bg_at_press(press_vector.data[PRESSURE_COL])
                press_vector.data[RS_COL] = self.oil_model.get_rs_at_press(press_vector.data[PRESSURE_COL])
                press_vector.data[WATER_FVF_COL] = WaterFluidModel(correlation=Bo_bw).get_rs_at_press(
                    press_vector.data[PRESSURE_COL], 220, 3000, unit=1)
                press_vector.data[RS_W_COL] = WaterFluidModel(correlation=RS_bw).get_rs_at_press(
                    press_vector.data[PRESSURE_COL], 220, 3000, unit=1)

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

    def calc_press_avg(self):
        pass

# Quicktest
df_pvt = pd.read_csv("../old/tests/data_for_tests/full_example_1/pvt.csv")
tank = list(tank_wells.keys())[0]
pvt = FluidModel(
    data_pvt=df_pvt,
    temperature=25,
)

uw = Tank(
    name=tank,
    wells=tank_wells[tank],
    oil_model=pvt
).calc_uw()

print(tank_wells["tank_center"][0])
print(tank_wells["tank_north"][0])
print(tank_wells["tank_south"][0])
print(tank_wells["No_tank"][0])
