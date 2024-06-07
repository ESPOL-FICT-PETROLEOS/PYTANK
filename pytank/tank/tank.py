import pandas as pd
from pydantic import BaseModel
from pytank.constants.constants import (OIL_FVF_COL,
                                        GAS_FVF_COL,
                                        RS_COL,
                                        PRESSURE_COL,
                                        OIL_CUM_COL,
                                        GAS_CUM_COL,
                                        WATER_CUM_COL,
                                        DATE_COL,
                                        WELL_COL,
                                        WATER_FVF_COL,
                                        RS_W_COL,
                                        TANK_COL,
                                        LIQ_CUM,
                                        UW_COL)
from pytank.fluid_model.fluid import OilModel, WaterModel
from pytank.functions.utilities import interp_dates_row
from pytank.functions.pvt_correlations import RS_bw, Bo_bw
from pytank.notebooks.get_wells import tank_wells
from pytank.functions.material_balance import underground_withdrawal, pressure_vol_avg


class Tank(BaseModel):
    tanks: dict
    name: str
    wells: list
    oil_model: OilModel
    water_model: WaterModel

    def __init__(self, tanks: dict, name: str, wells: list, oil_model: OilModel, water_model: WaterModel):
        super().__init__(tanks=tanks, name=name, wells=wells, oil_model=oil_model, water_model=water_model)

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

    def _prod_df_int(self):
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

                    df_prod = pd.concat([df_prod, temp_df_prod], ignore_index=True)
        return df_prod

    def calc_uw(self) -> pd.DataFrame:
        df_press = self._press_df_int()
        df_prod = self._prod_df_int()

        # Calculate the accumulated production in the pressure dataframe, based on the production dataframe
        for col in [OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL]:
            df_press[col] = df_press.apply(
                lambda x: interp_dates_row(
                    x, DATE_COL, df_prod, DATE_COL, col, WELL_COL, WELL_COL, left=0.0
                ),
                axis=1,
            )
            # For wells not available in the production data frame, fill nans with 0
            df_press[col].fillna(0, inplace=True)

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

    def pressure_vol_avg(self, avg_freq: str, position: str) -> pd.DataFrame:
        df_press = self.calc_uw()
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


# Quicktest
df_pvt = pd.read_csv("../resources/data_csv/pvt.csv")
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

# Uw calc
uw = Tank(
    tanks=tank_dict,
    name=tank_name,
    wells=tank_dict[tank_name],
    oil_model=oil_model,
    water_model=water_model
).calc_uw()

print(uw)
uw.to_csv("uw_tank.csv", index=False)

# Average Pressure
avg = Tank(
    tanks=tank_dict,
    name=tank_name,
    wells=tank_dict[tank_name],
    oil_model=oil_model,
    water_model=water_model
).pressure_vol_avg(
    avg_freq="12MS",
    position="end"
)

print(avg)
