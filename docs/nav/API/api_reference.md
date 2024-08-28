# **Pytank Methods**

## **Main Methods**

- `Well` - Create a *well* object.
- `Oil_Model` - Create an *oil-fluid* model based on PVT data.
- `Water_Model` - Create a *water-fluid* model based on formation data.
- `Tank` - Create a *Tank* object to perform the desired analysis.
- `Analysis` - It allows to perform the respective *analysis* to determine the
  POIS.

### **Description of each method and its functions**

| Main Method                                 | Functions                                                              | Description                                                                                                                                                                     |
|---------------------------------------------|------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **[Well](generated/well_api.md)**           | `no methods`                                                           | -                                                                                                                                                                               |
| **[Oil_Model](generated/oil_model.md)**     | `get_bg_at_press(p)`                                                   | Method to interpolate gas volumetric factor (Bg).                                                                                                                               |
|                                             | `get_bo_at_press(p)`                                                   | Method to interpolate oil volumetric factor (Bo).                                                                                                                               |
|                                             | `get_rs_at_press(p)`                                                   | Method to interpolate oil solubility (Rs).                                                                                                                                      |
| **[Water_Model](generated/water_model.md)** | `get_bw_at_press(p)`                                                   | Method to calculate the water volumetric factor Bw using correlation.                                                                                                           |
|                                             | `get_default_bw()`                                                     | Static method to calculate the Bw value per default.                                                                                                                            |
|                                             | `get_rs_at_press(p)`                                                   | Method to calculate the water solubility RS using correlation                                                                                                                   |
|                                             | `get_default_rs()`                                                     | Static method to calculate the RS value per default.                                                                                                                            |
| **[Tank](generated/tank_api.md)**           | `get_pressure_df(p)`                                                   | Gets a DatFrame with pressure data.                                                                                                                                             |
|                                             | `get_prodcution_df(p)`                                                 | Gets a DatFrame with production data.                                                                                                                                           |
| **[Analysis](generated/analysis_api.md)**   | `analytic_method(poes, option)`                                        | Method used to calculate the POES through an inferred POES that ensures that there is the best match between the behavior of the observed pressure and the calculated pressure. |
|                                             | `campbell_data()`                                                      | Method to give the Campbell data.                                                                                                                                               |
|                                             | `campbell_plot(custom_line=False, x1=None, y1=None, x2=None, y2=None)` | Method to graphic the Campbell graph and see the energy contribution of the aquifer.                                                                                            |
|                                             | `havlena_oded_data()`                                                  | Calculate values based on Havlena and Odeh Methods.                                                                                                                             |
|                                             | `havlena_oded_plot()`                                                  | Calculate results based on Havlena and Odeh Methods and show a graphic.                                                                                                         |
|                                             | `mat_bal_df()`                                                         | Obtains the material balance parameters at a certain frequency.                                                                                                                 |
|                                             | `plot_cum_prod_time()`                                                 | Graph of Oil and Water Cumulative Production vs Time.                                                                                                                           |
|                                             | `plot_cum_prod_tot_time()`                                             | Graph of Total Liquid Cumulative Production vs Time.                                                                                                                            |
|                                             | `plot_cum_prod_well()`                                                 | Graph of Cumulative Production per Well of Tank.                                                                                                                                |
|                                             | `plot_flow_rate_tank`                                                  | Graph of Flow Rate vs Time by Tank..                                                                                                                                            |
|                                             | `plot_flow_rate_well`                                                  | Graph of Flow Rate vs Time per Rate of Tank.                                                                                                                                    |
|                                             | `plot_press_avg_liq_cum`                                               | Graph of Average Pressure vs Cumulative Liquids (Oil and Water).                                                                                                                |
|                                             | `plot_press_avg_time`                                                  | Graph of Average Pressure vs Time.                                                                                                                                              |
|                                             | `plot_press_liq_cum`                                                   | Graph of Pressure vs Cumulative Liquids (Oil and Water).                                                                                                                        |
|                                             | `plot_press_time`                                                      | Graph of normal Pressure vs Time.                                                                                                                                               |

## **Secondary Methods**

- `Helpers` - Offers the user a quick way for **well** creation.
- `Vector` - Defines the VectorData Class for handling vector.

### **Description of each method and its functions**

| Secondary Method                        | Functions                                                          | Description                                                                   |
|-----------------------------------------|--------------------------------------------------------------------|-------------------------------------------------------------------------------|
| **[Helpers](generated/helpers.md)**     | `create_wells(df_prod, df_press, freq_prod=None, freq_press=None)` | Returns A list of Wells objects.                                              |
|                                         | `search_wells(wells, well_names)`                                  | Searches for wells in the list of all wells based on the provided well names. |
| **[Vectors](generated/vector_data.md)** | `InjVector`                                                        | This class is used to handle injection data with a specific scheme.           |
|                                         | `PressVector`                                                      | This class is used to handle pressure data with a specific scheme.            |
|                                         | `ProdVector`                                                       | This class is used to handle production data with a specific scheme.          |

## **Additional Functions**

- **[PVT Correlations](generated/pvt_correlations.md)**
- **[Material Balance](generated/mb_api.md)**
- **[Utilities](generated/utilities.md)**


