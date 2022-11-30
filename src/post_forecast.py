import xarray as xr
import pandas as pd
import pendulum
import requests
import numpy as np
import logging

logger = logging.getLogger(__name__)

SERVER_URL = "https://weather.ericleer.com/v1/weather"

def select_point(ds, lat, lon):
    # First, find the index of the grid point nearest a specific lat/lon.   
    abslat = np.abs(ds.XLAT[0]-lat)
    abslon = np.abs(ds.XLONG[0]-lon)
    c = np.maximum(abslon, abslat)

    ([xloc], [yloc]) = np.where(c == np.min(c))

    # Now I can use that index location to get the values at the x/y diminsion
    return ds.sel(south_north=xloc, west_east=yloc)

def construct_json(point_ds):
    logger.info("Constructing json")
    json_arr = []

    forecast_timestamp = pd.to_datetime(
        point_ds.attrs["SIMULATION_START_DATE"], 
        format="%Y-%m-%d_%H:%M:%S"
    ).strftime('%Y-%m-%dT%H:%M:%SZ')


    for i, time in enumerate(point_ds.Time):
        json_arr.append({
            "Location": "Amsterdam",
            "Timestamp": pd.to_datetime(str(time.values)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "Forecast_timestamp": forecast_timestamp,
            "windspeed": point_ds["windspeed"][i].item(),
            "wind_direction": point_ds["wind_direction"][i].item(),
            "temperature": point_ds["T2"][i].item(),
            "rain": point_ds["RAINNC"][i].item()
        })
    return json_arr

def process_post_forecast(filename, start):
    # I want to find the speed at a certain lat/lon point.
    logger.info(f"Loading file {filename} as xarray")
    ds = xr.load_dataset(filename, engine="netcdf4")

    end = start.add(hours=24)

    period = pendulum.period(start, end)

    ds = ds.assign_coords({"Time": list(period.range("hours", 1))})
    ds["windspeed"] = np.sqrt((ds["U10"]**2 + ds["V10"]**2))
    ds["wind_direction"] = (np.rad2deg(np.arctan(ds["V10"] / ds["U10"])) * 2)

    lat_min = 48
    lat_max = 56
    lon_min = 3
    lon_max = 9

    for lat in np.arange(lat_min, lat_max, 0.1):
        for lon in np.arange(lon_min, lon_max, 0.1):
            lat=lat.round(1),
            lon=lon.round(1),
            logger.info(f"Selecting point {(lat, lon)}")
            point_ds = select_point(ds, lat, lon)

            json_arr = construct_json(point_ds)
    
            logger.info(f"Posting {len(json_arr)} forecasts to the api")
            r = requests.post(SERVER_URL, json=json_arr)
            r.raise_for_status()

