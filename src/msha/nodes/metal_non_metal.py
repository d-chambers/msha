"""
Injuries for metal, non-metal (ie not coal) underground mines.
"""
import datetime
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
    GROUND_CONTROL_CLASSIFICATIONS,
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
)

from msha.constants import NON_INJURY_DEGREES

register_matplotlib_converters()
plt.style.use(["bmh"])

def get_ug_mnm_mines(mines, prod_df):
    """Filter dataframe to only include UG metal/non metal"""
    con1 = mines['primary_canvass'] != 'Coal'
    con2 = mines['current_mine_type'] == 'Underground'
    mnm_mines = mines[con1 & con2]
    # get minew which have some reported hours worked
    prod_con1 =  prod_df['mine_id'].isin(mnm_mines['mine_id'])
    is_underground = prod_df['subunit'] == 'UNDERGROUND'
    sub_prod = prod_df[prod_con1 & is_underground]
    prod_gb = sub_prod.groupby('mine_id')
    has_hours = prod_gb['hours_worked'].sum() > 0
    out = mnm_mines[mnm_mines['mine_id'].isin(has_hours.index)]
    return out


def get_ug_mnm_prod(prod, mines):
    """Return production and mine dfs that are UG metal/non-metal"""
    con1 = prod["mine_id"].isin(mines["mine_id"])
    con2 = prod["subunit"] == "UNDERGROUND"
    return prod[con1 & con2]


def get_ug_mnm_gc_injury(accidents, mines):
    """Return a dataframe of injuries in mnm underground mines. """
    # first filter to mines
    con1 = accidents["mine_id"].isin(mines["mine_id"])
    con2 = accidents["is_underground"]
    con3 = ~accidents["degree_injury"].isin(NON_INJURY_DEGREES)
    con4 = accidents["classification"].isin(GROUND_CONTROL_CLASSIFICATIONS)
    return accidents[con1 & con2 & con3 & con4]


def get_quarterly_gold_price(gold_price_monthly):
    """Gete quarterly gold price"""
    df = gold_price_monthly
    df.columns = [x.lower() for x in df.columns]
    grouper = pd.Grouper(freq="q", key="date")
    out = df.groupby(grouper).mean()
    return out


def plot_mnm_summary(production, accidents, mines, gold_price):
    """Make a summary plot of mnm mines."""
    mnm_mines = get_ug_mnm_mines(mines, production)
    prod = get_ug_mnm_prod(production, mnm_mines)
    injuries = get_ug_mnm_gc_injury(accidents, mnm_mines)
    breakpoint()
    norm = create_normalizer_df(prod, mines_df=mnm_mines)
    injuries_normed = normalize_injuries(injuries, prod)
    gp = gold_price.loc[norm.index]



    plt.clf()
    # define plot colors
    c1, c2 = ("#176EFF", "#FF4124")
    # plot production and active mine count
    injuries_total = injuries_normed["no_normalization"]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.5, 7), sharex=True)
    # ax1.set_xlabel("Date")
    ax1.set_ylabel("Employees ($10^3$)")
    ax1.plot(norm.index, norm["employee_count"] / 1_000, color=c1)
    ax1_twin = plt.twinx(ax1)
    ax1_twin.plot(injuries_total.index, injuries_total, color=c2)
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
    ax2.plot(norm.index, norm["active_mine_count"], color=c3)
    ax2.set_ylabel("Active UG Metal/Non Metal Mines")

    ax2_twin.plot(gp.index, gp.values, color=c4)
    ax2_twin.set_ylabel("Gold Price (USD/oz)")
    ax2.set_xlabel("Year")
    # color axis/ticks
    ax2_twin.spines["left"].set_color(c3)
    ax2_twin.spines["right"].set_color(c4)
    ax2_twin.tick_params(axis="y", colors=c4)
    ax2.tick_params(axis="y", colors=c3)
    ax2_twin.grid(False), ax2.grid(False)

    plt.tight_layout()

    ax2.set_xlabel("Year")
    # color axis/ticks
    ax2.tick_params(axis="y", colors=c3)
    plt.tight_layout()
    plt.subplots_adjust(wspace=0, hspace=0.04)
    return plt


def plot_injuries_by_commodity(production, accidents, mines, gold_price):
    """Plot mine count/injuries by commodity"""
    mnm_mines = get_ug_mnm_mines(mines, production)
    prod = get_ug_mnm_prod(production, mnm_mines)
    injuries = get_ug_mnm_gc_injury(accidents, mnm_mines)
    # join state to injury
    # inj_with_state =
    plt.plot([1,2,3])
    return plt
