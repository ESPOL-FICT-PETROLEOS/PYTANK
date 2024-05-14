from new.vector_data import PressVector
from new.constants import OIL_CUM_COL,WATER_CUM_COL,GAS_CUM_COL,OIL_FVF_COL,GAS_FVF_COL,RS_COL, WATER_FVF_COL,RS_W_COL

def underground_widrawal(
        press_vector: PressVector
):
    oil_vol = press_vector.data[OIL_CUM_COL].diff().fillna(press_vector.data[OIL_CUM_COL])
    water_vol = press_vector.data[WATER_CUM_COL].diff().fillna(press_vector.data[WATER_CUM_COL])
    gas_vol = press_vector.data[GAS_CUM_COL].diff().fillna(press_vector.data[GAS_CUM_COL])

    bo = press_vector.data[OIL_FVF_COL]
    bg = press_vector.data[GAS_FVF_COL]
    gor = press_vector.data[RS_COL]
    bw = press_vector.data[WATER_FVF_COL]
    rs_w = press_vector.data[RS_W_COL]

    #modificar tomando en cuenta la ecuación real, faltan datos como rsw_col, water_fvf_col
    gas_withdrawal = (gas_vol - oil_vol * gor - water_vol * rs_w) * bg

    if sum(gas_withdrawal < 0) > 0:
        raise   ArithmeticError("Gas withdrawal results in negative values")

    gas_withdrawal.fillna(0, inplace=True)

    uw = (oil_vol * bo + water_vol * bw + gas_withdrawal)

    return uw.cumsum().values

