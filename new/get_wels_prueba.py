# %%
import pandas as pd
from new.constants import OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM, PRESSURE_COL
from new.vector_data import ProdVector, PressVector
from new.well import Well
from new.utilities import normalize_date_freq
from old.utilities import interp_dates_row


# Leer los datos de producción y presiones
df_production = pd.read_csv("../old/tests/data_for_tests/full_example_1/production.csv")
df_pressures = pd.read_csv("../old/tests/data_for_tests/full_example_1/pressures.csv")

# Renombrar columnas para que coincidan
df_pressures.rename(columns={"DATE": "START_DATETIME", "WELLBORE": "ITEM_NAME"}, inplace=True)
df_production["START_DATETIME"] = pd.to_datetime(df_production["START_DATETIME"])
df_pressures["START_DATETIME"] = pd.to_datetime(df_pressures["START_DATETIME"])

# Fusionar los DataFrames por pozo
df_combined = pd.concat([df_production, df_pressures])

# Ordenar el DataFrame combinado por nombre de pozo y luego por fecha
df_combined.sort_values(by=["ITEM_NAME", "START_DATETIME"], inplace=True)


#%%
# %%
import pandas as pd
from new.constants import OIL_CUM_COL, WATER_CUM_COL, GAS_CUM_COL, LIQ_CUM, PRESSURE_COL,DATE_COL, PRESSURE_COL,WELL_COL
from new.vector_data import ProdVector, PressVector
from new.well import Well
from new.utilities import normalize_date_freq
from old.utilities import interp_dates_row

#Data to process
df_production = pd.read_csv("C:/Users/ksls2/PycharmProjects/PYTANK/new/data_files/production.csv")
df_production[DATE_COL] = pd.to_datetime(df_production[DATE_COL])
df_production.set_index(df_production[DATE_COL], inplace=True)
prod_wells = []

# Group data by well name and apply the function to create ProdWell objects
for name, group in df_production.groupby(WELL_COL):
    #print(f"Creating well {name}")

    group = group.rename(
        columns={
            OIL_CUM_COL: OIL_CUM_COL,
            WATER_CUM_COL: WATER_CUM_COL,
            GAS_CUM_COL: GAS_CUM_COL,
        }
    )
    group[LIQ_CUM] = group[OIL_CUM_COL] + group[WATER_CUM_COL]

    prod_vector = ProdVector(
        freq=None,
        data=group
    )

    # Create rates colums
    oil_rates = prod_vector.calculate_rate(OIL_CUM_COL)
    water_rates = prod_vector.calculate_rate(WATER_CUM_COL)
    prod_vector.data["OIL_RATE"] = oil_rates
    prod_vector.data["WATER_RATE"] = water_rates

    # Interpolated dates
    date_interpo = normalize_date_freq(prod_vector.data,
                                       "MS",
                                       cols_fill_na=["OIL_RATE", "WATER_RATE"],
                                       method_no_cols="ffill")
    prod_vector.data = date_interpo

    # Calculate new rates based on interpolated dates
    prod_vector.data["OIL_RATE"] = prod_vector.calculate_rate(OIL_CUM_COL)
    prod_vector.data["WATER_RATE"] = prod_vector.calculate_rate(WATER_CUM_COL)

    # Create the well
    prod_well = Well(
        name=name,
        vector_data=prod_vector,
    )
    prod_wells.append(prod_well)
#print(prod_wells)

df_pressures = pd.read_csv("C:/Users/ksls2/PycharmProjects/PYTANK/new/data_files/pressures.csv")
#df_pressures.rename(columns={"DATE":"START_DATETIME"}, inplace=True)
df_pressures[DATE_COL] = pd.to_datetime(df_pressures[DATE_COL])

df_pressures.set_index(df_pressures[DATE_COL], inplace=True)
pressures_wells = []

for name, group in df_pressures.groupby(WELL_COL):
    print(f"Creating well pressures {name}")
    group = group.rename(
        columns={
            PRESSURE_COL: PRESSURE_COL
        }
    )
    press_vector = PressVector(
        freq=None,
        data=group
    )

    press_well = Well(
        name=name,
        vector_data=press_vector
    )
    pressures_wells.append(press_well)

print(prod_wells)

# Iterar sobre la lista de pozos de producción
for prod_well in prod_wells:
    # Buscar el pozo correspondiente en la lista de pozos de presión
    for press_well in pressures_wells:
        if prod_well.name == press_well.name:
            # Fusionar los vectores de producción y presión
            combined_data = pd.concat([prod_well.vector_data.data, press_well.vector_data.data], axis=1)
            # Normalizar la frecuencia del DataFrame
            combined_data = normalize_date_freq(combined_data, freq= "D")
            # Agregar el DataFrame fusionado como un atributo del objeto Well
            prod_well.vector_data.data = combined_data
            # Romper el bucle una vez que se ha encontrado el pozo correspondiente
            break

a=prod_wells[0].vector_data.data

# Work pressure info
# Data to process
df_pressures = pd.read_csv("../old/tests/data_for_tests/full_example_1/pressures.csv")
df_pressures.rename(columns={"DATE":"START_DATETIME"}, inplace=True)
df_pressures["START_DATETIME"] = pd.to_datetime(df_pressures["START_DATETIME"])

df_pressures.set_index(df_pressures["START_DATETIME"], inplace=True)
pressures_wells = []


for name, group in df_pressures.groupby("WELLBORE"):
    #print(f"Creating well pressures {name}")
    group = group.rename(
        columns={
            PRESSURE_COL: PRESSURE_COL
        }
    )
    press_vector = PressVector(
        freq=None,
        data=group
    )

    press_well = Well(
        name=name,
        vector_data=press_vector
    )
    pressures_wells.append(press_well)

unified_wells = []

for prod_well in prod_wells:
    # Search the well in the list
    found = False
    for press_well in pressures_wells:
        if prod_well.name.strip() == press_well.name.strip():
            # Both df
            unified_data = pd.merge(prod_well.vector_data.data, press_well.vector_data.data, how='outer',
                                    left_index=True, right_index=True)

            unified_vector_data = VectorData(freq=None,
                                             data=unified_data)

            # Create a new object
            unified_well = Well(name=prod_well.name,
                                vector_data=unified_vector_data)

            # Agg the new object to a list
            unified_wells.append(unified_well)
            found = True
            break

    if not found:
        # Si el pozo de producción no tiene un equivalente en los datos de presión, agregarlo sin modificar sus datos
        unified_wells.append(prod_well)

for well in unified_wells:
    print(well.name)
    print(well.vector_data)

