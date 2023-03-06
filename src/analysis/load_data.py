import pandas as pd
import xarray as xr
import numpy as np

WEATHERSTATION_DATA_FILENAME = "/Users/ericleer/projects/weather_forecasting/data/knmi_weerstation/weerstation_2022.txt"
WEATHERSTATION_METADATA_FILENAME = "/Users/ericleer/projects/weather_forecasting/data/knmi_weerstation/STD___OPER_P___OBS_____L2.nc"



def load_weatherstation_metadata():
    ds_disk = xr.open_dataset(WEATHERSTATION_METADATA_FILENAME)

    df_weather_station_meta = ds_disk.to_dataframe()
    df_weather_station_meta['station_id'] = df_weather_station_meta['WMO'].astype(str).str[2:].astype(int)
    return df_weather_station_meta[["station_id", "lat", "lon"]]

def load_knmi_weatherstation():

    df = pd.read_csv(WEATHERSTATION_DATA_FILENAME, na_values=['     '])
    df = df.rename(columns={"# STN": "station_id"})

    df["timestamp"] = pd.to_datetime(df['YYYYMMDD'], format="%Y%m%d")
    df["timestamp"] = df.apply(lambda x: x["timestamp"] + pd.Timedelta(hours=x["   HH"]), axis=1)

    df = df.set_index('timestamp')
    df = df.drop(['YYYYMMDD', '   HH'], axis=1)
    df.columns = [column.strip() for column in df.columns]

    df_weather_station_meta = load_weatherstation_metadata()

    df = df.reset_index().merge(df_weather_station_meta, on="station_id").set_index('timestamp')
    df[['lat', "lon"]] = df[['lat', "lon"]].round(2)

    df = df.reset_index().set_index(['timestamp', "lat", "lon"])
    return df


## TODO: Remove the need for global variables here
def get_gfs_station_series(station_id, variable="temp"):
    station_location = station_location_map[station_id]
    
    if variable == "temp":
        gfs_temp = (
            stacked.sel(
                latitude=station_location["lat"], 
                longitude=station_location["lon"], 
                method="nearest"
            )['t'] - 273
        ).to_dataframe()['t']

        knmi_temp = (df[df.station_id == station_id].reset_index(['lat', 'lon'])['T']*0.1)
        return gfs_temp, knmi_temp

def construct_filenames(start, end):

    forecast_days = [day.strftime("%Y%m%d%H") for day in pd.date_range(start=start, end=end, freq="1D")]
    base_string = "/Users/ericleer/projects/weather_forecasting/data/GFS/gfs/"
    skip_day_list = [
        "2022040700",
        "2022061500"
    ]
    multi_filename = []
    for day in forecast_days:
        if day in skip_day_list:
            continue
        file_names = []
        for ahead_time in np.arange(0,48, 3):
            file_names.append(base_string + f"gfs.0p25.{day}.f{ahead_time:03d}.grib2")
        multi_filename.append(file_names)
    return multi_filename

def open_gfs_multi_files(multi_filename, type_of_level='surface'):
    ds_multi = xr.open_mfdataset(multi_filename, combine='nested', concat_dim=['time', 'step'], filter_by_keys={'stepType': 'instant', 'typeOfLevel': type_of_level})
    return ds_multi
    ds_first_day = ds_multi.sel(step=(ds_multi.step < np.timedelta64(1, 'D')))

    stacked = ds_first_day.stack(forecast_time=("time", "step"))
    stacked = stacked.assign_coords({"forecast_time": stacked.valid_time})
    return stacked


def load_gfs(start, end):
    multi_filename = construct_filenames(start, end)

    stacked = open_gfs_multi_files(multi_filename)
    stacked_level = open_gfs_multi_files(multi_filename, type_of_level='isobaricInhPa')
    stacked_level['windspeed'] = np.sqrt(stacked_level["u"]**2 + stacked_level["v"]**2)

    return stacked, stacked_level