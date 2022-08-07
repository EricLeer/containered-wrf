import logging
import os
import tarfile

import requests

logging.basicConfig(level=logging.INFO)

WRF_GEOG_URL = (
    "https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_low_res_mandatory.tar.gz"
)
GEOG_FILE_PATH = "geog_low_res_mandatory.tar.gz"


def get_geog_data():
    logging.info("Loading geog data")
    with open(GEOG_FILE_PATH, "wb") as file:
        r = requests.get(WRF_GEOG_URL)
        file.write(r.content)


def decompres_geog_files():
    logging.info("Decompressing geog tar file")
    with tarfile.open(GEOG_FILE_PATH) as file:
        file.extractall()
    logging.info("File decompresed, removing tar file")
    os.remove(GEOG_FILE_PATH)


if __name__ == "__main__":
    get_geog_data()
    decompres_geog_files()
