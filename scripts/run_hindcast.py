import logging
import subprocess
import pandas as pd

logging.basicConfig(level=logging.INFO)

#docker run -v /home/eric/data:/home/wrf/external_data weathercast:latest python3 main.py 2022-08-02 4


if __name__ == '__main__':
    start_date = "2022-08-01"
    end_date = "2022-08-31"
    logging.info("Running hindcast from {start_date} till {end_date}")
    
    dates = pd.date_range(start=start_date, end=end_date, freq="1D")

    for date in dates:
        date_str = date.strftime("%Y-%m-%d")
        logging.info(f"current date_str: {date_str}")
        
        subprocess.run([
                "docker",
                "run",
                "--rm",
                "-v",
                "/home/eric/data:/home/wrf/external_data",
                "weathercast:latest",
                "python3",
                "main.py",
                date_str,
                "4",
                "--postprocess",
                "true",
                "--save_folder",
                "exp_001"
            ])
