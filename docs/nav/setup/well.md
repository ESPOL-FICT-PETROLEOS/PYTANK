# **¿What is a Well?**

A well, from a reservoir engineering perspective, is defined as a cylindrical
borehole drilled into the subsurface for the purpose of exploring, evaluating or
exploiting a hydrocarbon reservoir. There are different types of wells:

## **Exploration Wells**

They are drilled to determine if a hydrocarbon reservoir exists in a specific
location. They provide geological and reservoir information that is used to
evaluate the feasibility of developing the field.

## **Development or Production Wells**

They are drilled in an existing field to exploit the reservoir and produce
hydrocarbons. This category includes vertical, horizontal and multilateral
wells.

## **Injection wells**

They are used to inject fluids (water, gas or chemicals) into the reservoir to
maintain pressure and improve hydrocarbon recovery.

## **The Well class**

The Well class is defined as a model class using the Pydantic library. Pydantic
is a data validation library that provides an elegant way to define and validate
data structures.

### **Classification of the Well class**

The Well class is classified as a data model class that is used to group
production and pressure information by well. It provides an organized structure
for storing and managing data related to hydrocarbon production wells.

### **Explanation of the Well class**

**The Well class comprises the following attributes:**

- `name`: a field of type str representing the name of the well.
- `prod_data`: an optional field of type ProdVector that stores the production
  data of the well.
- `press_data`: an optional field of type PressVector that stores the well's
  pressure data.

The *Well* class is used to group and manage information related to a specific
well. It allows storing and accessing production and pressure data associated
with each well in an organized and structured manner.

By using the *Well* class, individual *well* instances can be created, each with
its own name and associated production and pressure data. This facilitates the
management and analysis of *well* information in the context of reservoir
engineering.

## **Steps to create a well instance**

### 1. *Import Libraries*

```
import pandas as pd # Import the pandas library for data manipulation
from pytank.vector_data import 
     ProdVector, PressVector # Import ProdVector and PressVector classes
from pytank.well import Well # Import the Well class
```

### 2. *Create a sample DataFrame for production and pressure data*

```
prod_df = pd.DataFrame({  # Initialize a DataFrame with production data
    'START_DATETIME': ['2022-01-01', '2022-02-01', '2022-03-01'],
    # Dates for production entries
    'OIL_CUM': [100, 150, 200],  # Cumulative oil production values
    'WATER_CUM': [50, 75, 100],  # Cumulative water production values
    'GAS_CUM': [100, 150, 200],  # Cumulative gas production values
    'LIQ_CUM': [150, 225, 300]  # Cumulative liquid production values
})

prod_df.set_index(prod_df['START_DATETIME'],
                  inplace=True)  # Set the 'START_DATETIME' as the index of the DataFrame
```

```
print(prod_df)
```

```
               START_DATETIME  OIL_CUM  WATER_CUM  GAS_CUM  LIQ_CUM
START_DATETIME                                                     
2022-01-01         2022-01-01      100         50      100      150
2022-02-01         2022-02-01      150         75      150      225
2022-03-01         2022-03-01      200        100      200      300
```

```
press_df = pd.DataFrame({  # Initialize a DataFrame with pressure data
    'START_DATETIME': ["2022-01-05", "2022-01-26", "2022-02-12"],
    # Dates for pressure entries
    'PRESSURE_DATUM': [3000, 2930, 2900]  # Pressure values recorded
})

press_df.set_index(press_df['START_DATETIME'],
                   inplace=True)  # Set the 'START_DATETIME' as the index of the DataFrame
```

```
print(press_df)
```

```
               START_DATETIME  PRESSURE_DATUM
START_DATETIME                               
2022-01-05         2022-01-05            3000
2022-01-26         2022-01-26            2930
2022-02-12         2022-02-12            2900
```

### 3. *Create ProdVector and PressVector instances*

```
prod_vector = ProdVector(data=prod_df,
                         freq='MS')  # Create a ProdVector instance with monthly frequency

press_vector = PressVector(data=press_df,
                           freq=None)  # Create a PressVector instance without specified frequency
```

### 4. *Create an instance of the Well class*

```
well_instance = Well(name='Well_A', prod_data=prod_vector,
                     # Instantiate Well with name and production data
                     press_data=press_vector)  # Include pressure data in the Well instance
```

```
# Accessing the data
print(f"Well Name: {well_instance.name}")  # Print the name of the well
print("Production Data:")  # Print header for production data
print(well_instance.prod_data.data)  # Print the production data associated with the well
print("Pressure Data:")  # Print header for pressure data
print(well_instance.press_data.data)  # Print the pressure data associated with the well
```

```
Well Name: Well_A
Production Data:
                OIL_CUM  WATER_CUM  GAS_CUM  LIQ_CUM
START_DATETIME                                      
2022-01-01        100.0       50.0    100.0    150.0
2022-02-01        150.0       75.0    150.0    225.0
2022-03-01        200.0      100.0    200.0    300.0
Pressure Data:
                PRESSURE_DATUM
START_DATETIME                
2022-01-05              3000.0
2022-01-26              2930.0
2022-02-12              2900.0
```

## **¿How to create multiple wells?**

It seems a bit tedious to develop a script with which you can create wells to
develop your analysis, doesn't it?. Pytank offers two functions that will
help you to speed up this information processing, as long as you take into
account the format that your files must have, you can consult the information in
the *format notes*, in pytank [quick start guide](../setup/quick_starter.ipynb).
More information on these two functions can be found in the documentation of the
[supporting functions](../API/generated/helpers.md).

### **Create Wells Functions**

The `create_wells` function is responsible for creating a list of Well objects
from the production and pressure data provided in the form of pandas DataFrames.
This function processes the data, normalizes the frequencies and generates
ProdVector and PressVector instances for each well.

### **Search for your wells**

The `search_wells` function searches for wells in a list of existing wells based
on the provided well names. It returns a list of Well objects matching the
requested well names.

### **Create your list of wells**

The two functions together will help you group the production and pressure
information of the different wells you own. With this information processed you
can use the other functions to develop your analysis as you see fit.

**Let's see an example**

```
wells = create_wells(df_prod=df_production,
                     df_press=df_pressures,
                     freq_prod="MS",
                     freq_press=None)
```

**List of wells for user selection**

```
my_wells = [
    "A-1-P", "A-10-P", "A-11-P", "A-12-P", "A-13-P", "A-14-P", "A-16-P",
    "A-17-P", "A-18-P", "A-19-P", "A-21-P", "A-22-P", "A-23-P", "A-24-I",
    "A-4-P", "A-5-P", "A-6-P", "A-8-P", "A-9-P"
]
```

**lis of wells with the pressure and production info for user selection**

```
wells_info = search_wells(wells, my_wells)
```

If you execute the order of the functions correctly, and you have formatted your
dataset correctly, you will get a result similar to this from the list of your
wells as objects.

```
Well(name='A-13-P', prod_data=ProdVector(is_result=False, 
data_schema=<Schema DataFrameSchema(columns={'OIL_CUM': 
<Schema Column(name=OIL_CUM, type=DataType(float64))>, 'WATER_CUM': 
<Schema Column(name=WATER_CUM, type=DataType(float64))>, 'GAS_CUM': 
<Schema Column(name=GAS_CUM, type=DataType(float64))>, 'LIQ_CUM': 
<Schema Column(name=LIQ_CUM, type=DataType(float64))>}, checks=[], parsers=[], 
index=None, dtype=None, coerce=False, strict=filter, name=None, ordered=False, 
unique=None, report_duplicates=all, unique_column_names=False, 
add_missing_columns=False, title=None, description=None, metadata=None, 
drop_invalid_rows=False)>, freq='MS', use_pressure=False, data=                        
START_DATETIME    OIL_CUM  WATER_CUM    GAS_CUM    LIQ_CUM                                      
2002-11-01        6217.00     101.00    6217.00    6318.00
2002-12-01       17310.00     575.00   17310.00   17885.00
2003-01-01       30601.00     750.00   30601.00   31351.00
2003-02-01       39152.00     978.00   39152.00   40130.00
2003-03-01       46650.00    1234.00   46650.00   47884.00
...                   ...        ...        ...        ...
2015-08-01      456583.11   44371.24  456583.11  500954.35
2015-09-01      456583.11   44371.24  456583.11  500954.35
2015-10-01      456583.11   44371.24  456583.11  500954.35
2015-11-01      456583.11   44371.24  456583.11  500954.35
2015-12-01      456583.11   44371.24  456583.11  500954.35

[158 rows x 4 columns]), press_data=PressVector(is_result=False, 
data_schema=<Schema DataFrameSchema(columns={'PRESSURE_DATUM': 
<Schema Column(name=PRESSURE_DATUM, type=DataType(float64))>}, 
checks=[], parsers=[], index=None, dtype=None, coerce=False, strict=filter, 
name=None, ordered=False, unique=None, report_duplicates=all, 
unique_column_names=False, add_missing_columns=False, title=None, 
description=None, metadata=None, drop_invalid_rows=False)>, freq=None, 
use_pressure=False, data=                
START_DATETIME  PRESSURE_DATUM              
2002-11-06         2193.242118
2002-12-03         2042.342826)), Well(name='A-10-P', 
prod_data=ProdVector(is_result=False, data_schema=<Schema 
DataFrameSchema(columns={'OIL_CUM': <Schema Column(name=OIL_CUM, 
type=DataType(float64))>, 'WATER_CUM': <Schema Column(name=WATER_CUM, 
type=DataType(float64))>, 'GAS_CUM': <Schema Column(name=GAS_CUM, 
type=DataType(float64))>, 'LIQ_CUM': <Schema Column(name=LIQ_CUM, 
type=DataType(float64))>}, checks=[], parsers=[], index=None, dtype=None, 
coerce=False, strict=filter, name=None, ordered=False, unique=None, 
report_duplicates=all, unique_column_names=False, add_missing_columns=False, 
title=None, description=None, metadata=None, drop_invalid_rows=False)>, 
freq='MS', use_pressure=False, data=                 
TART_DATETIME    OIL_CUM  WATER_CUM   GAS_CUM    LIQ_CUM
2008-08-01       3522.00    3466.00   3522.00    6988.00
2008-09-01       4236.00    6105.00   4236.00   10341.00
2008-10-01       6735.00    7254.00   6735.00   13989.00
2008-11-01      11120.00    9280.00  11120.00   20400.00
2008-12-01      15494.00   12474.00  15494.00   27968.00
2009-01-01      20227.62   14561.16  20227.62   34788.78
2009-02-01      24276.04   16492.68  24276.04   40768.72
2009-03-01      29507.07   19851.19  29507.07   49358.26
...                  ...        ...       ...        ...
2012-04-01      78197.82   25030.04  78197.82  103227.86
2012-05-01      80597.52   25367.31  80597.52  105964.83
2012-06-01      82532.12   25646.75  82532.12  108178.87
2012-07-01      84191.72   25895.33  84191.72  110087.05
2012-08-01      84901.52   26000.87  84901.52  110902.39
2012-09-01      84992.50   26305.73  84992.50  111298.23), 
press_data=PressVector(is_result=False, data_schema=<Schema 
DataFrameSchema(columns={'PRESSURE_DATUM': 
<Schema Column(name=PRESSURE_DATUM, type=DataType(float64))>}, 
checks=[], parsers=[], index=None, dtype=None, coerce=False, strict=filter, 
name=None, ordered=False, unique=None, report_duplicates=all, 
unique_column_names=False, add_missing_columns=False, title=None, 
description=None, metadata=None, drop_invalid_rows=False)>, freq=None, 
use_pressure=False, data=                
START_DATETIME  PRESSURE_DATUM              
2008-07-29          884.696858
2008-07-31          884.696858))]
```