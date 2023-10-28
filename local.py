"""
Local configuration for MSHA.
"""
from pathlib import Path

import pandas as pd

here = Path(__file__).absolute().parent
input_path = here / 'inputs'
output_path = here / 'outputs'
output_path.mkdir(exist_ok=True, parents=True)

_base_msha_url = "https://arlweb.msha.gov/OpenGovernmentData/DataSets/"

msha_defintion_url = {
    "accidents": f"{_base_msha_url}Accidents_Definition_File.txt",
    "production": f"{_base_msha_url}MineSProdQuarterly_Definition_File.txt",
    "mines": f"{_base_msha_url}Mines_Definition_File.txt",
}

msha_download_url = dict(
    mines=f"{_base_msha_url}Mines.zip",
    accidents=f"{_base_msha_url}Accidents.zip",
    production=f"{_base_msha_url}MinesProdQuarterly.zip",
)

raw_msha_path = output_path / "a010_raw_data"
raw_msha_path.mkdir(exist_ok=True, parents=True)

msha_definition_paths = {
    "mines": raw_msha_path / "msha_mines_definitions.txt",
    "accidents": raw_msha_path / "msha_accidents_definitions.txt",
    "production": raw_msha_path / "msha_production_definitions.txt",
}

msha_raw_data_paths = {
    "mines": raw_msha_path / "msha_mines.csv",
    "accidents": raw_msha_path / "msha_accidents.csv",
    "production": raw_msha_path / "msha_production.csv",
}

# processed msha data
msha_data_paths = {
    "mines": output_path / "a020_mines.pkl",
    "accidents": output_path / "a020_accidents.pkl",
    "production": output_path / "a020_production.pkl",
}
