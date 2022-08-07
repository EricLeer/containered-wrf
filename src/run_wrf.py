import logging
import subprocess

logger = logging.get_logger(__name__)


def run_wrf():
    logger.info("Running WPS..")
    subprocess.run(["mv namelist.wps WPS/namelist.wps"])
    subprocess.run(["cd /home/wrf/WPS"])
    logger.info("Converting geogrid")
    subprocess.run(["./geogrid.exe >& log.geogrid"])
    subprocess.run(["./link_grib.csh /home/wrf/data/GFS*"])
    logger.info("Running ungrib")
    subprocess.run(["./ungrib.exe"])

    logger.info("Running WRF model")
    subprocess.run(["cd /home/wrf/WRF/run"])
    subprocess.run(["ln -sf /home/wrf/WPS/met_em* ."])
    subprocess.run(["mv /home/wrf/namelist.input namelist.input"])

    subprocess.run(["mpirun -np 1 ./real.exe"])

    subprocess.run(["mpirun -np 8 ./wrf.exe"])


if __name__ == "__main__":
    run_wrf()
