# **Tank in Pytank**

A tank is a system that stores and manages fluids in a reservoir. In reservoir
engineering, the tank can be considered as a model that represents the reservoir
properties, including pressure, temperature, and the characteristics of the
fluids present. Tanks are used to perform simulations and analyses to understand
reservoir behavior under different operating conditions.

## **Importance in Matter Balance Analysis**

The material balance is a fundamental principle in reservoir engineering that is
used to analyze the amount of fluids entering and leaving a system. The
importance of a tank in this analysis lies in several aspects:

- **Data Storage**: A tank allows storing crucial data on reservoir properties,
  such as fluid pressure, volume and temperature. This is essential for
  calculating reservoir behavior over time.

- **Calculation of PVT Properties**: PVT (Pressure, Volume and Temperature)
  properties are fundamental to understand how fluids behave in the reservoir.
  These properties vary with pressure and temperature, and a tank provides a
  framework for calculating and analyzing these properties at different
  conditions. For example, oil volumetric factor (Bo) and gas volumetric
  factor (Bg) are essential for estimating reservoir production and reserves.
- **Production Simulation**: Tanks allow different production scenarios to be
  simulated, which helps engineers predict how fluids will behave under various
  operating conditions. This is crucial for production planning and hydrocarbon
  recovery optimization.
- **Reservoir Evaluation**: The information stored in a tank is used to evaluate
  the reserves of a reservoir. This includes estimating the original volume of
  oil in the reservoir and determining the production rate over time.
- **Resource Management**: A tank also aids in the management of oil and water
  resources, allowing engineers to make informed decisions about the
  exploitation and management of fluids in the reservoir.

## **Class Tank**

This class is the main link with the other classes that Pytank has and on which
depends how the Analysis that calculates the OOIP is performed. Tank acts as a
container to store critical data about the reservoir, including its PVT
properties through the OilModel and WaterModel instances.

The class includes methods that allow obtaining DataFrames with the PVT
properties of the fluids in the reservoir. This facilitates the evaluation of
how these properties change under different pressure conditions, which is
fundamental for material balance analysis.

The Tank class allows simulating different production scenarios by integrating
data from multiple wells. This helps predict reservoir behavior under various
operating conditions, which is crucial for production planning and hydrocarbon
recovery optimization.

For more information on the Tank class you can review its
[documentation](../API/generated/tank_api.md).

## **Let´s Create a Tank**

In the first instance you must have created your `wells` to be able to perform
the analysis as required, in case you do not have them created, you can go to
[How to create a well?](well.md),also you must have developed the
respective fluid models for water and oil, in case you have not, take a look at
[Which fluid models do I need?](fluid_model.md).

### 1. Creating a Tank

- The engineer collects data on wells, PVT properties of oil and water, and
  other reservoir parameters.
- An instance of the Tank class is created, providing all the necessary data.

```
tank = Tank(
    name=“Reservoir_A”,
    wells=[well1, well2], # List of instances of class Well
    oil_model=oil_model, # Instance of OilModel
    water_model=water_model, # Instance of WaterModel
    pi=3000, # Initial pressure in psi
    swo=0.2, # Initial water saturation
    cw=0.0001, # Water compressibility
    cf=0.0005 # Total compressibility
)
```

### 2. Obtaining Pressure Data

-The engineer can obtain a DataFrame with the PVT properties of the fluids in
the tank using the get_pressure_df() method. This will allow him to analyze how
the properties vary at different pressures.

```
tank_press = tank.get_pressure_df().head()
```

```
   PRESSURE_DATUM WELL_BORE START_DATETIME        Bo  Bg   GOR        Bw        RS_bw    Tank  
0      884.696858    well1     2008-07-29  1.138542 NaN  89.0  1.038348   606.566799  Zone_B
1      884.696858    well1     2008-07-31  1.138542 NaN  89.0  1.038348   606.566799  Zone_B
2     2443.800580    well1     1995-08-09  1.126459 NaN  89.0  1.035423  1352.168228  Zone_B 
3      876.389229    well1     2006-12-23  1.138591 NaN  89.0  1.038361   601.632019  Zone_B
4     2193.242118    well2     2002-11-06  1.128232 NaN  89.0  1.035934  1250.620330  Zone_B 
5     2042.342826    well2     2002-12-03  1.129300 NaN  89.0  1.036236  1186.791953  Zone_B 
6     2316.404940    well2     2002-05-25  1.127360 NaN  89.0  1.035684  1301.197973  Zone_B 
7     1214.652407    well2     2010-12-05  1.135892 NaN  89.0  1.037794   791.889827  Zone_B 
8      926.493133    well2     2011-01-07  1.138274 NaN  89.0  1.038281   631.177797  Zone_B

```

### 3. Obtaining Production Data

Similarly, the engineer can obtain a DataFrame with the cumulative production
data using the get_production_df() method, which will allow him/her to perform a
material balance analysis

```
tank_prod = tank.get_production_df().head()
```

```
   OIL_CUM  WATER_CUM  GAS_CUM  LIQ_CUM WELL_BORE START_DATETIME    Tank
0   3522.0     3466.0   3522.0   6988.0    well1     2008-08-01  Zone_B
1   4236.0     6105.0   4236.0  10341.0    well1     2008-09-01  Zone_B
2   6735.0     7254.0   6735.0  13989.0    well1     2008-10-01  Zone_B
3  11120.0     9280.0  11120.0  20400.0    well2     2008-11-01  Zone_B
4  15494.0    12474.0  15494.0  27968.0    well2     2008-12-01  Zone_B
```