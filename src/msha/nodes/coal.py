"""
Nodes for calculating aggregated underground coal stats.
"""
import matplotlib.pyplot as plt
import pandas as pd

from pandas.plotting import register_matplotlib_converters

from msha.core import normalize_accidents, create_normalizer_df, aggregate_accidents, aggregate_descriptive_stats, \
    is_ug_coal, is_ground_control, is_eastern_us

from msha.constants import (
    GROUND_CONTROL_CLASSIFICATIONS,
)

register_matplotlib_converters()
plt.style.use(['bmh'])


def aggregate_injuries(df, **kwargs):
    """
    Aggregate injuries.

    kwargs are used to specify values for columns.

    EG ug_mining_method='Longwall' will select all rows where ug_mining_method
    is equal to 'Longwall'.
    """
    # filter out only accidents (no injuries)
    df = df[df['degree_injury'] != 'ACCIDENT ONLY']
    # filter out non-selected method
    for colname, value in kwargs.items():
        df = df[df[colname] == value]
    grouper = pd.Grouper(key="date", freq="q")
    size = df.groupby(grouper).size()
    return size


def is_ug_gc_accidents(df):
    """Return a dataframe where each row is an ug gc accident."""
    con1 = is_ug_coal(df)
    con2 = is_ground_control(df)
    return con1 & con2


def ground_control_coal_accidents(df):
    """Create a dataframe of ground-control related coal accidents."""

    df_sub = df[is_ug_coal(df) & is_ground_control(df)]
    return aggregate_accidents(df_sub, column='degree_injury')


def aggregate_coal_production(prod_df, mines_df):
    """ Aggregate production by quarter. """
    # filter production to only include underground coal mines
    # and only the underground subunits
    mine_sub = mines_df[is_ug_coal(mines_df)]
    con2 = prod_df["subunit"] == "UNDERGROUND"
    prod_sub = prod_df[con2]
    return create_normalizer_df(prod_sub, mine_sub)


def aggregate_coal_accidents_by_classification(df):
    """Aggregate accidents by quarter. They must have caused an injury. """
    # first select only ug coal for which there were injuries
    has_injury = df["injury_count"].astype(bool)
    df_sub = df[is_ug_coal(df) & has_injury]
    return aggregate_accidents(df_sub, column='classification')


def normalized_ground_control_coal_accidents(accident_df, prod_df):
    """Create a dataframe, grouped by quarter, with normalized values. """
    out = normalize_accidents(accident_df, prod_df)
    return out


def aggregate_gc_coal_experience_stats(accident_df):
    """Return aggregated description stats of mine experience. """
    con3 = accident_df["classification"].isin(GROUND_CONTROL_CLASSIFICATIONS)
    sub_df = accident_df[is_ug_coal(accident_df) & con3]
    return aggregate_descriptive_stats(sub_df, 'total_experience')


# ----- Plotting functions


def plot_employees_and_mines(prod_df, accidents_normed):
    """Make a plot of employee count and number of coal mines."""
    plt.clf()
    # define plot colors
    c1, c2 = ("#176EFF", '#FF4124')
    # plot production and active mine count
    injuries = accidents_normed[('no_normalization', 'injury')]
    df = prod_df
    fig, (ax2, ax1) = plt.subplots(2, 1, figsize=(5.5, 7), sharex=True)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Employees ($10^3$)')
    ax1.plot(df.index, df['employee_count']/1_000, color=c1)
    ax1_twin = plt.twinx(ax1)
    ax1_twin.plot(injuries.index, injuries, color=c2)
    ax1_twin.set_ylabel('GC Injuries per Quarter')
    # color axis/ticks
    ax1_twin.spines['left'].set_color(c1)
    ax1_twin.spines['right'].set_color(c2)
    ax1_twin.tick_params(axis='y', colors=c2)
    ax1.tick_params(axis='y', colors=c1)
    ax1_twin.grid(False), ax1.grid(False)
    # plot hours and tonnes
    c3, c4 = ('#8AB339', '#B35442')
    ax2_twin = plt.twinx(ax2)
    ax2.plot(prod_df.index, prod_df['coal_production']/1_000_000, color=c3)
    ax2.set_ylabel('Short Tones Produced ($10^6$)')
    ax2_twin.plot(prod_df.index, prod_df['active_mine_count'], color=c4)
    ax2_twin.set_ylabel('Active UG Coal Mines')
    # color axis/ticks
    ax2_twin.spines['left'].set_color(c3)
    ax2_twin.spines['right'].set_color(c4)
    ax2_twin.tick_params(axis='y', colors=c4)
    ax2.tick_params(axis='y', colors=c3)
    plt.tight_layout()
    ax2_twin.grid(False), ax2.grid(False)
    plt.subplots_adjust(wspace=0, hspace=.04)
    return plt


def plot_accidents(accident_df, experience_df):
    """Make a plot of employee count and number of coal mines."""
    def plot_experience(ax):
        """ Plot the experience lines on axis"""
        colors = {'75%': '#B8260E', '50%': 'black', '25%': '#2C7EB8'}
        for column, color in colors.items():
            ser = experience_df[column]
            ax.plot(ser.index, ser, color=color, ls='-', label=column)
        ax.legend()
        ax.set_ylabel('Total Experience (years)')
        return ax


    plt.clf()
    # define plot colors
    c1, c2 = ("#176EFF", '#FF4124')
    # plot production and active mine count
    hour_normed = accident_df[('hours_worked', 'injury')] * 1_000_000
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.5, 7), sharex=True)
    ax1.set_ylabel('GC Injuries per $10^6$ Hours')
    ax1.plot(hour_normed.index, hour_normed, color=c1)
    plot_experience(ax2)
    ax2.set_xlabel('Date')
    plt.subplots_adjust(wspace=0, hspace=.04)
    return plt


def plot_mining_method(accidents_df):
    """
    Plot the mining method related to the injuries
    """
    # get df of UG coal GC accidents
    df = accidents_df[is_ug_gc_accidents(accidents_df)]
    # separate longwall and cm
    lw = aggregate_injuries(df, ug_mining_method='Longwall')
    cm = aggregate_injuries(df, ug_mining_method='Continuous Mining')
    # plot
    fig, ax1 = plt.subplots(1, 1, figsize=(5.5, 3.5),)
    ax1.plot(lw.index, lw, label='longwall')
    ax1.plot(cm.index, cm, label='cont. miner')
    ax1.legend(title='Mining Method', fancybox=True)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('GC Injuries Per Quarter')
    return plt


def plot_region(accident_df, mines_df, production_df):
    """Plot the number of mines and gc accidents by region """
    def _get_regional_accidents(accident_df, mines_df):
        # get east/west accidents and aggregate
        mine_ids = mines_df['mine_id'].unique()
        contains_mines = accident_df['mine_id'].isin(mine_ids)
        ug_gc = is_ug_coal(accident_df)
        return accident_df[contains_mines & ug_gc]

    def _get_accident_rate(accident_df, prod_df):
        """Return a series of accident rates."""
        common_dates = sorted(set(accident_df.index) & set(prod_df.index))
        adf, pdf = accident_df.loc[common_dates], prod_df.loc[common_dates]
        return (adf / pdf['hours_worked']) * 1_000_000

    colors = ['red', 'blue']
    is_east = is_eastern_us(mines_df)
    east_ids = mines_df[is_east]['mine_id'].unique()
    east_mines = mines_df[mines_df['mine_id'].isin(east_ids)]
    west_mines = mines_df[~mines_df['mine_id'].isin(east_ids)]
    # get accidents
    east = _get_regional_accidents(accident_df, east_mines)
    west = _get_regional_accidents(accident_df, west_mines)
    east_gc_coal = aggregate_injuries(east)
    west_gc_coal = aggregate_injuries(west)
    # init figs
    plt.clf()
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(5.5, 10.5), sharex=True)
    # plot mines
    east_prod = aggregate_coal_production(production_df, east_mines)
    west_prod = aggregate_coal_production(production_df, west_mines)
    ax1.plot(east_prod.index, east_prod['active_mine_count'], label='east', color=colors[0])
    ax1.plot(west_prod.index, west_prod['active_mine_count'], label='west', color=colors[1])
    ax1.set_ylabel('Active UG Coal Mines')
    # plot accidents
    ax2.plot(east_gc_coal.index, east_gc_coal, label='east', color=colors[0])
    ax2.plot(west_gc_coal.index, west_gc_coal, label='west', color=colors[1])
    ax2.set_ylabel('GC Injuries per Quarter')
    ax2.legend()
    # plot accident rates
    acc_rate_east = _get_accident_rate(east_gc_coal, east_prod)
    acc_rate_west = _get_accident_rate(west_gc_coal, west_prod)
    ax3.plot(acc_rate_east.index, acc_rate_east, label='east', color=colors[0])
    ax3.plot(acc_rate_west.index, acc_rate_west, label='west', color=colors[1])
    ax3.set_xlabel('year')
    ax3.set_ylabel('GC Injuries per $10^6$ Hours')
    # adjust spacing, tighten
    plt.subplots_adjust(wspace=0, hspace=.04)
    plt.tight_layout()
    return plt
