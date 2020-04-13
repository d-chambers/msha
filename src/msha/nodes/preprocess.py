"""
Nodes for simple pre-processing.
"""
import pandas as pd

# --- Utils

# A mapping of column names to new names. If None just lowercase name.
COLUMN_MAP = {
    "MINE_ID": None,
    "CONTROLLER_NAME": None,
    "OPERATOR_ID": None,
    "SUBUNIT": None,
    "UG_LOCATION": None,
    "UG_MINING_METHOD": None,
    "CLASSIFICATION": None,
    "ACCIDENT_TYPE": None,
    "NO_INJURIES": "injury_count",
    "OCCUPATION": None,
    "ACTIVITY": None,
    "INJURY_SOURCE": None,
    "NATURE_INJURY": None,
    "INJ_BODY_PART": "body_part",
    "DAYS_RESTRICT": "days_restricted",
    "DAYS_LOST": "days_lost",
    "NARRATIVE": None,
    "ACCIDENT_DT": 'date',
}


def rename_and_drop(df):
    """
    Rename column names to names found in COLUMN_MAP or, if None, just lowercase.
    """
    col_set, map_set = set(df.columns), set(COLUMN_MAP)
    overlap = col_set & map_set
    sub_map = {x: COLUMN_MAP[x] for x in overlap}
    rename = {i: v if v is not None else i.lower() for i, v in sub_map.items()}
    return df.rename(columns=rename)


def drop_upper_case(df):
    """Drop all columns which are upper case."""
    upper_cols = [x for x in df.columns if x.isupper()]
    return df.drop(columns=upper_cols)



# --- Node functions


def preproc_accidents(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocessing for accidents.
    """
    out = (
        df.assign(is_coal=df['COAL_METAL_IND'] == 'C')
        .pipe(rename_and_drop)
        .pipe(drop_upper_case)
    )

    breakpoint()
    print(df)
    return out


def preproce_mines(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocessing for mines """



def preproce_production(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocessing for production."""


def dummy_download():
    """Simple function just to call download functions """
    return ""
