"""
Pipelines for making coal datasets.
"""
import msha.core
import msha.nodes.coal as coal

from kedro.pipeline import node, Pipeline


nodes = [
    node(
        coal.plot_employees_and_mines,
        name="plot_production",
        outputs="coal_employee_mine_count_plot",
        inputs=["pp_production", "pp_accidents", "pp_mines"],
    ),
    node(
        coal.plot_experience_and_accident_rates,
        name="plot_accidents",
        outputs="coal_accidents_plot",
        inputs=["pp_production", "pp_accidents", "pp_mines"],
    ),
    node(
        coal.plot_mining_method,
        name="plot_mining_method",
        outputs="coal_mining_method_plot",
        inputs="pp_accidents",
    ),
    node(
        coal.plot_region,
        name="plot_region",
        outputs="regional_gc_accidents_plot",
        inputs=["pp_accidents", "pp_mines", "pp_production"],
    ),
    node(
        coal.plot_employee_by_mine,
        name="plot_employee_number",
        outputs="employee_numbers",
        inputs=["pp_production", "pp_mines"],
    ),
    node(
        coal.plot_accident_rates_by_size,
        name="plot_accident_rates_by_size",
        outputs="accident_rate_by_size",
        inputs=["pp_production", "pp_mines", "pp_accidents"],
    ),
    node(
        coal.plot_predicted_injury_rates,
        name="plot_predicted_injury_rates",
        outputs="predicted_injury_rate",
        inputs=["pp_production", "pp_accidents", "pp_mines"],
    ),
    node(
        coal.plot_gc_injury_severity,
        name="plot_injury_severity",
        outputs="injury_severity",
        inputs=["pp_production", "pp_accidents", "pp_mines"],
    ),
]


def make_pipeline():
    """Make the coal pipeline. """
    return Pipeline(nodes)
