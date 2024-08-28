# **Why should we define an aquifer model?**

Defining an aquifer model is fundamental to estimating reservoir reserves for several
key reasons:

## **Understanding Hydraulic Behavior**

### Aquifer Dynamics

Aquifers act as sources of pressure that can influence hydrocarbon production. A
well-defined model allows understanding how the aquifer responds to resource extraction,
which is crucial for predicting changes in pressure and water flow.

### Reservoir-Aquifer Interaction

The interaction between the aquifer and the reservoir can be complex. A model allows
simulating different production scenarios and assessing how aquifer pressure affects
hydrocarbon recovery. This is especially relevant in reservoirs that rely on the aquifer
to maintain pressure.

## **Accurate Reservoir Estimation**

### Estimating Recoverable Resources

Aquifer models, such as those of Fetkovich and Carter-Tracy, allow the calculation of
cumulative water influx, which is essential to determine how much of the resource is
recoverable. These models consider factors such as porosity, permeability and
compressibility of the aquifer, resulting in more accurate estimates of reserves.

### Recovery Efficiency Evaluation

Models help evaluate the recovery efficiency of the reservoir, allowing production
strategies to be adjusted. With a better understanding of the aquifer, enhanced recovery
techniques can be implemented to optimize hydrocarbon extraction.

## **Aquifer Models**

### **Fetkovich**

The Fetkovich model is designed to predict the behavior of water influx into a reservoir
over time, particularly in cases where an aquifer is present. It is based on the concept
of productivity and the pressure differential between the aquifer and the reservoir.

$$W = J \cdot (P_a - P_r)$$

*Parameters*:

- W: Cumulative water influx (volume).
- J: Productivity of the aquifer (flow rate per unit pressure).
- Pa: Pressure in the aquifer.
- Pr: Pressure in the reservoir.

#### Considerations

- **Cumulative Water Influx**: The model is designed to calculate the cumulative water
  influx from an aquifer into a reservoir, which is essential for understanding
  reservoir performance and managing hydrocarbon production.
- **Productivity Index**: The model employs the concept of productivity to describe the
  relationship between pressure differentials and the rate of water influx. This helps
  in predicting how effectively the aquifer can support the reservoir.
- **Steady-State Assumption**: The Fetkovich model is often applied under steady-state
  conditions, where the influx of water remains relatively stable over time, simplifying
  the analysis.

#### Limitations

- **Homogeneity Assumption**: The model assumes that both the aquifer and the reservoir
  are
  homogeneous. In reality, geological variations can lead to significant differences in
  rock properties, affecting flow behavior.
- **Pressure Differential Dependence**: The model's effectiveness relies heavily on the
  pressure differential between the aquifer and the reservoir. If this differential is
  small, the model may underestimate the influx of water.
- **Transient Conditions**: The Fetkovich model is primarily applicable in steady-state
  scenarios. During transient conditions, such as the initial production phase, the flow
  behavior may be more complex and not accurately captured by the model.
- **Geometric Simplifications**: The model typically assumes simple geometries for the
  aquifer and reservoir. Complex geological settings may require more sophisticated
  modeling techniques.
- **Limited Applicability**: While the model is useful for reservoirs with strong
  aquifer
  support, it may not be applicable in scenarios where the aquifer is limited or absent.

### **Carter-Tracy Model**

The model is based on the premise that the flow of water from an aquifer into an oil
reservoir can be described using equations of flow in porous media. It focuses on the
relationship between reservoir pressure and the rate of water influx, considering the
aquifer as a source of pressure.

The Carter-Tracy model utilizes the radial flow equation for aquifers, commonly
expressed in terms of the water influx rate `qw` and the pressure in the reservoir `P`

$$q_w = \frac{2 \pi k}{\mu} (P_a - P)$$

*Parameters*:

- qw: Water influx rate (volume per time).
- k: Permeability of the aquifer.
- u: Viscosity of water.
- Pa: Pressure of the aquifer.
- p: Pressure in the reservoir.

### Considerations

- **Constant Influx Rate**: The model assumes a constant rate of water intrusion during
  specified time intervals. This simplification helps in making calculations more
  manageable but may not reflect real-world conditions accurately.
- **Homogeneous Aquifer**: The model presumes that the aquifer is homogeneous, meaning
  that
  its properties (like permeability and porosity) are consistent throughout. This
  assumption is critical for the model's validity.
- **Steady-State Conditions**: The Carter-Tracy model is primarily applicable under
  steady-state conditions, where the influx of water remains relatively stable over
  time.

### Limitations

- **Transient Conditions**: The model may not accurately predict water influx during
  transient conditions, such as the initial production phase when pressures are changing
  rapidly.
- **Geological Variability**: Real-world aquifers and reservoirs often exhibit
  geological
  variability, including heterogeneities in rock properties, which can significantly
  impact flow behavior. The model's assumptions may not hold true in such cases.
- **Simplified Geometry**: The model typically assumes simple geometries for the aquifer
  and
  reservoir, which may not be the case in complex geological settings.
- **Pressure Differential**: The effectiveness of the model relies heavily on the
  pressure
  differential between the aquifer and the reservoir. If this differential is small, the
  model may underestimate the influx.
- **Limited Applicability**: The model is best suited for specific types of reservoirs,
  particularly those with strong aquifer support. It may not be applicable for all
  reservoir scenarios, especially those with limited or no aquifer
  influence.

## **Let's create an aquifer model**

Before defining an aquifer model for either Fetkovich or Carter Tracy, it is first
necessary to know what parameters we need, I recommend you to visit the documentation of
the [aquifer reference](../API/generated/aquifer_api.md) functions. If you think you
have everything you need, we can get started.

### 1. Create an Instance of the Aquifer Model

For this case we will take as an example how to create a fetkovich aquifer model. Once
we have identified the parameters of which we require information, we proceed to fill in
the function, in an order, or also defining its parameters and its value.

*Example*

```
aquifer_model = Fetkovich(
    aq_radius=1000,      # Aquifer radius in feet
    res_radius=500,      # Reservoir radius in feet
    aq_thickness=50,     # Aquifer thickness in feet
    aq_por=0.25,         # Aquifer porosity
    ct=1e-5,             # Total compressibility
    theta=30,            # Aquifer angle in degrees
    k=100,               # Permeability in millidarcy
    water_visc=1,        # Water viscosity in centipoise
    boundary_type="no_flow",
    flow_type="radial",
    pr=[3000, 2900, 2800],  # List of reservoir pressures in psi
    time_step=[0, 30, 60]    # List of time steps in days
)
```

### 2. Calculate and Retrieve Results

Once we have finished defining the value of the parameters for our aquifer model, we can
call the function `get_we()`, which returns a matrix with the values of the inflow at a
given time differential.

```
cumulative_influx = aquifer_model.get_we()
print(cumulative_influx)
```