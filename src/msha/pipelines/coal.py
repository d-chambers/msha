"""
Pipelines for making coal datasets.
"""
import msha.core
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
        inputs=['coal_production_agg', 'coal_gc_accidents_normalized_agg'],
    ),
    node(
        coal.plot_accidents,
        name='plot_accidents',
        outputs='coal_accidents_plot',
        inputs=['coal_gc_accidents_normalized_agg', 'coal_gc_experience_df'],
    ),
    node(
        coal.plot_mining_method,
        name='plot_mining_method',
        outputs='coal_mining_method_plot',
        inputs='pp_accidents',
    ),
    node(
        coal.plot_region,
        name='plot_region',
        outputs='regional_gc_accidents_plot',
        inputs=['pp_accidents', 'pp_mines', 'pp_production'],
    ),
    node(
        coal.plot_employee_number_histograms,
        name='plot_employee_number',
        outputs='employee_numbers',
        inputs=['pp_production', 'pp_mines'],
    ),
    node(
        coal.plot_accident_rates_by_size,
        name='plot_accident_rates_by_size',
        outputs='accident_rate_by_size',
        inputs=['pp_production', 'pp_mines', 'pp_accidents'],
    ),
]


def make_pipeline():
    """Make the coal pipeline. """
    return Pipeline(nodes)
