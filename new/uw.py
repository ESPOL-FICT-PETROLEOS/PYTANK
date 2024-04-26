from new.vector_data import ProdVector,PressVector
from new.constants import OIL_CUM_COL,WATER_CUM_COL,GAS_CUM_COL,PRESSURE_COL

def underground_widrawal(
        prod_vector: ProdVector,
        press_vector: PressVector
):
    oil_vol = prod_vector.data[OIL_CUM_COL].diff().fillna(prod_vector.data[OIL_CUM_COL])
    water_vol = prod_vector.data[WATER_CUM_COL].diff().fillna(prod_vector.data[WATER_CUM_COL])
    gas_vol = prod_vector.data[GAS_CUM_COL].diff().fillna(prod_vector.data[GAS_CUM_COL])

    pressure = press_vector.data[PRESSURE_COL]
    bo = press_vector.data["Bo"]
    bg = press_vector.data["Bg"]
    gor = press_vector.data["GOR"]

    #modificar tomando en cuenta la ecuación real, faltan datos como rsw_col, water_fvf_col
    gas_withdrawal = (gas_vol - oil_vol * gor) * bg

    if sum(gas_withdrawal < 0) > 0:
        raise   ArithmeticError("Gas withdrawal results in negative values")

    gas_withdrawal.fillna(0, inplace=True)

    uw = oil_vol * bo + water_vol + gas_withdrawal

    return uw.cumsum().values

