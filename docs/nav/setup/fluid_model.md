# **PVT Properties**

PVT (Pressure, Volume and Temperature) properties are fundamental in reservoir
engineering, as they determine the behavior of fluids in a reservoir. These
properties are obtained through various techniques, including laboratory
analysis, empirical correlations and interpolation. The following is a
description of how these properties and model fluids are obtained for water and
oil.

## **Obtaining PVT Properties**

### 1. PVT Analysis

PVT analysis is a set of experimental tests that simulate the behavior of fluids
in the reservoir under different pressure and temperature conditions. This
analysis includes:

- ``Separation tests``: determine how the fluids behave when separating under
  laboratory conditions, replicating the situation in the reservoir.
- ``Differential release tests``: Measure how the gas is released from the fluid
  as the pressure decreases.
- ``Composition tests``: Analyze the composition of fluids to understand their
  physical and chemical properties.

### 2. Empirical Correlations

Various empirical correlations have been developed over the years to estimate
PVT properties based on field data. These correlations can be simple or
complex and are used to estimate properties such as:

- **Bubble pressure**
- **Gas-Oil Ratio (GOR)**
- **Volumetric factors (Bo and Bg)**
- **Viscosity and compressibility**
- **Viscosity and compressibility**

It is important to note that the use of correlations should be done with
caution, as they may not be applicable to all reservoir conditions and may
introduce errors if fluid characteristics are not properly considered.

### 3. Interpolation

Interpolation is used to estimate PVT property values at pressures that were
not directly measured in the laboratory. This is done by means of
interpolation functions that allow intermediate values to be calculated based
on the data obtained from PVT tests. For example, the volumetric oil factor (
Bo) or gas solubility (Rs) at a specific pressure can be interpolated using
pressure data and the corresponding properties.

## **Model Fluids for Water and Oil**

### Oil Model

The oil model is based on PVT properties obtained through laboratory analysis.
Key parameters include:

- ``Bo (Oil Volumetric Factor)``: relates the volume of oil in the reservoir to
  the volume at surface conditions.
- ``Bg (Gas Volumetric Factor)``: Relates the volume of gas in the reservoir to
  the volume at surface conditions.
- ``GOR (Gas-Oil Ratio)``: Ratio of dissolved gas to oil. These parameters are
  essential for the design of production systems and for reserves estimation.

### Water Model

The water model focuses on properties such as:

- ``Bw (Volumetric Water Factor)``: relates the volume of water in the reservoir
  to the volume at surface conditions.
- ``Salinity``: Affects the density and viscosity of water, which in turn
  influences the behavior of the fluid in the reservoir.

Water properties are often calculated using correlations based on salinity,
temperature and pressure.

## **Pytank Fluid Models**

Pytank has two Classes: *OilModel*, *WaterModel*, which will allow you to
develop a
model so that you can perform the respective analysis of your data.

### **OilModel**

The OilModel class focuses on the PVT properties of oil, through interpolations
made with the interpolated (linear interpolation) module of the Python scipy
library from a given pressure. It uses a DataFrame containing validated PVT
data, which may include properties such as:

- ``Bo (Volumetric Oil Factor)``: This factor is crucial for converting oil
  volumes at reservoir conditions to surface conditions. The OilModel class
  allows users to interpolate the Bo value at different pressures using the
  get_bo_at_press() method. This is critical for production planning and reserve
  estimation.
- ``Bg (Volumetric Gas Factor) and GOR (Gas-Oil Ratio)``: The class also allows
  interpolation of these properties, which helps users understand how the gas
  dissolved in the oil will behave under different pressure conditions.

Using the OilModel class allows users to easily access PVT properties of the
oil, perform calculations needed for production planning and optimize
hydrocarbon recovery. For example, an engineer could create an instance of
OilModel with PVT data obtained from laboratory tests and then use interpolation
methods to estimate properties at specific pressures, facilitating informed
decision-making.

For more information on the OilModel class you can review its
[documentation](../API/generated/oil_model.md).

### **WaterModel**

The WaterModel class focuses on obtaining the PVT properties of water by using
[PVT correlations](../API/generated/pvt_correlations.md). The key properties it
handles include:

- ``Bw (Volumetric Water Factor)``: this factor is essential to understand how
  water behaves in the reservoir and how it affects oil production. The
  WaterModel class allows calculating Bw at different pressures through the
  get_bw_at_press() method, using correlations based on salinity and
  temperature.
- ``Salinity``: The salinity of water influences its density and viscosity,
  which in turn affects the behavior of the fluid in the reservoir. The class
  allows users to specify salinity and obtain related properties, which is
  crucial for water production modeling.

The WaterModel class provides users with a tool to calculate and analyze water
properties in the reservoir, allowing a better understanding of how water
interacts with oil and how it can be managed in the production process.

For more information on the WaterModel class you can review its
[documentation](../API/generated/water_model.md).

### **Example of Use**

A user working in reservoir engineering can use the OilModel and WaterModel
classes as follows:

#### 1. Model Creation:

- PVT data is collected through laboratory testing and organized in a
  DataFrame (df_pvt).
- An instance of OilModel is created by passing the PVT DataFrame and the
  reservoir temperature.
- A WaterModel instance is created by specifying salinity, temperature and unit
  of measure.

```
oil_model = OilModel(data_pvt=df_pvt, temperature=25)
water_model = WaterModel(salinity=3000, temperature=200, unit=1)
```

#### 2. Property interpolation:

- The engineer can use OilModel's interpolation methods to obtain the volumetric
  oil factor (Bo) at different pressures, allowing him to adjust his production
  calculations according to reservoir conditions.

```
bo_value = oil_model.get_bo_at_press(3000)  # Bo interpolation at 3000 psi
```

- Similarly, you can use WaterModel to calculate the volumetric water factor (
  Bw) at the same pressure, ensuring that all aspects of production are properly
  considered.

```
bw_value = water_model.get_bw_at_press(3000)  # Calculation of Bw at 3000 psi
```