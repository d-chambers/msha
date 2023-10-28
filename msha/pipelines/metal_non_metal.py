"""
Pipelines for making coal datasets.
"""
import msha.nodes.metal_non_metal as mnm

from kedro.pipeline import node, Pipeline


nodes = [
    node(
        mnm.get_quarterly_gold_price,
        name="get gold price",
        outputs="gold_price",
        inputs="gold_price_monthly",
    ),
    node(
        mnm.plot_mnm_summary,
        name="plot_mnm_summary",
        outputs="mnm_summary_plot",
        inputs=["pp_production", "pp_accidents", "pp_mines", "gold_price"],
    ),
    node(
        mnm.plot_injuries_by_commodity,
        name="plot_commodity",
        outputs="mnm_commodity_plot",
        inputs=["pp_production", "pp_accidents", "pp_mines", "gold_price"],
    ),
    node(
        mnm.plot_by_state,
        name="plot_miners_by_state",
        outputs="mnm_state_plot",
        inputs=["pp_production", "pp_mines", "pp_accidents"],
    ),
]


def make_pipeline():
    """Make the coal pipeline. """
    return Pipeline(nodes)
