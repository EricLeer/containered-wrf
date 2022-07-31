import argparse
import yaml
import tempfile
import subprocess

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create wrf namelist files')
    parser.add_argument('forecast_date', help='Forecast start date')

    args = parser.parse_args()
    
    create_namelist(args.forecast_date)

