"""
Pipelines for making coal datasets.
"""
import msha.nodes.metal_non_metal as mnm

from kedro.pipeline import node, Pipeline


nodes = [
    node(
        mnm.plot_mnm_summary,
        name="plot_mnm_summary",
        outputs="mnm_summary_plot",
        inputs=["pp_production", "pp_accidents", "pp_mines"],
    ),
]


def make_pipeline():
    """Make the coal pipeline. """
    return Pipeline(nodes)
