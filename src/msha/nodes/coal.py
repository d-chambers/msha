"""
Nodes for calculating aggregated underground coal stats.
"""
import pandas as pd


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
    out = prod_df.groupby(grouper)[cols].sum()
    return out


def aggregate_accidents(df):
    """Aggregate accidents by quarter. They must have caused an injury. """
    # first select only ug coal for which there were injuries
    con = df["is_underground"] & df["is_coal"]
    has_injury = df["injury_count"].astype(bool)
    df_sub = df[con & has_injury]
    grouper = pd.Grouper(key="date", freq="q")
    gr = df_sub.groupby(grouper)["classification"]
    counts = gr.value_counts()
    counts.name = "count"
    piv_kwargs = dict(index="date", columns="classification", values="count")
    piv = counts.reset_index().pivot(**piv_kwargs)
    return piv


def ground_control_coal_accidents(df):
    """Create a dataframe of ground-control related coal accidents."""
    breakpoint()
    print(df)
