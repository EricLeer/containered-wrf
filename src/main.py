import argparse
import ftplib
import logging
import os
import shutil
import subprocess
import tempfile
from datetime import datetime

import pendulum
import yaml

from load_wrf_geog import decompres_geog_files, get_geog_data
from post_forecast import process_post_forecast
from run_wrf import run_wrf

logging.basicConfig(level=logging.INFO)

BASE_NAMELIST_PATH = "base_namelist.yaml"


def create_namelist(forecast_date):
    """
    Creates a yaml namelist file, edits the given `forecast_date` and converts it into the wrf
    `namelist.input` and `namelist.wps` format.
    """
    base_namelist = open_base_namelist()

    base_namelist["run_info"]["start_date"] = forecast_date

    tmp_namelist_path = write_namelist_yaml(base_namelist)

    subprocess.run(["wrfconf", "create", tmp_namelist_path])


def open_base_namelist():
    with open(BASE_NAMELIST_PATH) as file:
        base_namelist = yaml.load(file, Loader=yaml.FullLoader)

    return base_namelist


def write_namelist_yaml(namelist_yaml):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
        yaml.dump(namelist_yaml, tmp)
        return tmp.name


def load_gfs_files_remote(forecast_start_date):
    gfs_url = "ftpprd.ncep.noaa.gov"
    gfs_path = f"pub/data/nccf/com/gfs/prod/gfs.{forecast_start_date.strftime('%Y%m%d')}/00/atmos/"

    ftp = ftplib.FTP(gfs_url)
    ftp.login()
    # ftp.login("UserName", "Password")
    ftp.cwd(gfs_path)
    for i in range(0, 25, 3):
        gfs_filename = f"gfs.t00z.pgrb2.0p50.f{i:03d}"
        local_filename = f"data/GFS_{i:02d}"

        logging.info(f"Loading file {gfs_filename} to {local_filename}")
        with open(local_filename, "wb") as f:
            ftp.retrbinary("RETR " + gfs_filename, f.write)
    ftp.quit()


def load_gfs_files_local(forecast_start_date, local_file_path, datetime="2022080100"):
    for i in range(0, 25, 3):
        gfs_filename = f"{local_file_path}/gfs.0p25.{datetime}.f{i:03d}.grib2"
        local_filename = f"data/GFS_{i:02d}"

        logging.info(f"Loading local file {gfs_filename} to {local_filename}")

        shutil.copy(gfs_filename, local_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create wrf namelist files")
    parser.add_argument("forecast_date", help="Forecast start date")
    parser.add_argument(
        "num_cores", default=1, help="number of cores used for forecasting"
    )
    parser.add_argument(
        "--post_api",
        type=bool,
        default=False,
        help="Post the resultant forecast to the api, else will be copied to the local system",
    )
    args = parser.parse_args()

    forecast_start_date = datetime.fromisoformat(args.forecast_date)

    logging.info("Creating namelist..")
    create_namelist(forecast_start_date.strftime("%Y-%m-%d_%H:%M:%S"))

    logging.info("Loading GFS initialization files..")

    gfs_local_path = "/home/wrf/external_data/gfs_forecasts"
    if os.path.exists(gfs_local_path):
        load_gfs_files_local(
            forecast_start_date,
            gfs_local_path,
            datetime=forecast_start_date.strftime("%Y%m%d00"),
        )
    else:
        load_gfs_files_remote(forecast_start_date)

    # Check for presence of geog file, if it is not there load it, else move it to the local location
    geog_path = "/home/wrf/external_data/WPS_GEOG_LOW_RES"
    if os.path.exists(geog_path):
        logging.info(f"GEOG data already loaded at {geog_path}, just moving files.")
        shutil.copytree(geog_path, "/home/wrf/WPS_GEOG_LOW_RES")
    else:
        get_geog_data()
        decompres_geog_files()

    run_wrf(num_cores=args.num_cores)

    output_filename = f"wrfout_d02_{forecast_start_date.strftime('%Y-%m-%d_%H:%M:%S')}"
    if args.post_api:
        process_post_forecast(
            output_filename,
            start=pendulum.instance(forecast_start_date),
        )
    else:
        output_filename_outer = f"wrfout_d01_{forecast_start_date.strftime('%Y-%m-%d_%H:%M:%S')}"

        shutil.copy(
            output_filename,
            f"/home/wrf/external_data/forecast_output/{output_filename}",
        )

        shutil.copy(
            output_filename_outer,
            f"/home/wrf/external_data/forecast_output/{output_filename_outer}",
        )
