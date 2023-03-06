import argparse
import numpy as np

import xarray as xr
import xwrf
import xesmf as xe

import logging

def postprocess_wrf(wrf_location, save_to_file=False):
    logging.info(f"Opening file: {wrf_location}")
    ds_wrf = xr.open_mfdataset(wrf_location, engine='netcdf4')

    ds_wrf = ds_wrf.xwrf.postprocess()
    ds_wrf = ds_wrf.xwrf.destagger()
    
    ds_wrf = ds_wrf.rename({"XLONG": "lon", "XLAT": "lat"})
    
    
    ds_out = xr.Dataset(
    {
        "lat": (["lat"], np.arange(
            ((ds_wrf.lat.min().values+0.6)/5).round(1)*5, 
            ((ds_wrf.lat.max().values-0.6)/5).round(1)*5, 
            0.25
        ), {"units": "degrees_north"}),
        "lon": (["lon"], np.arange(
            ((ds_wrf.lon.min().values+0.9)/5).round(1)*5, 
            ((ds_wrf.lon.max().values-0.6)/5).round(1)*5, 
            0.25
        ), {"units": "degrees_east"}),
        }
    )
    
    regridder = xe.Regridder(ds_wrf, ds_out, "bilinear")
    
    ds_wrf_out = regridder(ds_wrf, keep_attrs=True)
    ds_wrf_out = ds_wrf_out.drop(['XTIME', 'x_stag', 'y_stag', 'z_stag'])
    ds_wrf_out = ds_wrf_out[[
        'U', 
        'V', 
        'air_potential_temperature',
        'air_pressure',
        'wind_east', 
        'wind_north',
        'geopotential_height',
        'geopotential',
        'T2', 
        'U10', 
        'V10',
    ]]

    output_file = f"{wrf_location}_processed.nc"
    logging.info(f"Writing to file: {output_file}")
    ds_wrf_out.to_netcdf(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Postprocess wrf forecast files")
    parser.add_argument("file_location", help="Location of the wrf forecast file")
    
    args = parser.parse_args()
    postprocess_wrf(wrf_location=args.file_location)
