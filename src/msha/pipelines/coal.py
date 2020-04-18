"""
Pipelines for making coal datasets.
"""
import msha.nodes.coal as coal

from kedro.pipeline import node, Pipeline


nodes = [
    node(
        coal.aggregate_accidents,
        name="coal_accidents_agg",
        inputs="pp_accidents",
        outputs="coal_accidents_agg",
    ),
    node(
        coal.aggregate_production,
        name="coal_production_agg",
        inputs=["pp_production", "pp_mines"],
        outputs="coal_production_agg",
    ),
    node(
        coal.ground_control_coal_accidents,
        name="ground_coal_accidents_agg",
        inputs="pp_accidents",
        outputs="coal_ground_control_accidents",
    ),
]


def make_pipeline():
    """Make the coal pipeline. """
    return Pipeline(nodes)
