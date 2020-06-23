"""
Pipelines for making coal datasets.
"""
import msha.nodes.metal_non_metal as mnm

from kedro.pipeline import node, Pipeline



nodes = [
    node(
        mnm.get_quarterly_gold_price,
        name='get gold price',
        outputs='gold_price',
        inputs='gold_price_monthly',
        ),
    node(
        mnm.plot_mnm_summary,
        name="plot_mnm_summary",
        outputs="mnm_summary_plot",
        inputs=["pp_production", "pp_accidents", "pp_mines", "gold_price"],
    ),
]


def make_pipeline():
    """Make the coal pipeline. """
    return Pipeline(nodes)
