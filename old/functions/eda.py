import pandas as pd
from old.utilities import days_in_month
from old.utilities import interp_dates_row
import matplotlib.ticker as ticker
from scipy.interpolate import interp1d
from old.material_balance.material_balance import (
    underground_withdrawal,
    pressure_vol_avg,
)

formatter = ticker.EngFormatter()

# %% specify files to load
production_file = "C:/Users/CompuMundo/PycharmProjects/PYTANK/old/tests/data_for_tests/full_example_1/production.csv"
pressure_file = "C:/Users/CompuMundo/PycharmProjects/PYTANK/old/tests/data_for_tests/full_example_1/pressures.csv"
pvt_file = "C:/Users/CompuMundo/PycharmProjects/PYTANK/old/tests/data_for_tests/full_example_1/pvt.csv"

# %% Load data into dataframes
df_prod = pd.read_csv(production_file)
df_press = pd.read_csv(pressure_file)
df_pvt = pd.read_csv(pvt_file)

# %% Cast date column to date
date_col = "START_DATETIME"
df_prod[date_col] = pd.to_datetime(df_prod["START_DATETIME"])

# %% Define data frame columns
# Input
oil_cum_col = "OIL_CUM"
water_cum_col = "WATER_CUM"
gas_cum_col = "GAS_CUM"
well_name_col = "ITEM_NAME"
tank_name_col = "Tank"
# Output
cal_day_col = "cal_day"
oil_rate_col = "oil_rate"
water_rate_col = "water_rate"
gas_rate_col = "gas_rate"
liquid_rate_col = "liquid_rate"
liquid_cum_col = "liquid_cum"

# %% Calculate Rates
# Calculate the calendar days
df_prod[cal_day_col] = df_prod[date_col].map(lambda date: days_in_month(date))

# Define the input and output columns
cols_input = [oil_cum_col, water_cum_col, gas_cum_col]
cols_output = [oil_rate_col, water_rate_col, gas_rate_col]

# Calculate the rates using the differences between cumulatives
# df_input = df_prod[[well_name_col, *cols_input]]
# df_prod[cols_output] = (df_input.groupby(well_name_col).diff().fillna(df_input)
#                        .div(df_prod[cal_day_col], axis=0))

# Calculate liquid production rate and cumulative


# %% Housekeeping of pressure data frame
# Rename column names for pressure data frame to use the same as the production one
df_press.rename(columns={"WELLBORE": well_name_col, "DATE": date_col}, inplace=True)
# Make sure the date column is o datetime object
df_press[date_col] = pd.to_datetime(df_press[date_col])
# Specify important columns
press_col = "PRESSURE_DATUM"
press_type_col = "TEST_TYPE"

# %% 1.- #Interpolate PC information

# Define the fluid properties column names for the df pressure
oil_fvf_col = "Bo"
gas_oil_rs_col = "Rs"
gas_fvf_col = "Bg"

oil_fvf_interp = interp1d(df_pvt["Pressure"], df_pvt["Bo"], fill_value="extrapolate")

gas_oil_rs_interp = interp1d(
    df_pvt["Pressure"], df_pvt["GOR"], fill_value="extrapolate"
)

gas_fvf_interp = interp1d(df_pvt["Pressure"], df_pvt["Bg"], fill_value="extrapolate")

# 2.- Apply the functions to the pressure df
df_press[oil_fvf_col] = oil_fvf_interp(df_press[press_col])
df_press[gas_oil_rs_col] = gas_oil_rs_interp(df_press[press_col])
df_press[gas_fvf_col] = gas_fvf_interp(df_press[press_col])
print(oil_fvf_interp)
print(gas_fvf_interp)
print(gas_oil_rs_interp)
# %% Interpolate oil, gas and water cumulatives into the pressure data frame
for col in cols_input:
    df_press[col] = df_press.apply(
        lambda x: interp_dates_row(
            x, date_col, df_prod, date_col, col, well_name_col, well_name_col, left=0.0
        ),
        axis=1,
    )
    # For wells not available in the production data frame, fill nans with 0
    df_press[col].fillna(0, inplace=True)

presscsv = df_press.to_csv("interpolado.csv")
# %% Calculate underground withdrawal for each well
uw_col = "UW"

df_press[uw_col] = underground_withdrawal(
    df_press,
    oil_cum_col,
    water_cum_col,
    gas_cum_col,
    oil_fvf_col,
    1,
    gas_fvf_col,
    gas_oil_rs_col,
    0,
)
print(df_press.columns)
# %% Calculate the pressure volumetric average per tank
avg_freq = "12MS"
df_press_avg = (
    df_press.groupby(tank_name_col)
    .apply(
        lambda g: pressure_vol_avg(
            g, well_name_col, date_col, press_col, uw_col, avg_freq, "end"
        )
    )
    .reset_index(0)
)
press_avg = df_press_avg.to_csv("press_avg.csv", index=False)
