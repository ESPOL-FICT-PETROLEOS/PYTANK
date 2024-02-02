from utilities import pvt_correlations as pvt
import pandas as pd
import numpy as np


def pvt_table1(p_sep, t_sep, api, rsp, sg_sep, tres, den_sto, p_res, salinity, jump,
              units=1) -> pd.DataFrame:

    """The pvt_table data frame is a table that has a size of the length of Pres(it
    is printed regarding a range) vs 6 columns, where within the first column are shown
    the pressure values (from 0 to Pres) whereas within each of the next 6 columns, are
    displayed 6 PVT properties such as the oil density, FVF_oil, GOR, rsw, FVF_water,
    and water compressibility evaluated at the values of P from 0 to the reservoir
    pressure. The required input data is: Separator pressure [psia], Separator
    Temperature [F], Stock tank oil gravity [API], Separator producing GOR [scf/STB],
    Separator gas Specific Gravity, Reservoir Temperature [F], Density of stock-tank oil
    [lb/cu ft], Reservoir Pressure [psia], water salinity, and Jump(it indicates the
    step size of the iteration over the pressure).It also requires the Pb from Velarde
    correlation, which is called within the function.

    Parameters
    ----------
    p_sep: int or float
        Separator pressure [psia]
    t_sep: int or float
        Separator temperature [F]
    api: int or float
        Stock tank oil gravity [API]
    rsp: int or float
        Separator producing GOR [scf/STB]
    sg_sep: int or float
        Separator gas specific gravity
    tres: int or float
        Reservoir temperature [F]
    den_sto: int or float
        Density of stock-tank oil [lb/cu ft]
    p_res: int or float
        Initial reservoir pressure [psia]
    salinity: int or float
        Water Salinity [ppm]
    jump: int or float
        step size of the iteration over the pressure
    units: unit system
        if units = 1, it will use field units. Otherwise, it will be used metric units

    Returns
    -------
    Pandas Dataframe:
        Returns a pandas Dataframe with some pvt properties
    """

    # Call the bubble point pressure function
    pb = pvt.Pb_Velarde(api, sg_sep, tres, p_sep, t_sep, rsp, units)

    # Naming the dataframe columns
    pressure = "pressure[psia]"
    gor = "gor[scf/stb]"
    density = "density[lb/cu ft]"
    oil_fvf = "oil_fvf[rb/stb]"
    rsw = "gas_water_Rs[scf/stb]"
    water_fvf = "water_fvf[rb/stb]"
    water_comp = "water_comp[1/psia]"

    # List containing the names of all columns
    columns = [pressure, gor, density, oil_fvf, rsw, water_fvf, water_comp]

    # Creation of empty dataframes; under, at, and above the bubble pressure point
    df_under = pd.DataFrame(columns=columns)
    df_pb = pd.DataFrame(columns=columns)
    df_above = pd.DataFrame(columns=columns)
    #creations of empty arrays
    array_under = []
    array_pb = []
    array_above = []

    # Loop to iterate from 0 to reservoir pressure
    for p in np.arange(0, p_res+1, jump):

        # Condition when pressure is less than the bubble point pressure
        if 0 < p < pb:

            gor_velarde2 = pvt.Solution_GOR_Velarde2(sg_sep, api, tres, p, p_sep, t_sep,
                                                     rsp, units)
            den_underpb = pvt.Den_underPb(sg_sep, tres, p, api, p_sep, t_sep, rsp,
                                          units)
            fvf_underpb = pvt.FVF_underPb(den_sto, p_sep, t_sep, api, rsp, sg_sep, tres,
                                          p, units)
            rsw_under = pvt.RS_bw(p, tres, salinity, units)
            water_fvf_under = pvt.Bo_bw(p, tres, salinity, units)
            water_comp_under = pvt.comp_bw_nogas(p, tres, salinity, units)
            p_under = p

            array_under.append([p_under, gor_velarde2, den_underpb, fvf_underpb, rsw_under, water_fvf_under, water_comp_under])

        # Condition when pressures is equal to the bubble point pressure
        elif p == pb:
            array_pb.append([p,
                             pvt.Solution_GOR_Pb_ValkoMcCain(p_sep, t_sep, api, rsp, units),
                             pvt.Den_Pb(sg_sep, tres, p_sep, t_sep, api, rsp, units),
                             pvt.FVF_Pb(den_sto, p_sep, t_sep, api, rsp, sg_sep, tres, units),
                             pvt.RS_bw(p, tres, salinity, units),
                             pvt.Bo_bw(p, tres, salinity, units),
                             pvt.comp_bw_nogas(p, tres, salinity, units)])

        # Condition when pressure is greater than the bubble point pressure
        elif pb < p <= p_res:

            den_abovepb = pvt.Den_abovePb(p, sg_sep, tres, p_sep, t_sep, api, rsp,
                                          p_res, units)
            gor_velarde2_above = pvt.Solution_GOR_Pb_ValkoMcCain(p_sep, t_sep, api, rsp,
                                                                 units)
            fvf_abovepb = pvt.FVF_abovePb(p, den_sto, p_sep, t_sep, api, rsp, sg_sep,
                                          tres, p_res, units)
            rsw_above = pvt.RS_bw(p, tres, salinity, units)
            water_fvf_above = pvt.Bo_bw(p, tres, salinity, units)
            water_comp_above = pvt.comp_bw_nogas(p, tres, salinity, units)
            p_above = p

            array_above.append([p_above, gor_velarde2_above, den_abovepb, fvf_abovepb, rsw_above, water_fvf_above, water_comp_above])

    # Concatenation of the pvt dataframes regarding their relationship to the bubble
    # Convert lists to numpy arrays
    array_under = np.array(array_under)
    array_pb = np.array(array_pb)
    array_above = np.array(array_above)

    #Create DataFrames
    df_above = pd.DataFrame(array_above)
    df_pb = pd.DataFrame(array_pb)
    df_under = pd.DataFrame(array_under)

    # Concatenate DataFrames
    pvt_dataframe = pd.concat([df_above, df_pb, df_under], ignore_index=False, axis=0)
    pvt_dataframe.columns = columns

    # Return the result
    return pvt_dataframe

def pvt_table2(p_sep, t_sep, api, rsp, sg_sep, tres, den_sto, p_res, salinity, jump,
              units=1) -> pd.DataFrame:

    """The pvt_table data frame is a table that has a size of the length of Pres(it
    is printed regarding a range) vs 6 columns, where within the first column are shown
    the pressure values (from 0 to Pres) whereas within each of the next 6 columns, are
    displayed 6 PVT properties such as the oil density, FVF_oil, GOR, rsw, FVF_water,
    and water compressibility evaluated at the values of P from 0 to the reservoir
    pressure. The required input data is: Separator pressure [psia], Separator
    Temperature [F], Stock tank oil gravity [API], Separator producing GOR [scf/STB],
    Separator gas Specific Gravity, Reservoir Temperature [F], Density of stock-tank oil
    [lb/cu ft], Reservoir Pressure [psia], water salinity, and Jump(it indicates the
    step size of the iteration over the pressure).It also requires the Pb from Velarde
    correlation, which is called within the function.

    Parameters
    ----------
    p_sep: int or float
        Separator pressure [psia]
    t_sep: int or float
        Separator temperature [F]
    api: int or float
        Stock tank oil gravity [API]
    rsp: int or float
        Separator producing GOR [scf/STB]
    sg_sep: int or float
        Separator gas specific gravity
    tres: int or float
        Reservoir temperature [F]
    den_sto: int or float
        Density of stock-tank oil [lb/cu ft]
    p_res: int or float
        Initial reservoir pressure [psia]
    salinity: int or float
        Water Salinity [ppm]
    jump: int or float
        step size of the iteration over the pressure
    units: unit system
        if units = 1, it will use field units. Otherwise, it will be used metric units

    Returns
    -------
    Pandas Dataframe:
        Returns a pandas Dataframe with some pvt properties
    """

    # Call the bubble point pressure function
    pb = pvt.Pb_Velarde(api, sg_sep, tres, p_sep, t_sep, rsp, units)

    # Naming the dataframe columns
    pressure = "pressure[psia]"
    gor = "gor[scf/stb]"
    density = "density[lb/cu ft]"
    oil_fvf = "oil_fvf[rb/stb]"
    rsw = "gas_water_Rs[scf/stb]"
    water_fvf = "water_fvf[rb/stb]"
    water_comp = "water_comp[1/psia]"

    # List containing the names of all columns
    columns = [pressure, gor, density, oil_fvf, rsw, water_fvf, water_comp]

    # Creation of empty dataframes; under, at, and above the bubble pressure point
    df_under = pd.DataFrame(columns=columns)
    df_pb = pd.DataFrame(columns=columns)
    df_above = pd.DataFrame(columns=columns)

    #Creation of empty list, under, at, and above the bubble pressure point
    data_under = []
    data_pb = []
    data_above = []

    # Loop to iterate from 0 to reservoir pressure
    for p in np.arange(0, p_res+1, jump):

        # Condition when pressure is less than the bubble point pressure
        if (p > 0) and (p < pb):

            gor_velarde2 = pvt.Solution_GOR_Velarde2(sg_sep, api, tres, p, p_sep, t_sep,
                                                     rsp, units)
            den_underpb = pvt.Den_underPb(sg_sep, tres, p, api, p_sep, t_sep, rsp,
                                          units)
            fvf_underpb = pvt.FVF_underPb(den_sto, p_sep, t_sep, api, rsp, sg_sep, tres,
                                          p, units)
            rsw_under = pvt.RS_bw(p, tres, salinity, units)
            water_fvf_under = pvt.Bo_bw(p, tres, salinity, units)
            water_comp_under = pvt.comp_bw_nogas(p, tres, salinity, units)
            p_under = p

            data_under.append([p_under, gor_velarde2, den_underpb, fvf_underpb, rsw_under, water_fvf_under,
                               water_comp_under])


        # Condition when pressures is equal to the bubble point pressure
        elif p == pb:
            data_pb.append([p, pvt.Solution_GOR_Pb_ValkoMcCain(p_sep, t_sep, api, rsp, units),
                            pvt.Den_Pb(sg_sep, tres, p_sep, t_sep, api, rsp, units),
                            pvt.FVF_Pb(den_sto, p_sep, t_sep, api, rsp, sg_sep, tres, units),
                            pvt.RS_bw(p, tres, salinity, units), pvt.Bo_bw(p, tres, salinity, units),
                            pvt.comp_bw_nogas(p, tres, salinity, units)])

        # Condition when pressure is greater than the bubble point pressure
        elif (p > pb) and (p <= p_res):

            den_abovepb = pvt.Den_abovePb(p, sg_sep, tres, p_sep, t_sep, api, rsp,
                                          p_res, units)
            gor_velarde2_above = pvt.Solution_GOR_Pb_ValkoMcCain(p_sep, t_sep, api, rsp,
                                                                 units)
            fvf_abovepb = pvt.FVF_abovePb(p, den_sto, p_sep, t_sep, api, rsp, sg_sep,
                                          tres, p_res, units)
            rsw_above = pvt.RS_bw(p, tres, salinity, units)
            water_fvf_above = pvt.Bo_bw(p, tres, salinity, units)
            water_comp_above = pvt.comp_bw_nogas(p, tres, salinity, units)
            p_above = p

            data_above.append(
                [p_above, gor_velarde2_above, den_abovepb, fvf_abovepb, rsw_above, water_fvf_above, water_comp_above])
    #Empty dataframes
    df_under = pd.DataFrame(data_under, columns=columns)
    df_pb = pd.DataFrame(data_pb, columns=columns)
    df_above = pd.DataFrame(data_above, columns=columns)


    # Concatenation of the pvt dataframes regarding their relationship to the bubble
    # point pressure
    pvt_dataframe = pd.concat([df_under, df_pb, df_above], ignore_index=True, axis=0)

    return pvt_dataframe

#%%
## Example values for the function parameters
p_sep = 2500  # Separator pressure [psia]
t_sep = 150   # Separator temperature [F]
api = 35      # Stock tank oil gravity [API]
rsp = 500     # Separator producing GOR [scf/STB]
sg_sep = 0.7  # Separator gas specific gravity
tres = 180    # Reservoir temperature [F]
den_sto = 55  # Density of stock-tank oil [lb/cu ft]
p_res = 5000  # Initial reservoir pressure [psia]
salinity = 500  # Water Salinity [ppm]
jump = 100    # step size of the iteration over the pressure

# Call the function with these example values
result_df = pvt_table2(p_sep, t_sep, api, rsp, sg_sep, tres, den_sto, p_res, salinity, jump)
print(result_df)
