import logging
import subprocess
import os
from pathlib import Path
import glob

logger = logging.getLogger(__name__)


def run_wrf():
    logger.info("Running WPS..")
    subprocess.run([
        "mv",
        "/home/wrf/namelist.wps",
        "/home/wrf/WPS/namelist.wps"
    ])
    # subprocess.run([
    #    "cd",
    #    "/home/wrf/WPS"
    #])
    os.chdir("/home/wrf/WPS")

    logger.info("Converting geogrid")
    subprocess.run(["./geogrid.exe"])
    subprocess.run([
        "./link_grib.csh",
        "/home/wrf/data/GFS*"
        ])
    subprocess.run([
        "ln",
        "-sf",
        "ungrib/Variable_Tables/Vtable.GFS",
        "Vtable"
    ])
    logger.info("Running ungrib")
    subprocess.run(["./ungrib.exe"])

    subprocess.run(["./metgrid.exe"])

    logger.info("Running WRF model")
    os.chdir("/home/wrf/WRF/run")
    # subprocess.run(["cd /home/wrf/WRF/run"])
    #subprocess.run([
    #    "ln",
    #    "-sf",
    #    "/home/wrf/WPS/met_em*",
    #    "."])

    # TODO: Fix linking to the met_em files
    for meteofile in glob.glob("/home/wrf/WPS/met_em*"):
        print(meteofile)
        p = Path(f"./{meteofile.split('/')[-1]}")
        p.symlink_to(meteofile)

    subprocess.run([
        "mv",
        "/home/wrf/namelist.input",
        "namelist.input"
        ])

    subprocess.run([
        "mpirun",
        "-np",
        "1",
        "./real.exe"
        ])

    subprocess.run([
        "mpirun",
        "-np",
        "8",
        "./wrf.exe"])


if __name__ == "__main__":
    run_wrf()

