"""from fluid import FullFluidModel, OilFluidModel
import pandas as pd
from get_wells import tank_wells

#%% Read fluid data
df_pvt = pd.read_csv("data/pvt.csv")
black_oil = OilFluidModel(
    data_pvt=df_pvt
)
brine_model = WaterFluidModel(
    salinity=30000.0,
    correlations="Spivey"
)

# create full fluid for tank
full_fluid = FullFluidModel(
    oil=black_oil,
    water=brine_model
)

# Create tanks with fluids and well data
tank_center = Tank(wells=[well_1, well_2], fluid=full_fluid)

tank_center.plot_avg_pressure(freq="6MS")
tank_center.initialize_mbal_with_data(freq="6MS", stoiip, porosity, swi, bsw, fluid_density, fluid_compressibility, fluid_viscosity)

tank_center.plot_campbell_plot()"""