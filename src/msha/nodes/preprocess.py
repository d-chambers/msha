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
    "DEGREE INJRUY": None,
    "OCCUPATION": None,
    "ACTIVITY": None,
    "INJURY_SOURCE": None,
    "NATURE_INJURY": None,
    "INJ_BODY_PART": "body_part",
    "DAYS_RESTRICT": "days_restricted",
    "DAYS_LOST": "days_lost",
    "NARRATIVE": None,
    "ACCIDENT_DT": "date",
    "CURRENT_MINE_NAME": None,
    "CURRENT_MINE_TYPE": None,
    "LATTITUDE": None,
    "LONGITUDE": None,
    "PROD_SHIFTS_PER_DAY": None,
    "CURRENT_STATUS_DT": "last_updated",
    "STATE": "state",
    "CURRENT_CONTROLLER_BEGIN_DT": "controller_start",
    "PRIMARY_CANVASS": None,
    "SECONDAY_CANVASS": None,
    "NO_EMPLOYEES": "employee_count",
    "AVG_EMPLOYEE_CNT": "employee_count",
    "HOURS_WORKED": None,
    "COAL_PRODUCTION": None,
}


def rename(df):
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
        df.assign(is_coal=df["COAL_METAL_IND"] == "C")
        .assign(is_underground=df["SUBUNIT"] == "UNDERGROUND")
        .pipe(rename)
        .pipe(drop_upper_case)
    )
    return out


def preproce_mines(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocessing for mines """
    assignments = dict(
        is_underground=df["CURRENT_MINE_TYPE"] == "Underground",
        is_surface=df["CURRENT_MINE_TYPE"] == "Surface",
        is_active=df["CURRENT_MINE_STATUS"] == "ACTIVE",
        is_coal=df["PRIMARY_CANVASS"] == "Coal",
        is_metal=df["PRIMARY_CANVASS"] == "Metal",
    )
    out = df.assign(**assignments).pipe(rename).pipe(drop_upper_case)
    return out


def preproce_production(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocessing for production."""

    def _add_production_date(df):
        """Add the date to the projection using the year cols and quarter. """
        dst = df["CAL_YR"].astype(str) + "-Q" + df["CAL_QTR"].astype(str)
        df["date"] = pd.to_datetime(dst)
        return df

    return df.pipe(_add_production_date).pipe(rename).pipe(drop_upper_case)


def dummy_download():
    """Simple function just to call download functions """
    return ""
