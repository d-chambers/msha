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


def get_label_size_label(col, col_num, col_count):
    """ Make nice labels for pandas groups. """
    if col_num == 0:
        return f"< {int(col.right)}"
    elif col_num == col_count - 1:
        return f"> {int(col.left)}"
    return f"({int(col.left)}, {int(col.right)}]"


def get_ug_coal_prod_and_mines(prod_df, mine_df):
    """Return the filtered dfs for production and UG coal."""
    # get a dataframe of just UG coal production
    ug_coal_mines = mine_df[mine_df['is_underground'] & mine_df['is_coal']]
    df = prod_df[
        prod_df['mine_id'].isin(ug_coal_mines['mine_id'].unique())
        & (prod_df['subunit'] == 'UNDERGROUND')
        ]
    # remove mines with zero employees/production
    df = df[(df['coal_production'] > 0) & (df['employee_count'])]
    return df, ug_coal_mines


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


def plot_employee_number_histograms(prod_df, mine_df):
    """
    Create a histogram of employees per mine by year.
    """

    plt.clf()
    df, ug_coal_mines = get_ug_coal_prod_and_mines(prod_df, mine_df)
    # get 5 bins of employee count
    df['qcount'] = pd.qcut(df['employee_count'], 4)
    grouper = pd.Grouper(freq='Y', key='date')
    out = df.groupby(grouper)['qcount'].value_counts()
    out.name='count'
    # pivot out df
    piv_kwargs = dict(index="date", columns='qcount', values="count")
    piv = out.to_frame().reset_index().pivot(**piv_kwargs)
    piv_percentage = piv.divide(piv.sum(axis=1), axis=0) * 100
    # now plot
    fig, ax1 = plt.subplots(1, 1, figsize=(5.5, 3.5),)
    dff = piv_percentage
    for col_num in range(len(dff.columns)):
        col = dff.columns[col_num]
        if col_num == 0:
            bottom=None
        else:
            bottom = dff[dff.columns[:col_num]].sum(axis=1).values
        label = get_label_size_label(col, col_num, len(dff.columns))
        ser = dff[col]
        x_labels = ser.index.year
        ax1.bar(x_labels, ser.values, label=label, bottom=bottom)
        ax1.set_xticks(x_labels[::4])
    # set labels
    ax1.set_ylabel('% of UG Coal Mines')
    ax1.set_xlabel('Year')
    # put legend on top
    # box = ax1.get_position()
    # ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    bbox_to_anchor = (.92, .5)
    # Put a legend to the right of the current axis
    ax1.legend(loc='center left', bbox_to_anchor=bbox_to_anchor, title='Employee Count')
    plt.tight_layout()
    return plt


def plot_accident_rates_by_size(prod_df, mine_df, accidents_df):
    """
    Create a plot of accident rates.
    """

    def _get_mine_year_quarter(df):
        """Get a columns mine_id_year_qt"""
        date = df['date'].dt
        year = date.year.astype(str)
        # quarter = date.quarter.astype(str)
        mine_id = df['mine_id']
        return mine_id.astype(str) + '.' + year

    plt.clf()
    fig, ax1 = plt.subplots(1, 1, figsize=(5.5, 3.5),)
    grouper = pd.Grouper(key="date", freq="y")
    prod_df, mine_df = get_ug_coal_prod_and_mines(prod_df, mine_df)
    prod_df['qcount'] = pd.qcut(prod_df['employee_count'], 4)
    prod_df = prod_df.sort_values('qcount')
    prod_df['myq'] = _get_mine_year_quarter(prod_df)
    categories = sorted(prod_df['qcount'].unique())
    # get accidents for UG coal where injuries resulted
    con1 = is_ug_coal(accidents_df)
    con2 = is_ground_control(accidents_df)
    con3 = accidents_df['degree_injury'] != 'ACCIDENT ONLY'
    acc_df = accidents_df[con1 & con2 & con3 ]
    acc_df['myq'] = _get_mine_year_quarter(acc_df)
    for category, sub_prod in prod_df.groupby('qcount'):
        # get injuries associated with this group
        label = get_label_size_label(category, categories.index(category), len(categories))
        df = acc_df[acc_df['myq'].isin(sub_prod['myq'].unique())]
        accidents = df.groupby(grouper).size()
        hours = sub_prod.groupby(grouper)['hours_worked'].sum()
        out = (accidents / hours).fillna(0) * 1_000_000
        ax1.plot(out.index, out, label=label)
    plt.legend(title='Employee Count')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('GC Injures per $10^6$ Hours ')
    return plt

