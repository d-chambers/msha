import pandas as pd

from msha.constants import (
    NON_INJURY_DEGREES,
    SEVERE_INJURY_DEGREES,
    GROUND_CONTROL_CLASSIFICATIONS,
    EASTERN_STATE_CODES,
)


def create_normalizer_df(prod_df, mines_df=None, freq='q'):
    """
    Create an aggregated dataframe of mine production/labor stats.

    Will include columns such as hours worked, employees, active mines, etc.
    These are useful for normalizing accident rates.

    Parameters
    ----------
    prod_df
        A dataframe of mine_id and production stats
    mines_df
        The dataframe containing the mine info.

    Returns
    -------
    A dataframe of mine stats for

    """
    if mines_df is not None:
        mine_ids = mines_df["mine_id"].unique()
        prod_df = prod_df[prod_df["mine_id"].isin(mine_ids)]
    # group by quarter, get stats, employee count,
    grouper = pd.Grouper(key="date", freq=freq)
    cols = ["employee_count", "hours_worked", "coal_production"]
    gb = prod_df.groupby(grouper)
    out = gb[cols].sum()
    # add number of active mines
    out["active_mine_count"] = gb["mine_id"].unique().apply(lambda x: len(x))
    out['no_normalization'] = 1
    return out


def aggregate_columns(df, column, freq='q'):
    """Aggregate columns by """
    grouper = pd.Grouper(key="date", freq=freq)
    # only include accidents
    df = df[df[column] != 'ACCIDENT ONLY']
    gr = df.groupby(grouper)[column]
    counts = gr.value_counts()
    counts.name = "count"
    piv_kwargs = dict(index="date", columns=column, values="count")
    piv = counts.reset_index().pivot(**piv_kwargs).fillna(0.0).astype(int)
    return piv

def aggregate_injuries(df, freq='q'):
    """Aggregate injuries for each quarter by classification."""
    column = 'degree_injury'
    grouper = pd.Grouper(key="date", freq=freq)
    # only include accidents
    df = df[df[column] != 'ACCIDENT ONLY']
    aggs = aggregate_columns(df, column=column, freq=freq)
    return aggs.sum(axis=1)


def aggregate_descriptive_stats(df, column, freq='q'):
    """Aggregate a dataframe by quarter for one columns descriptive stats."""
    grouper = pd.Grouper(key="date", freq=freq)
    out = df.groupby(grouper)[column].describe()
    return out


def normalize_injuries(accident_df, prod_df, mine_df=None, freq='q') -> pd.DataFrame:
    """
    Normalize accidents by each column in norm_df.

    Parameters
    ----------
    accident_df
        A dataframe with aggregated accidents, grouped by quarter.
    prod_df
        A dataframe with normalization denominator, grouped by quarter.
        Often contains number of mines, hours worked, coal production, etc.

    Returns
    -------
    A multi-index column df with the first level being norm_df columns
    and the second level being accident_df columns.
    """
    acc_ag = aggregate_injuries(accident_df, freq=freq)
    norm = create_normalizer_df(prod_df, mines_df=mine_df, freq=freq)
    # assign a columns of one for no normalizations
    # norm["no_normalization"] = 1
    # trim both dfs down to match indicies
    # new_dates = sorted(set(accident_df.index) & set(prod_df.index))
    return (acc_ag / norm.T).T


def is_ug_coal(df):
    """ Return a bool series indicating if each row is underground coal."""
    assert {"is_underground", "is_coal"}.issubset(set(df.columns))
    return df["is_underground"] & df["is_coal"]


def is_ground_control(df):
    """
    Return a bool series indicating if the accident is ground control related.
    """
    return df["classification"].isin(GROUND_CONTROL_CLASSIFICATIONS)


def is_eastern_us(df):
    """Return a series indicating if the mine is located east of missipi"""
    return df["state"].isin(set(EASTERN_STATE_CODES))
