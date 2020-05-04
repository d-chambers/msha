"""
Pipelines for making coal datasets.
"""
import msha.nodes.coal as coal

from kedro.pipeline import node, Pipeline


nodes = [
    node(
        coal.aggregate_coal_accidents_by_classification,
        name="coal_accidents_agg",
        inputs="pp_accidents",
        outputs="coal_accidents_agg",
    ),
    node(
        coal.aggregate_coal_production,
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
    node(
        coal.aggregate_gc_coal_experience_stats,
        name='aggregate_coal_gc_experience',
        inputs='pp_accidents',
        outputs='coal_gc_experience_df',
    ),
    node(
        coal.plot_employees_and_mines,
        name='plot_production',
        outputs='coal_employee_mine_count_plot',
        inputs='coal_production_agg',
    ),

]


def make_pipeline():
    """Make the coal pipeline. """
    return Pipeline(nodes)
