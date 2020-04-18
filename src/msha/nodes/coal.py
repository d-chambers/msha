"""
Nodes for calculating aggregated underground coal stats.
"""
import pandas as pd

from msha.constants import GROUND_CONTROL_CLASSIFICATIONS, NON_INJURY_DEGREES, SEVERE_INJURY_DEGREES


def aggregate_production(prod_df, mines_df):
    """ Aggregate production by quarter. """
    # get mine ids of underground coal mines
    con = mines_df["is_underground"] & mines_df["is_coal"]
    mine_ids = mines_df[con]["mine_id"].unique()
    # filter production to only include underground coal mines
    # and only the underground subunits
    con1 = prod_df["mine_id"].isin(mine_ids)
    con2 = prod_df["subunit"] == "UNDERGROUND"
    prod_sub = prod_df[con1 & con2]
    # group by quarter, get stats, employee count,
    grouper = pd.Grouper(key="date", freq="q")
    cols = ["employee_count", "hours_worked", "coal_production"]
    out = prod_sub.groupby(grouper)[cols].sum()
    return out


def aggregate_accidents(df):
    """Aggregate accidents by quarter. They must have caused an injury. """
    # first select only ug coal for which there were injuries
    con = df["is_underground"] & df["is_coal"]
    has_injury = df["injury_count"].astype(bool)
    df_sub = df[con & has_injury]
    # group by quarter
    grouper = pd.Grouper(key="date", freq="q")
    gr = df_sub.groupby(grouper)["classification"]
    counts = gr.value_counts()
    counts.name = "count"
    piv_kwargs = dict(index="date", columns="classification", values="count")
    piv = counts.reset_index().pivot(**piv_kwargs)
    return piv


def ground_control_coal_accidents(df):
    """Create a dataframe of ground-control related coal accidents."""
    con1 = df['is_coal']
    con2 = df['is_underground']
    con3 = df['classification'].isin(GROUND_CONTROL_CLASSIFICATIONS)
    df_sub = df[con1 & con2 & con3]
    # group by quarter, value_count on degree injury
    grouper = pd.Grouper(key="date", freq="q")
    gr = df_sub.groupby(grouper)["degree_injury"]
    counts = gr.value_counts()
    counts.name = 'count'
    piv_kwargs = dict(index="date", columns="degree_injury", values="count")
    out = counts.reset_index().pivot(**piv_kwargs).fillna(0.0).astype(int)
    return out


def normalized_ground_control_coal_accidents(accident_df, prod_df):
    """Create a dataframe, grouped by quarter, with normalized values. """
    # trim both dfs down to match indicies
    new_dates = sorted(set(accident_df.index) & set(prod_df.index))
    adf = accident_df.loc[new_dates]
    pdf = prod_df.loc[new_dates]
    # assign a columns of one for no normalizations
    pdf['no_normalization'] = 1
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

    import matplotlib.pyplot as plt
    breakpoint()
    return out