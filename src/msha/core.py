import pandas as pd

from msha.constants import NON_INJURY_DEGREES, SEVERE_INJURY_DEGREES




def create_normalizer_df(prod_df, mines_df):
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
    mine_ids = mines_df['mine_id'].unique()
    prod_sub = prod_df[prod_df['mine_id'].isin(mine_ids)]
    # group by quarter, get stats, employee count,
    grouper = pd.Grouper(key="date", freq="q")
    cols = ["employee_count", "hours_worked", "coal_production"]
    gb = prod_sub.groupby(grouper)
    out = gb[cols].sum()
    # add number of active mines
    out['active_mine_count'] = gb['mine_id'].unique().apply(lambda x: len(x))
    return out


def aggregate_accidents(df, column):
    """Aggregate injuries for each quarter by classification."""
    grouper = pd.Grouper(key="date", freq="q")
    gr = df.groupby(grouper)[column]
    counts = gr.value_counts()
    counts.name = "count"
    piv_kwargs = dict(index="date", columns=column, values="count")
    piv = counts.reset_index().pivot(**piv_kwargs).fillna(0.0).astype(int)
    return piv


def aggregate_descriptive_stats(df, column):
    """Aggregate a dataframe by quarter for one columns descriptive stats."""


def normalize_accidents(accident_df, norm_df) -> pd.DataFrame:
    """
    Normalize accidents by each column in norm_df.

    Parameters
    ----------
    accident_df
        A dataframe with aggregated accidents, grouped by quarter.
    norm_df
        A dataframe with normalization denominator, grouped by quarter.
        Often contains number of mines, hours worked, coal production, etc.

    Returns
    -------
    A multi-index column df with the first level being norm_df columns
    and the second level being accident_df columns.
    """
    # trim both dfs down to match indicies
    new_dates = sorted(set(accident_df.index) & set(norm_df.index))
    adf = accident_df.loc[new_dates]
    pdf = norm_df.loc[new_dates]
    # assign a columns of one for no normalizations
    pdf["no_normalization"] = 1
    # get non, injury, and severe categories
    category = dict(
        injury=set(adf) - set(NON_INJURY_DEGREES),
        non_injury=NON_INJURY_DEGREES,
        severe=SEVERE_INJURY_DEGREES,
    )
    multi_index = pd.MultiIndex.from_product([pdf.columns, list(category)])
    out = pd.DataFrame(index=new_dates, columns=multi_index)
    # calc normalized columns, populate dataframe
    for category_name, cols in category.items():
        adf_ = adf[cols].sum(axis=1)
        for normalization_col_name, series in pdf.iteritems():
            norm = adf_ / series
            out.loc[:, (normalization_col_name, category_name)] = norm
    return out
