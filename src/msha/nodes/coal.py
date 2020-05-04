"""
Nodes for calculating aggregated underground coal stats.
"""
import matplotlib.pyplot as plt
import pandas as pd

from pandas.plotting import register_matplotlib_converters

from msha.core import normalize_accidents, create_normalizer_df, aggregate_accidents, aggregate_descriptive_stats

register_matplotlib_converters()



from msha.constants import (
    GROUND_CONTROL_CLASSIFICATIONS,
)


def aggregate_coal_production(prod_df, mines_df):
    """ Aggregate production by quarter. """
    # filter production to only include underground coal mines
    # and only the underground subunits
    con1 = mines_df["is_underground"] & mines_df["is_coal"]
    mine_sub = mines_df[con1]
    con2 = prod_df["subunit"] == "UNDERGROUND"
    prod_sub = prod_df[con2]
    breakpoint()
    return create_normalizer_df(prod_sub, mine_sub)


def aggregate_coal_accidents_by_classification(df):
    """Aggregate accidents by quarter. They must have caused an injury. """
    # first select only ug coal for which there were injuries
    con = df["is_underground"] & df["is_coal"]
    has_injury = df["injury_count"].astype(bool)
    df_sub = df[con & has_injury]
    return aggregate_accidents(df_sub, column='classification')


def ground_control_coal_accidents(df):
    """Create a dataframe of ground-control related coal accidents."""
    con1 = df["is_coal"]
    con2 = df["is_underground"]
    con3 = df["classification"].isin(GROUND_CONTROL_CLASSIFICATIONS)
    df_sub = df[con1 & con2 & con3]
    return aggregate_accidents(df_sub, column='degree_injury')


def normalized_ground_control_coal_accidents(accident_df, prod_df):
    """Create a dataframe, grouped by quarter, with normalized values. """
    return normalize_accidents(accident_df, prod_df)


def aggregate_gc_coal_experience_stats(accident_df):
    """Return aggregated descriptibe stas of mine experience. """
    con1 = accident_df["is_coal"]
    con2 = accident_df["is_underground"]
    con3 = accident_df["classification"].isin(GROUND_CONTROL_CLASSIFICATIONS)
    sub_df = accident_df[con1 & con2 & con3]
    breakpoint()
    aggregate_descriptive_stats(sub_df, 'miner_experience')
    print(sub_df)



def plot_employees_and_mines(prod_df):
    """Make a plot of employee count and number of coal mines."""
    # define plot colors
    c1, c2 = ("#176EFF", '#FF4124')

    # plot production and active mine count
    df = prod_df
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8), sharex=True)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Employees ($10^3$)')
    ax1.plot(df.index, df['employee_count']/1_000, color=c1)
    ax1_twin = plt.twinx(ax1)
    ax1_twin.plot(prod_df.index, prod_df['active_mine_count'], color=c2)
    ax1_twin.set_ylabel('Active Mines')
    # color axis/ticks
    ax1_twin.spines['left'].set_color(c1)
    ax1_twin.spines['right'].set_color(c2)
    ax1_twin.tick_params(axis='y', colors=c2)
    ax1.tick_params(axis='y', colors=c1)
    # plot hours and tonnes
    c3, c4 = ('#0BE7FF', '#B35900')
    ax2.plot(prod_df.index, prod_df['hours_worked']/1_000_000, color=c3, )
    ax2.set_ylabel('Hours Worked ($10^6$)')
    ax2_twin = plt.twinx(ax2)
    ax2_twin.plot(prod_df.index, prod_df['coal_production']/1_000_000, color=c4)
    ax2_twin.set_ylabel('Short Tones Produced ($10^6$)')
    # color axis/ticks
    ax2_twin.spines['left'].set_color(c3)
    ax2_twin.spines['right'].set_color(c4)
    ax2_twin.tick_params(axis='y', colors=c4)
    ax2.tick_params(axis='y', colors=c3)
    plt.tight_layout()
    # plt.plot(df.index, df['employee_count'])
    return plt
