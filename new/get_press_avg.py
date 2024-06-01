from get_wells import tank_wells
from new.constants import (OIL_FVF_COL,GAS_FVF_COL,RS_COL, PRESSURE_COL,OIL_CUM_COL,GAS_CUM_COL,WATER_CUM_COL,DATE_COL,WELL_COL, WATER_FVF_COL, RS_W_COL
                           )
import pandas as pd
from fluid import OilModel, WaterModel
from new.utilities import interp_dates_row
#from uw import underground_widrawal
from old.utilities.pvt_correlations import RS_bw, Bo_bw
from old.material_balance import underground_withdrawal

df_pvt = pd.read_csv("../old/tests/data_for_tests/full_example_1/pvt.csv")

all_pressure_vectors = []
all_production_vectors = []

for tank,wells in tank_wells.items():
    for well in wells:
        if well.press_data is not None:
            all_pressure_vectors.append(well.press_data)
        if well.prod_data is not None:
            all_production_vectors.append(well.prod_data)

print(len(all_pressure_vectors))

for press_vector, prod_vector in zip(all_pressure_vectors, all_production_vectors):
    if press_vector is not None and prod_vector is not None:
        pvt = OilModel(data_pvt=df_pvt,temperature=25)
        press_vector.data[OIL_FVF_COL] = pvt.get_bo_at_press(press_vector.data[PRESSURE_COL])
        press_vector.data[GAS_FVF_COL] = pvt.get_bg_at_press(press_vector.data[PRESSURE_COL])
        press_vector.data[RS_COL] = pvt.get_rs_at_press(press_vector.data[PRESSURE_COL])
        press_vector.data[WATER_FVF_COL] = WaterModel(correlation_bw=Bo_bw,correlation_rs=RS_bw, salinity=3000,temperature=200,
                                                      unit=1).get_bw_at_press(press_vector.data[PRESSURE_COL])
        press_vector.data[RS_W_COL] = WaterModel(correlation_bw=Bo_bw,correlation_rs=RS_bw, salinity=3000,temperature=200,
                                                 unit=1).get_rs_at_press(press_vector.data[PRESSURE_COL])
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

        """prod_vector.data.drop([DATE_COL, WELL_COL], axis=1, inplace=True)
        press_vector.data.drop([DATE_COL, WELL_COL], axis=1, inplace=True)
        press_vector.data["UW"] = underground_widrawal(press_vector)"""

        press_vector.data["UW"] = underground_withdrawal(press_vector,
                                                         OIL_CUM_COL,
                                                         WATER_CUM_COL,
                                                         GAS_CUM_COL,
                                                         OIL_FVF_COL,
                                                         1,
                                                         GAS_FVF_COL,
                                                         RS_COL,
                                                         0
                                                         )

        print(press_vector)