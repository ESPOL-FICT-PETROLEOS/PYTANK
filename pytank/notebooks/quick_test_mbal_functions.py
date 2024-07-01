from pytank.functions.material_balance import (fw_expansion, gas_expansion,
                                               ho_terms_equation,
                                               campbell_function,
                                               oil_expansion)
from pytank.notebooks.quick_test_analysis import analysis2

# Call dataframe of tank
df_mbal = analysis2.mat_bal_df().fillna(0.0)

# Some required data
water_sat = 0.15
rock_comp = 3.5e-6
water_comp = 3.62e-6
water_fvf = 1.0
gas_water_rs = 0
oil_fvf_init = 1.12
gas_fvf_init = 0.04
tot_fvf_init = 0.60
gas_oil_rs_init = 89
pressure_init = 3700

# Calculate Oil Expansion
eo = oil_expansion(
    df_mbal,
    "Bo",
    "Bg",
    "GOR",
    gas_oil_rs_init,
    oil_fvf_init,
)
print(eo)

# Calculate Gas Expansion
eg = gas_expansion(df_mbal, "Bo", "Bg", gas_fvf_init,
                   tot_fvf_init)
print(eg)

# Calculate Rock and Fluid Expansion
efw = fw_expansion(df_mbal, "Bo", "PRESSURE_DATUM", water_sat,
                   water_comp,
                   rock_comp, oil_fvf_init, pressure_init)
print(efw)

# Calculate Ho Terms
ho = ho_terms_equation(df_mbal, "OIL_CUM_TANK",
                       "WATER_CUM_TANK",
                       "GAS_CUM_TANK", "PRESSURE_DATUM",
                       "Bo", "Bg", "GOR",
                       "Bw", gas_water_rs, water_sat, water_comp,
                       rock_comp,
                       oil_fvf_init, gas_fvf_init, tot_fvf_init,
                       gas_oil_rs_init, pressure_init)
print(ho.columns)

# Campbell Function
camp = campbell_function(df_mbal, "OIL_CUM_TANK",
                         "WATER_CUM_TANK",
                         "GAS_CUM_TANK", "PRESSURE_DATUM",
                         "F", "Eo", "Efw",
                         "Bo", "Bg", "GOR",
                         "Bw", gas_water_rs, water_sat,
                         water_comp, rock_comp, oil_fvf_init, gas_fvf_init,
                         tot_fvf_init, gas_oil_rs_init, pressure_init)
