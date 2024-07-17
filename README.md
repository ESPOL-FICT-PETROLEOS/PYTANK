<div align="center">
  <!-- <img src="https://github.com/reservoirpy/reservoirpy/raw/master/static/rpy_banner_bw.png"><br> !-->
  <img src="./static/logo.png"><br>
</div>

# Pytank (v0.1.3) 

**A tool for estimating the original volume of oil in reserves by using an object-oriented programming approach (POO).**

```python
from pytank.fluid_model import OilModel, WaterModel
from pytank.tank import Tank
from pytank.analysis import Analysis
from pytank.aquifer_model import Fetkovich, CarterTracy
from pytank.functions.helpers import create_wells, search_wells

"-------------------------- Well Module----------------------------"
wells = create_wells(df_prod,
                     df_press,
                     freq_prod,
                     freq_press)

# List of all wells

# List of wells for user selection
my_wells = [
    "A-1-P", "A-10-P", "A-11-P", "A-12-P", "A-13-P", "A-14-P", "A-16-P",
    "A-17-P", "A-18-P", "A-19-P", "A-21-P", "A-22-P", "A-23-P", "A-24-I",
    "A-4-P", "A-5-P", "A-6-P", "A-8-P", "A-9-P"
]

# lis of wells with the pressure and production info for user selection
wells_info = search_wells(wells,
                          my_wells)

"----------------------- Fluid Models Module -----------------------"

oil_model = OilModel(
 data_pvt,
 temperature)

water_model = WaterModel(salinity,
                         temperature,
                         unit)

"---------------------------- Tank Module ---------------------------"
tank1 = Tank(name,
            wells,
            oil_model,
            water_modell,
            pi,
            swo,
            cw,
            cf,
            aquifer)

"-------------------------- Analysis Module ------------------------"
frequency = "12M"
analysis = Analysis(tank_class=tank1,
                    freq=frequency,
                    position="end",
                    smooth=True)

"--- P vs T ---"
plt5 = analysis.plot_press_avg_liq_cum()
plt5.show()

plt = analysis.plot_press_avg_time()
plt.show()

# %%
"Campbell"
# Plot without points selected
camp = analysis.campbell_plot(custom_line=False)
camp.show()

#%%
# Plot with points selected
camp_custom = analysis.campbell_plot(
    custom_line=False,
    x1,
    y1,
    x2,
    y2,
)
camp_custom.show()
# %%
"Havlena"
# Plot without points selected
havlena_plot = analysis.havlena_odeh_plot()
havlena_plot.show()

#%%
# Plot with points selected
havlena_custom = analysis.havlena_odeh_plot(
    custom_line=False,
    x1,
    y1,
    x2,
    y2
)
havlena_custom.show()
#

"-------------------------- Aquifer Models --------------------------"
"----- With Aquifer - Fetkovich ------"

fet = Fetkovich(
    aq_radius,
    res_radius,
    aq_thickness,
    aq_por,
    ct,
    theta,
    k,
    water_visc,
)

tank_fet = Tank(name,
                wells,
                oil_model,
                water_model,
                pi,
                swo,
                cw,
                cf,
                aquifer)

analysis_fet = Analysis(tank_class,
                        freq,
                        position,
                        smooth=True)

"Analytic method"
analytic_meth_fet = analysis_fet.analytic_method(poes=67e+6, 
                                                 option="plot")
analytic_meth_fet.show()

"Havlena Method"
# Without points selectec
havlena_fet = analysis_fet.havlena_odeh_plot(
    custom_line=False,
)
havlena_fet.show()

# With points selected
havlena_fet_custom = analysis_fet.havlena_odeh_plot(
    custom_line=False,
    x1,
    y1,
    x2,
    y2,
)
havlena_fet_custom.show()

```
**PyTank** is a library that implements different scientific 
scientific modules based on the Object Oriented Programming (OOP) 
object oriented programming (OOP), in order to calculate the original
the purpose of calculating the original volume of oil reserves.
of oil reserves.

It is designed in such a way that it allows the user to
to develop an analysis using as main principle the material balance
the material balance, using the Havlena Odeh graphical method.
Havlena Odeh graphical method.

Among the different modules we have:
-**Wells**: Allows the creation of objects (Wells), in order to
 to perform the analysis at tank level.
-**Tank**: Allows the grouping of production data, pressure,
 and relevant pvt data of the wells to be analyzed. 
 you want to analyze.
-**OilModel**: Allows to set up an oil model based on a PVT data given by
 based on a PVT data given by the user.
-**WaterModel**: Allows to set a water model under
 pressure, temperature and salinity parameters.
-**Aquifer**: Allows to set up a model to determine the reservoir contribution in case of
 reservoir contribution in case it exists or not. The
 user can determine if it is necessary or not to define it.
-**Analysis**: Allows to establish an analysis in a graphical way to determine the POES
 to determine the POES, determine the existence of an aquifer graphically 
 the existence of an aquifer in a graphical way using Campbell's theory,
 allows to calculate the POES in an analytical way by varying the
 parameters that have influence in the analysis, in addition to the
 has different functions that allow the user to perform an exploratory
 to perform an exploratory analysis of the data entered,
 and to have an idea of the behavior of the tank.

This library works for **Python 3.10** and higher.