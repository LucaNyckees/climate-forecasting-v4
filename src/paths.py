from pathlib import Path
from typing import Literal

DATA_PATH = Path(__file__).parents[1] / "data"
FIGURES_PATH = Path(__file__).parents[1] / "figures"
REPORTS_PATH = Path(__file__).parents[1] / "reports"
DATAGENERATED_PATH = DATA_PATH / "generated"


def get_data_file_path(elt: str) -> Path:
    if elt == "Mean temperature":
        path = DATA_PATH / "observatoire-geneve" / "TG_STAID000241.txt"
    elif elt == "Sunshine duration":
        path = DATA_PATH / "SS_STAID000241.txt"
    return path
