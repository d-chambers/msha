"""
Injuries for metal, non-metal (ie not coal) underground mines.
"""

import matplotlib.pyplot as plt
import pandas as pd
from msha.constants import GROUND_CONTROL_CLASSIFICATIONS
from msha.constants import NON_INJURY_DEGREES
from msha.core import (
    normalize_injuries,
    create_normalizer_df,
)
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
plt.style.use(["bmh"])


def get_ug_mnm_mines(mines, prod_df):
    """Filter dataframe to only include UG metal/non metal"""
    con1 = mines["primary_canvass"] != "Coal"
    con2 = mines["current_mine_type"] == "Underground"
    mnm_mines = mines[con1 & con2]
    # get minew which have some reported hours worked
    prod_con1 = prod_df["mine_id"].isin(mnm_mines["mine_id"])
    is_underground = prod_df["subunit"] == "UNDERGROUND"
    sub_prod = prod_df[prod_con1 & is_underground]
    prod_gb = sub_prod.groupby("mine_id")
    has_hours = prod_gb["hours_worked"].sum() > 0
    out = mnm_mines[mnm_mines["mine_id"].isin(has_hours.index)]
    return out


def get_ug_mnm_prod(prod, mines):
    """Return production and mine dfs that are UG metal/non-metal"""
    con1 = prod["mine_id"].isin(mines["mine_id"])
    con2 = prod["subunit"] == "UNDERGROUND"
    # ensure some hours were worked
    con3 = (prod["hours_worked"] > 0) | (prod["employee_count"] > 0)
    return prod[con1 & con2 & con3]


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
    # join commodity to injury
    comod = mnm_mines[["mine_id", "primary_canvass"]]
    inj_with_comod = pd.merge(injuries, comod, on="mine_id")
    prod_with_comod = pd.merge(prod, comod, on="mine_id")

    grouper = pd.Grouper(key="date", freq="Y")
    # now init mine count plot and injury plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.5, 7), sharex=True)
    for comod_name in comod["primary_canvass"].unique():
        if comod_name == "nan" or pd.isnull(comod_name):
            continue
        inj = inj_with_comod[inj_with_comod["primary_canvass"] == comod_name]
        inj = inj[inj["date"] < "2020-01-01"]
        pro = prod_with_comod[prod_with_comod["primary_canvass"] == comod_name]
        # remoce duplicate mine entries for each year
        pro["year"] = pro["date"].dt.year
        pro = pro.drop_duplicates(["year", "mine_id"])
        mine_count = pro.groupby(grouper).size()
        miner_count = pro.groupby(grouper)["employee_count"].sum()
        inj_count = inj.groupby(grouper).size()
        ax2.plot(miner_count.index, miner_count.values, label=comod_name)
        ax1.plot(inj_count.index, inj_count.values, label=comod_name)

    ax2.set_xlabel("Year")
    ax2.set_ylabel("UG MNM Miners")
    ax1.set_ylabel("GC Injuries per Year")
    ax1.legend()
    plt.tight_layout()
    plt.subplots_adjust(wspace=0, hspace=0.04)
    return plt


def plot_by_state(production, mines, accidents, num_states=6):
    """Plot a yearly histogram of miners by state. """

    def get_injuries_and_employees_per_year(mnm_mines, prod, injuries):
        """Get employees and injuries by state."""
        comod = mnm_mines[["mine_id", "primary_canvass", "state"]]
        prod_with_comod = pd.merge(prod.drop(columns="state"), comod, on="mine_id")
        prod_with_comod["year"] = prod_with_comod["date"].dt.year
        gcols = ["primary_canvass", "year", "state"]

        # get av num employees per year
        gr = prod_with_comod.groupby(["mine_id", "year", "primary_canvass", "state"])
        emp_count_year = gr["employee_count"].mean().reset_index()
        employee_count = emp_count_year.groupby(gcols)["employee_count"].sum().round()
        hrs_worked = gr["hours_worked"].mean().reset_index()
        hrs_worked_year = hrs_worked.groupby(gcols)["hours_worked"].sum().round()

        # now get injuries
        injs = pd.merge(injuries, comod, on="mine_id")
        injs["year"] = injs["date"].dt.year
        inj_df = injs.groupby(gcols).size()
        inj_df.name = "injuries"

        out = (
            pd.concat([inj_df, employee_count, hrs_worked_year], axis=1)
            .fillna(0)
            .reset_index()
        )
        out["injury_rate"] = (out["injuries"] / out["hours_worked"]) * 1_000_000
        return out

    def get_top_states(df):
        """Filter the datafame to only include top n states by worker count."""
        states_counts = (
            sub_df.groupby(["state"])["employee_count"]
            .sum()
            .sort_values(ascending=False)
        )
        top_n = states_counts.index[:num_states]
        filtered = df[df["state"].isin(top_n)]
        ratios = {}
        for name in ["employee_count", "injuries"]:
            ratios[name] = filtered[name].sum() / df[name].sum()
        return filtered, ratios

    def _pivot(df):
        """Pivot out employee count and injuries."""
        emps = df.pivot(index="state", columns="year", values="employee_count")
        injs = df.pivot(index="state", columns="year", values="injuries")
        inj_rate = df.pivot(index="state", columns="year", values="injury_rate")
        return emps, injs, inj_rate

    def _plot_histogram(ax, piv, color_key, show_legend=True):
        """Plot a histograme of employee count by state. """
        # sort states by size
        piv = piv.loc[list(color_key)]
        states = piv.index
        for num, state in enumerate(piv.index):
            ser = piv.loc[state]
            # get bottom
            if num == 0:
                bottom = None
            else:
                previous_states = states[:num]
                bottom = piv.loc[previous_states].sum(axis=0).values
            ax.bar(
                ser.index.values,
                ser.values,
                bottom=bottom,
                label=state,
                color=color_key[state],
            )
        if show_legend:
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(reversed(handles), reversed(labels), title='State', loc=2)

        return ax

    def _get_legend_colors(emp):
        """Get legend colors by employee count."""
        state_sum = emp.sum(axis=1).sort_values(ascending=False)
        cm = plt.get_cmap("tab20c")
        out = {}
        for num, state in enumerate(state_sum.index):
            out[state] = cm(num / len(state_sum))
        return out

    def _plot_injury_rates(rate_ax, inj_rate, color_key):
        """plot the injury rates."""
        for state, color in color_key.items():
            ser = inj_rate.loc[state]
            rate_ax.plot(ser.index, ser.values, color=color)

    def _plot(sub_axes, emp, inj, inj_rate, canvas, ratios):
        """ perform plotting."""
        # get legend colors
        color_key = _get_legend_colors(emp)
        # create stacked histogram
        employee_ax, injury_ax, rate_ax = sub_axes
        _plot_histogram(employee_ax, emp, color_key, show_legend=True)
        _plot_histogram(injury_ax, inj, color_key, show_legend=False)
        _plot_injury_rates(rate_ax, inj_rate, color_key)

        # set titles
        emp_percent = f"{int(ratios['employee_count'] * 100):d}"
        inj_percent = f"{int(ratios['injuries'] * 100):d}"

        if canvas == "Metal":
            employee_ax.set_ylabel(f"UG Miners ({emp_percent}%)")
            injury_ax.set_ylabel(f"Injuries ({inj_percent}%)")
            rate_ax.set_ylabel("GC Injures per $10^6$ Hours")

    mnm_mines = get_ug_mnm_mines(mines, production)
    prod = get_ug_mnm_prod(production, mnm_mines)
    injuries = get_ug_mnm_gc_injury(accidents, mnm_mines)

    # Get average employees per year (by state)
    df = get_injuries_and_employees_per_year(mnm_mines, prod, injuries)

    # init plot and axis
    fig, axes = plt.subplots(3, 3, figsize=(16, 12), sharex=True)

    for num, (canvas, sub_df) in enumerate(df.groupby("primary_canvass")):
        # find top n states
        filt_df, ratios = get_top_states(sub_df)
        # pivot out injuries and employee counts (year as col state as row)
        emp, inj, inj_rate = _pivot(filt_df)
        sub_axes = axes[:, num]
        _plot(sub_axes, emp, inj, inj_rate, canvas, ratios)

        # plt.tight_layout()
    # plt.subplots_adjust(wspace=0.15, hspace=0.15)
    plt.tight_layout(h_pad=0.35, w_pad=0.15)
    return plt
