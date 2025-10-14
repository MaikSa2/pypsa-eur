#from scripts.build_cop_profiles.run import get_cop
import xarray as xr
from _helpers import load_cutout, get_snapshots
import pandas as pd
import numpy as np
import geopandas as gpd
from dask.distributed import Client, LocalCluster
from definitions.heat_system_type import HeatSystemType
from build_cop_profiles.CentralHeatingCopApproximator_new import (
    CentralHeatingCopApproximator,
)

heat_source_cooling_central_heating= 6 # config_provider(
            #"sector", "district_heating", "heat_source_cooling"
        #),

heat_pump_cop_approximation_central_heating=   {                    #config_provider(
  "refrigerant": "ammonia",                                         # "sector", "district_heating", "heat_pump_cop_approximation"
  "heat_exchanger_pinch_point_temperature_difference": 5,   # K     #),
  "isentropic_compressor_efficiency": 0.8,                  # -
  "heat_loss": 0.0,                                          # -
  "min_delta_t_lift": 10,                                   # K
}     
            
def get_cop(
    heat_system_type: str,
    heat_source: str,
    source_inlet_temperature_celsius: xr.DataArray,
    sink_outlet_temperature_celsius: xr.DataArray = None,
    sink_inlet_temperature_celsius: xr.DataArray = None,
) -> xr.DataArray:
    """
    Calculate the coefficient of performance (COP) for a heating system.

    Parameters
    ----------
    heat_system_type : str
        The type of heating system.
    heat_source : str
        The heat source used in the heating system.
    source_inlet_temperature_celsius : xr.DataArray
        The inlet temperature of the heat source in Celsius.

    Returns
    -------
    xr.DataArray
        The calculated coefficient of performance (COP) for the heating system.
    """
    if HeatSystemType(heat_system_type).is_central:
        return CentralHeatingCopApproximator(
            sink_outlet_temperature_celsius=sink_outlet_temperature_celsius,
            sink_inlet_temperature_celsius=sink_inlet_temperature_celsius,
            source_inlet_temperature_celsius=source_inlet_temperature_celsius,
            source_outlet_temperature_celsius=source_inlet_temperature_celsius
            - heat_source_cooling_central_heating,                                                            #snakemake.params.
            refrigerant=heat_pump_cop_approximation_central_heating[                                          #snakemake.params.
                "refrigerant"
            ],
            delta_t_pinch_point=heat_pump_cop_approximation_central_heating[                                   #snakemake.params.
                "heat_exchanger_pinch_point_temperature_difference"
            ],
            isentropic_compressor_efficiency=heat_pump_cop_approximation_central_heating[                       #snakemake.params.
                "isentropic_compressor_efficiency"
            ],
            heat_loss=heat_pump_cop_approximation_central_heating[                                              #snakemake.params.
                "heat_loss"
            ],
            min_delta_t_lift=heat_pump_cop_approximation_central_heating[                                       #snakemake.params.
                "min_delta_t_lift"
            ],
        ).approximate_cop()

    else:
        return print("HeatSystem is not type central") #DecentralHeatingCopApproximator(
            #sink_outlet_temperature_celsius=snakemake.params.heat_pump_sink_T_decentral_heating,
            #source_inlet_temperature_celsius=source_inlet_temperature_celsius,
            #source_type=heat_source,
        #).approximate_cop()
        # 

snapshots= {"start": "2013-01-01", "end": "2014-01-01", "inclusive": "left"}    # config_provider("snapshots")
drop_leap_day= True                                                             # config_provider("enable", "drop_leap_day")
time = get_snapshots(snapshots, drop_leap_day)                                                          # snakemake.params.snapshots, snakemake.params.drop_leap_day

#cutout=lambda w: input_cutout(
#            w, config_provider("sector", "heat_demand_cutout")(w)
#        ),

#cutout = load_cutout(snakemake.input.cutout, time=time)
cutout = load_cutout(r"/home/student_01/Student_Folders/Maik/pypsa-eur/cutouts/europe-2013-sarah3-era5.nc", time)

regions_onshore = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/a4_base_shipping_ME_SH2_MG/regions_onshore_base_s_20.geojson"
clustered_regions = (
        gpd.read_file(regions_onshore).set_index("name").buffer(0)       #regions_onshore=resources("regions_onshore_base_s_{clusters}.geojson"), snakemake.input.regions_onshore
    )
I = cutout.indicatormatrix(clustered_regions)  # noqa: E741
pop_layout = xr.open_dataarray(r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/a4_base_shipping_ME_SH2_MG/pop_layout_total.nc") # pop_layout=resources("pop_layout_total.nc"), xr.open_dataarray(snakemake.input.pop_layout)

stacked_pop = pop_layout.stack(spatial=("y", "x"))
M = I.T.dot(np.diag(I.dot(stacked_pop)))

nonzero_sum = M.sum(axis=0, keepdims=True)
nonzero_sum[nonzero_sum == 0.0] = 1.0
M_tilde = M / nonzero_sum

nprocesses = int(8)                                                     # threads: 8
cluster = LocalCluster(n_workers=nprocesses, threads_per_worker=1)
client = Client(cluster, asynchronous=True)

temp_air = cutout.temperature(
        matrix=M_tilde.T,
        index=clustered_regions.index,
        dask_kwargs=dict(scheduler=client),
        show_progress=False,
    )

temp_air_path= r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/a4_base_shipping_ME_SH2_MG/new_temperature.nc"                           # resources("temp_air_total_base_s_{clusters}.nc")
temp_air.to_netcdf(temp_air_path)                                                                        # snakemake.output.temp_air

heat_system_type = "urban central"
heat_source = "air"
source_inlet_temperature_celsius_path = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/a4_base_shipping_ME_SH2_MG/new_temperature.nc"
source_inlet_temperature_celsius = xr.open_dataarray(
                    source_inlet_temperature_celsius_path            # snakemake.input[f"temp_{heat_source.replace('ground', 'soil')}_total"]
                )

central_heating_forward_temperature_path = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/a4_base_shipping_ME_SH2_MG/central_heating_forward_temperature_profiles_base_s_20_2050.nc"

central_heating_forward_temperature: xr.DataArray = xr.open_dataarray(
            central_heating_forward_temperature_path                                    #resources("central_heating_forward_temperature_profiles_base_s_{clusters}_{planning_horizons}.nc"), snakemake.input.central_heating_forward_temperature_profiles
    )

central_heating_return_temperature_path = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/a4_base_shipping_ME_SH2_MG/central_heating_return_temperature_profiles_base_s_20_2050.nc"

central_heating_return_temperature: xr.DataArray = xr.open_dataarray(
            central_heating_return_temperature_path                                    #resources("central_heating_return_temperature_profiles_base_s_{clusters}_{planning_horizons}.nc"), snakemake.input.central_heating_return_temperature_profiles
    )

cop_da = get_cop(
                heat_system_type=heat_system_type,
                heat_source=heat_source,
                source_inlet_temperature_celsius=source_inlet_temperature_celsius,
                sink_outlet_temperature_celsius=central_heating_forward_temperature,
                sink_inlet_temperature_celsius=central_heating_return_temperature,
            )

print(cop_da)