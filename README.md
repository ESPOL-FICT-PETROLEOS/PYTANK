<div align="center">
  <!-- <img src="https://github.com/reservoirpy/reservoirpy/raw/master/static/rpy_banner_bw.png"><br> !-->
  <img src="./static/PyTank_Logo.jpg"><br>
</div>

# PyTank (v0.1.1) ??

**A tool for estimating the original volume of oil in reserves, using an object-oriented programming approach (POO).**

```python
from pytank.fluid_model.fluid import OilModel, WaterModel
from pytank.tank.tank import Tank
from pytank.well.well import Wells
from pytank.analysis.analysis import Analysis
from pytank.aquifer.aquifer_model import Fetkovich, CarterTracy

wells = Wells(df_prod,
              df_press,
              freq_prod,
              freq_press)

oil_model = OilModel(
    data_pvt,
    temperature)

water_model = WaterModel(salinity,
                         temperature,
                         unit)

tank = Tank(name,
             wells,
             oil_model,
             water_modell,
             pi,
             swo,
             cw,
             cf,
             aquifer)
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