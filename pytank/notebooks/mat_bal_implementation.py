"""from pytank.fluid_model.fluid import OilModel, WaterModel
import pandas as pd
from pytank.functions.pvt_correlations import RS_bw

#%% Read fluid data
df_pvt = pd.read_csv("data/pvt.csv")
black_oil = OilModel(
    data_pvt=df_pvt
)
brine_model = WaterModel(
    salinity=30000.0,
    correlations=RS_bw
)

# create full fluid for tank


# Create tanks with fluids and well data
tank_center = Tank(wells=[well_1, well_2], fluid=full_fluid)

tank_center.plot_avg_pressure(freq="6MS")
tank_center.initialize_mbal_with_data(freq="6MS", stoiip, porosity, swi, bsw, fluid_density, fluid_compressibility, fluid_viscosity)

tank_center.plot_campbell_plot()"""