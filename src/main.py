import argparse
import yaml
import tempfile
import subprocess
import ftplib
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

BASE_NAMELIST_PATH = "base_namelist.yaml"

def create_namelist(forecast_date):
    """
    Creates a yaml namelist file, edits the given `forecast_date` and converts it into the wrf 
    `namelist.input` and `namelist.wps` format. 
    """
    base_namelist = open_base_namelist()
   
    base_namelist['run_info']['start_date'] = forecast_date

    tmp_namelist_path = write_namelist_yaml(base_namelist)
    
    subprocess.run([
        "wrfconf", 
        "create",
        tmp_namelist_path
    ])

def open_base_namelist():
    with open(BASE_NAMELIST_PATH) as file:
        base_namelist = yaml.load(file, Loader=yaml.FullLoader)

    return base_namelist

def write_namelist_yaml(namelist_yaml):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
        yaml.dump(namelist_yaml, tmp)
        return tmp.name

def load_gfs_files(forecast_start_date):
    gfs_url = "ftpprd.ncep.noaa.gov"
    gfs_path = f"pub/data/nccf/com/gfs/prod/gfs.{forecast_start_date.strftime('%Y%m%d')}/00/atmos/"

    ftp = ftplib.FTP(gfs_url)
    ftp.login()
    # ftp.login("UserName", "Password") 
    ftp.cwd(gfs_path)
    for i in range(0,25,3):
        gfs_filename = f'gfs.t00z.pgrb2.0p50.f{i:03d}'
        local_filename = f"data/GFS_{i:02d}"

        logging.info(f"Loading file {gfs_filename} to {local_filename}")
        with open(local_filename, 'wb') as f:
            ftp.retrbinary("RETR " + gfs_filename, f.write)
    ftp.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create wrf namelist files')
    parser.add_argument('forecast_date', help='Forecast start date')

    args = parser.parse_args()
    
    forecast_start_date = datetime.fromisoformat(args.forecast_date)
    
    logging.info("Creating namelist..")
    create_namelist(forecast_start_date.strftime('%Y-%m-%d_%H:%M:%S'))

    logging.info("Loading GFS initialization files..")
    load_gfs_files(forecast_start_date)

