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

from msha.constants import NON_INJURY_DEGREES, DEGREE_MAP, DEGREE_ORDER
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

register_matplotlib_converters()
plt.style.use(["bmh"])


def get_ug_mnm_mines_prod(prod, mines):
    """Return production and mine dfs that are UG metal/non-metal"""



def is_ug_mnm_injury(accidents):
    """Return a dataframe of injuries in mnm underground mines. """


def plot_mnm_summary(accident, production, mines):
    """Make a summary plot of mnm mines."""


