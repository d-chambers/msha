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
        outputs="coal_gc_accidents_agg",
    ),
    node(
        coal.normalized_ground_control_coal_accidents,
        name="normalized accidents",
        inputs=["coal_gc_accidents_agg", "coal_production_agg"],
        outputs="coal_gc_accidents_normalized_agg",
    ),
]


def make_pipeline():
    """Make the coal pipeline. """
    return Pipeline(nodes)
