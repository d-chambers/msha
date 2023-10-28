"""
Nodes for calculating aggregated underground coal stats.
"""
import datetime
import pathlib
from contextlib import suppress
from functools import reduce
from operator import iand

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, explained_variance_score

from msha.constants import (
    NON_INJURY_DEGREES,
    DEGREE_MAP,
    DEGREE_ORDER,
    SEVERE_INJURY_DEGREES,
)
from msha.core import (
    normalize_injuries,
    create_normalizer_df,
    aggregate_injuries,
    aggregate_descriptive_stats,
    is_ug_coal,
    is_ground_control,
    is_eastern_us,
    select_k_best_regression,
    aggregate_columns,
    probably_burst,
)

register_matplotlib_converters()
plt.style.use(["bmh"])


def aggregate_injuries(df, freq="q", **kwargs):
    """
    Aggregate injuries.

    kwargs are used to specify values for columns.

    EG ug_mining_method='Longwall' will select all rows where ug_mining_method
    is equal to 'Longwall'.
    """
    # filter out only accidents (no injuries)
    df = df[df["degree_injury"] != "ACCIDENT ONLY"]
    # filter out non-selected method
    for colname, value in kwargs.items():
        df = df[df[colname] == value]
    grouper = pd.Grouper(key="date", freq=freq)
    size = df.groupby(grouper).size()
    return size


def is_ug_gc_accidents(df, only_injuries=False):
    """Return a dataframe where each row is an ug gc accident."""
    con1 = is_ug_coal(df)
    con2 = is_ground_control(df)
    out = con1 & con2
    if only_injuries:
        out &= ~df["degree_injury"].isin(NON_INJURY_DEGREES)
    return out


def ground_control_coal_accidents(df):
    """Create a dataframe of ground-control related coal accidents."""
    df_sub = df[is_ug_gc_accidents(df)]
    return aggregate_injuries(df_sub, column="degree_injury")


def aggregate_coal_production(prod_df, mines_df):
    """ Aggregate production by quarter. """
    prod, mines = get_ug_coal_prod_and_mines(prod_df, mines_df)
    return create_normalizer_df(prod, mines)


def get_label_size_label(col, columns):
    """ Make nice labels for pandas groups. """
    assert col in columns
    col_count = len(columns)
    col_num = sorted(list(columns)).index(col)
    if col_num == 0:
        return f"< {int(col.right)}"
    elif col_num == col_count - 1:
        return f"> {int(col.left)}"
    return f"({int(col.left)}, {int(col.right)}]"


def get_ug_coal_prod_and_mines(prod_df, mine_df, qbins=4):
    """Return the filtered dfs for production and UG coal."""
    # get a dataframe of just UG coal production
    ug_coal_mines = mine_df[mine_df["is_underground"] & mine_df["is_coal"]]
    df = prod_df[
        prod_df["mine_id"].isin(ug_coal_mines["mine_id"].unique())
        & (prod_df["subunit"] == "UNDERGROUND")
    ]
    # remove mines with zero employees/production
    df = df[(df["coal_production"] > 0) & (df["employee_count"] > 0)]
    # add quant bins
    df["qcount"] = pd.qcut(df["employee_count"], qbins)
    return df, ug_coal_mines


def get_coal_bump_df(accident_df,):
    """Plot the number of bumps and bump-related GCIs each year."""
    injuries = accident_df[is_ug_gc_accidents(accident_df, only_injuries=True)]
    bursty_gci = injuries[probably_burst(injuries)]
    return bursty_gci


# ----- Plotting functions


def plot_employees_and_mines(prod_df, accident_df, mine_df):
    """Make a plot of employee count and number of coal mines."""
    plt.clf()
    acc = accident_df[is_ug_gc_accidents(accident_df)]
    prod, mines = get_ug_coal_prod_and_mines(prod_df, mine_df)
    norm = create_normalizer_df(prod, mines_df=mines)
    injuries_normed = normalize_injuries(acc, prod)

    # define plot colors
    c1, c2 = ("#176EFF", "#FF4124")
    # plot production and active mine count
    injuries = injuries_normed["no_normalization"]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.5, 7), sharex=True)
    # ax1.set_xlabel("Date")
    ax1.set_ylabel("Employees ($10^3$)")
    ax1.plot(norm.index, norm["employee_count"] / 1_000, color=c1)
    ax1_twin = plt.twinx(ax1)
    ax1_twin.plot(injuries.index, injuries, color=c2)
    ax1_twin.set_ylabel("GC Injuries per Quarter")

    # color axis/ticks
    ax1_twin.spines["left"].set_color(c1)
    ax1_twin.spines["right"].set_color(c2)
    ax1_twin.tick_params(axis="y", colors=c2)
    ax1.tick_params(axis="y", colors=c1)
    ax1_twin.grid(False), ax1.grid(False)
    # plot hours and tonnes
    c3, c4 = ("#8AB339", "#B35442")
    ax2_twin = plt.twinx(ax2)
    ax2.plot(norm.index, norm["coal_production"] / 1_000_000, color=c3)
    ax2.set_ylabel("Short Tones Produced ($10^6$)")
    ax2_twin.plot(norm.index, norm["active_mine_count"], color=c4)
    ax2_twin.set_ylabel("Active UG Coal Mines")
    ax2.set_xlabel("Year")
    # color axis/ticks
    ax2_twin.spines["left"].set_color(c3)
    ax2_twin.spines["right"].set_color(c4)
    ax2_twin.tick_params(axis="y", colors=c4)
    ax2.tick_params(axis="y", colors=c3)
    plt.tight_layout()
    ax2_twin.grid(False), ax2.grid(False)
    plt.subplots_adjust(wspace=0, hspace=0.04)
    return plt


def plot_experience_and_accident_rates(prod_df, accident_df, mines_df):
    """Make a plot of employee count and number of coal mines."""

    def plot_experience(ax, experience_df):
        """ Plot the experience lines on axis"""
        colors = {"75%": "#B8260E", "50%": "black", "25%": "#2C7EB8"}
        for column, color in colors.items():
            ser = experience_df[column]
            ax.plot(ser.index, ser, color=color, ls="-", label=column)
        ax.legend()
        ax.set_ylabel("Total Experience (years)")
        return ax

    plt.clf()
    prod, mines = get_ug_coal_prod_and_mines(prod_df, mines_df)
    injuries = accident_df[is_ug_gc_accidents(accident_df, only_injuries=True)]
    normed = normalize_injuries(injuries, prod, mines)
    experience = aggregate_descriptive_stats(injuries, "total_experience")

    # define plot colors
    c1, c2 = ("#176EFF", "#FF4124")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.5, 7), sharex=True)
    ax1.set_ylabel("GC Injuries per $10^6$ Hours")
    ax1.plot(normed.index, normed["hours_worked"] * 1_000_000, color=c1)
    plot_experience(ax2, experience_df=experience)
    ax2.set_xlabel("Date")
    plt.subplots_adjust(wspace=0, hspace=0.04)
    return plt


def plot_mining_method(accidents_df):
    """
    Plot the mining method related to the injuries
    """
    # get df of UG coal GC accidents
    df = accidents_df[is_ug_gc_accidents(accidents_df)]
    # separate longwall and cm
    lw = aggregate_injuries(df, ug_mining_method="Longwall")
    cm = aggregate_injuries(df, ug_mining_method="Continuous Mining")
    # plot
    fig, ax1 = plt.subplots(1, 1, figsize=(5.5, 3.5),)
    ax1.plot(lw.index, lw, label="longwall")
    ax1.plot(cm.index, cm, label="cont. miner")
    ax1.legend(title="Mining Method", fancybox=True)
    ax1.set_xlabel("Year")
    ax1.set_ylabel("GC Injuries Per Quarter")
    return plt


def plot_region(accident_df, mines_df, production_df):
    """Plot the number of mines and gc accidents by region """

    def _get_regional_accidents(accident_df, mines_df):
        # get east/west accidents and aggregate
        mine_ids = mines_df["mine_id"].unique()
        contains_mines = accident_df["mine_id"].isin(mine_ids)
        ug_gc = is_ug_coal(accident_df)
        return accident_df[contains_mines & ug_gc]

    def _get_accident_rate(accident_df, prod_df):
        """Return a series of accident rates."""
        common_dates = sorted(set(accident_df.index) & set(prod_df.index))
        adf, pdf = accident_df.loc[common_dates], prod_df.loc[common_dates]
        return (adf / pdf["hours_worked"]) * 1_000_000

    colors = ["red", "blue"]
    is_east = is_eastern_us(mines_df)
    east_ids = mines_df[is_east]["mine_id"].unique()
    east_mines = mines_df[mines_df["mine_id"].isin(east_ids)]
    west_mines = mines_df[~mines_df["mine_id"].isin(east_ids)]
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
    ax1.plot(
        east_prod.index, east_prod["active_mine_count"], label="east", color=colors[0]
    )
    ax1.plot(
        west_prod.index, west_prod["active_mine_count"], label="west", color=colors[1]
    )
    ax1.set_ylabel("Active UG Coal Mines")
    # plot accidents
    ax2.plot(east_gc_coal.index, east_gc_coal, label="east", color=colors[0])
    ax2.plot(west_gc_coal.index, west_gc_coal, label="west", color=colors[1])
    ax2.set_ylabel("GC Injuries per Quarter")
    ax2.legend()
    # plot accident rates
    acc_rate_east = _get_accident_rate(east_gc_coal, east_prod)
    acc_rate_west = _get_accident_rate(west_gc_coal, west_prod)
    ax3.plot(acc_rate_east.index, acc_rate_east, label="east", color=colors[0])
    ax3.plot(acc_rate_west.index, acc_rate_west, label="west", color=colors[1])
    ax3.set_xlabel("year")
    ax3.set_ylabel("GC Injuries per $10^6$ Hours")
    # adjust spacing, tighten
    plt.subplots_adjust(wspace=0, hspace=0.04)
    plt.tight_layout()
    return plt


def plot_employee_by_mine(prod_df, mine_df):
    """
    Create a histogram of number of mines with their size.
    """

    def _create_year_labels(df):
        """
        Create year labels from index. A number of spaces are added to the end
        in order to maintain uniqueness.
        """
        x_labels = [str(x.year) + " " * (x.quarter - 1) for x in df.index]
        return x_labels

    def _plot_hist(ax, piv):
        x_labels = _create_year_labels(piv)
        reversed_columns = sorted(piv.columns, reverse=True)
        for col_num, col in enumerate(reversed_columns):
            if col_num == 0:
                bottom = None
            else:
                cols_to_include = list(reversed_columns[:col_num])
                bottom = piv[cols_to_include].sum(axis=1).values
            label = get_label_size_label(col, piv.columns)
            ser = piv[col]
            ax.bar(x_labels, ser.values, label=label, bottom=bottom, width=1)
        with suppress(Exception):
            ax.set_xticks(x_labels[::16])
        return ax

    def plot_active_mines_by_employees(ax, prod):
        """Create a plot of active mines binned by employee counts """
        grouper = pd.Grouper(freq="q", key="date")
        out = prod.groupby(grouper)["qcount"].value_counts()
        out.name = "mine_count"
        # pivot out df
        piv_kwargs = dict(index="date", columns="qcount", values="mine_count")
        piv = out.to_frame().reset_index().pivot(**piv_kwargs)
        _plot_hist(ax, piv)
        # set labels
        ax.set_ylabel("Active UG Coal Mines")
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], loc="top right", title="Employee Count")
        return ax

    def plot_employees_by_employer_size(ax, prod):
        """ Plot the number of UG employees by mine size. """
        grouper = pd.Grouper(freq="q", key="date")
        out = prod.groupby([grouper, "qcount"])["employee_count"].sum()
        out.name = "employee_count"
        piv_kwargs = dict(index="date", columns="qcount", values="employee_count")
        piv = out.to_frame().reset_index().pivot(**piv_kwargs) / 1_000
        _plot_hist(ax, piv)
        ax.set_ylabel("UG Coal Miners ($10^3$) ")
        return ax

    # def make_mine_employee_count()

    prod_year = prod_df  # _get_production_by_year(prod_df)
    prod, ug_coal_mines = get_ug_coal_prod_and_mines(prod_year, mine_df)
    # init figures
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 7), sharex=True)
    plot_active_mines_by_employees(ax1, prod)
    plot_employees_by_employer_size(ax2, prod)
    ax2.set_xlabel("Year")

    plt.tight_layout()
    return plt


def plot_accident_rates_by_size(prod_df, mine_df, accidents_df):
    """
    Create a plot of accident rates.
    """

    def _get_mine_year_quarter(df):
        """Get a columns mine_id_year_qt"""
        date = df["date"].dt
        year = date.year.astype(str)
        # quarter = date.quarter.astype(str)
        mine_id = df["mine_id"]
        return mine_id.astype(str) + "." + year

    plt.clf()
    fig, ax1 = plt.subplots(1, 1, figsize=(5.5, 3.5),)
    grouper = pd.Grouper(key="date", freq="y")
    prod_df, mine_df = get_ug_coal_prod_and_mines(prod_df, mine_df)
    prod_df = prod_df.sort_values("qcount")
    prod_df["myq"] = _get_mine_year_quarter(prod_df)
    categories = sorted(prod_df["qcount"].unique())
    # get accidents for UG coal where injuries resulted
    con1 = is_ug_gc_accidents(accidents_df)
    con2 = accidents_df["degree_injury"] != "ACCIDENT ONLY"
    acc_df = accidents_df[con1 & con2]
    acc_df["myq"] = _get_mine_year_quarter(acc_df)
    # first create a dict of categories and prod
    cat = {}
    for category, sub_prod in prod_df.groupby("qcount"):
        cat[category] = sub_prod
    # now iterate categories, starting with the largest, and plot
    for category in sorted(cat, reverse=True):
        sub_prod = cat[category]
        # get injuries associated with this group
        label = get_label_size_label(category, categories)
        df = acc_df[acc_df["myq"].isin(sub_prod["myq"].unique())]
        injuries = df.groupby(grouper).size()
        hours = sub_prod.groupby(grouper)["hours_worked"].sum()
        out = (injuries / hours).fillna(0) * 1_000_000
        ax1.plot(out.index, out, label=label)

    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles[::-1], labels[::-1], loc="top right", title="Employee Count")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("GC Injures per $10^6$ Hours")
    return plt


def plot_predicted_injury_rates(prod_df, accident_df, mines_df):
    """Use simple features to predict accident rates and plot. """

    def get_dates_with_no_nan(df_list):
        """return a sorted list a index which contain no nans in any columns"""
        common_index = reduce(iand, [set(x.index) for x in df_list])

        for df in df_list:
            has_nulls = df[df.isnull().any(axis=1)].index
            for element in has_nulls:
                if element in common_index:
                    common_index.remove(element)
            # out.add(list(df[df.isnull().any(axis=1)].index))
        return sorted(common_index)

    def create_features_df(injuries, prod, norm_df):
        """Create a dataframe of features to predict accident rates."""
        grouper = pd.Grouper(key="date", freq="q")
        # get features from production df
        prod_cols = ["hours_worked", "employee_count", "coal_production"]
        prod_features = prod.groupby(grouper)[prod_cols].sum()
        exp_df = aggregate_descriptive_stats(injuries, "total_experience")
        size_df = aggregate_descriptive_stats(prod, "employee_count")
        # prod_per_hour = prod_features['coal_production'] / prod_features['hours_worked']
        # prod_features['coal_per_hour'] = prod_per_hour
        df_list = [exp_df, size_df, prod_features, norm_df]
        index = get_dates_with_no_nan(df_list)
        hours = prod_features.loc[index]
        exp = exp_df.loc[index]
        size = size_df.loc[index]
        # drop number of accidents info from exp df
        exp = exp.drop(columns="count")
        out = pd.concat([exp, size, hours], keys=["exp", "size", "prod"], axis=1)
        return out

    plt.clf()
    # get features and such
    prod, mines = get_ug_coal_prod_and_mines(prod_df, mines_df)
    injuries = accident_df[is_ug_gc_accidents(accident_df, only_injuries=True)]
    normed = normalize_injuries(injuries, prod, mines)
    # get experience, mine sizes (by employee count) and hours worked
    # combine into a feature dataframe
    feature_df = create_features_df(injuries, prod, normed)
    norm = normed.loc[feature_df.index]
    # get GC injury rate (injuries per 10^6 hours)
    target = norm["hours_worked"] * 1_000_000
    # select the most important features
    select_feats = select_k_best_regression(feature_df, target, k=5, normalize=True,)
    X = select_feats.values
    reg = LinearRegression(normalize=True).fit(X, target.values)
    x_pred = reg.predict(X)
    rmse = mean_squared_error(target.values, x_pred, squared=False)
    explained_var = explained_variance_score(target.values, x_pred,)
    # now plot
    plt.figure(figsize=(5.5, 3.5))
    plt.plot(target.index, target.values, color="b", label="GC injury rate")
    plt.plot(select_feats.index, x_pred, color="r", label="predicted injury rate")
    plt.legend()
    plt.xlabel("Year")
    plt.ylabel("GC Injures per $10^6$ Hours")
    return plt


def plot_gc_injury_severity(prod_df, accident_df, mines_df):
    """Plot the severity of GC injuries a function of time."""

    def plot_injuries(ax, injury_df):
        """Plot the histogram. """
        bottom = pd.Series(data=np.ones(len(injury_df)), index=injury_df.index)
        for label, ser in injury_df.iteritems():
            # ax.bar(ser.index, ser.values, label=label, bottom=bottom, width=300)
            ax.semilogy(ser.index, ser.values, label=label)

            bottom += ser
        ax.set_ylabel("Number of Injuries")
        # ax.set_yscale('log')
        # with suppress(Exception):
        #     ax.set_xticks(x_labels[::16])
        return ax

    plt.clf()
    # get features and such
    # prod, mines = get_ug_coal_prod_and_mines(prod_df, mines_df)
    injuries = accident_df[is_ug_gc_accidents(accident_df, only_injuries=True)]
    injuries["degree"] = injuries["degree_injury"].map(DEGREE_MAP)
    inj = aggregate_columns(injuries, "degree", freq="y")
    # drop current (not complete yet)
    year = datetime.datetime.now().year
    inj = inj.loc[inj.index.year != year][list(DEGREE_ORDER)]
    # init plot and create hist

    fig, ax1 = plt.subplots(1, 1, figsize=(5.5, 3.5),)
    ax1.legend()
    plot_injuries(ax1, inj)
    return fig


def plot_coal_bumps(accident_df, coal_bumps):
    """Plot the number of bumps and bump-related GCIs each year."""
    injuries = accident_df[is_ug_gc_accidents(accident_df, only_injuries=True)]
    non_burst = injuries[~injuries["narrative"].isin(coal_bumps["narrative"])]
    return

    burst_major = coal_bumps["degree_injury"].isin({"FATALITY"}).sum()
    non_burst_major = non_burst["degree_injury"].isin({"FATALITY"}).sum()
    breakpoint()

    merged = pd.merge(assumed_bumps, accident_df, how="left", on="narrative")
    # each bump should be accounted for in accident_df
    assert len(merged) == len(assumed_bumps)
    # test classifying bumps
    # bursty_bumps = probably_burst(assumed_bumps)
    # should_have_found = injuries[injuries['narrative'].isin(assumed_bumps['narrative'])]
    # bursty_gci = injuries[probably_burst(injuries)]

    # write output

    #
    # outstr = '\n\n\n'.join(
    #     [f"{name}::: {x['narrative']}" for name, x in bursty_gci.iterrows()]
    # )
    # path = pathlib.Path('burst_desc.txt')
    # with path.open('w') as fi:
    #     fi.write(outstr)

    breakpoint()

    print(accident_df)
