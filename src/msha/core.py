"""
Core functionality for MSHA
"""
import numpy as np
import pandas as pd

from msha.constants import (
    NON_INJURY_DEGREES,
    SEVERE_INJURY_DEGREES,
    GROUND_CONTROL_CLASSIFICATIONS,
    EASTERN_STATE_CODES,
    ROCKBURSTY_WORDS,
    STRICTLY_ROCKBURST_WORDS,
    THINGS_THAT_BURST,
)

from sklearn.linear_model import LinearRegression

import spacy

nlp = spacy.load("en_core_web_sm")
bursty_set = set(ROCKBURSTY_WORDS)


def create_normalizer_df(prod_df, mines_df=None, freq="q"):
    """
    Create an aggregated dataframe of mine production/labor stats.

    Will include columns such as hours worked, employees, active mines, etc.
    These are useful for normalizing accident rates.

    Parameters
    ----------
    prod_df
        A dataframe of mine_id and production stats
    mines_df
        The dataframe containing the mine info.

    Returns
    -------
    A dataframe of mine stats for

    """
    if mines_df is not None:
        mine_ids = mines_df["mine_id"].unique()
        prod_df = prod_df[prod_df["mine_id"].isin(mine_ids)]
    # remove columns with no employees or hours worked
    has_hours = prod_df["hours_worked"] > 0
    has_employees = prod_df["employee_count"] > 0
    prod_df = prod_df[has_hours & has_employees]
    # group by quarter, get stats, employee count,
    grouper = pd.Grouper(key="date", freq=freq)
    cols = ["employee_count", "hours_worked", "coal_production"]
    gb = prod_df.groupby(grouper)
    out = gb[cols].sum()
    # add number of active mines
    out["active_mine_count"] = gb["mine_id"].unique().apply(lambda x: len(x))
    out["no_normalization"] = 1
    return out


def aggregate_columns(df, column, freq="q"):
    """Aggregate columns by """
    grouper = pd.Grouper(key="date", freq=freq)
    # only include accidents
    gr = df.groupby(grouper)[column]
    counts = gr.value_counts()
    counts.name = "count"
    piv_kwargs = dict(index="date", columns=column, values="count")
    piv = counts.reset_index().pivot(**piv_kwargs).fillna(0.0).astype(int)
    return piv


def aggregate_injuries(df, freq="q"):
    """Aggregate injuries for each quarter by classification."""
    column = "degree_injury"
    grouper = pd.Grouper(key="date", freq=freq)
    # only include accidents
    df = df[df[column] != "ACCIDENT ONLY"]
    aggs = aggregate_columns(df, column=column, freq=freq)
    return aggs.sum(axis=1)


def aggregate_descriptive_stats(df, column, freq="q"):
    """Aggregate a dataframe by quarter for one columns descriptive stats."""
    grouper = pd.Grouper(key="date", freq=freq)
    out = df.groupby(grouper)[column].describe()
    return out


def normalize_injuries(accident_df, prod_df, mine_df=None, freq="q") -> pd.DataFrame:
    """
    Normalize accidents by each column in norm_df.

    Parameters
    ----------
    accident_df
        A dataframe with aggregated accidents, grouped by quarter.
    prod_df
        A dataframe with normalization denominator, grouped by quarter.
        Often contains number of mines, hours worked, coal production, etc.

    Returns
    -------
    A multi-index column df with the first level being norm_df columns
    and the second level being accident_df columns.
    """
    acc_ag = aggregate_injuries(accident_df, freq=freq)
    norm = create_normalizer_df(prod_df, mines_df=mine_df, freq=freq)
    # assign a columns of one for no normalizations
    # norm["no_normalization"] = 1
    # trim both dfs down to match indicies
    # new_dates = sorted(set(accident_df.index) & set(prod_df.index))
    return (acc_ag / norm.T).T


def is_ug_coal(df):
    """ Return a bool series indicating if each row is underground coal."""
    assert {"is_underground", "is_coal"}.issubset(set(df.columns))
    return df["is_underground"] & df["is_coal"]


def is_ground_control(df):
    """
    Return a bool series indicating if the accident is ground control related.
    """
    return df["classification"].isin(GROUND_CONTROL_CLASSIFICATIONS)


def is_eastern_us(df):
    """Return a series indicating if the mine is located east of missipi"""
    return df["state"].isin(set(EASTERN_STATE_CODES))


def _is_bursty(nar_str):
    """Parse a narrative string"""

    preproc = nar_str.replace("(", "").replace(")", "").lower()
    # First check if one of the strictly rockburst words is used
    has_bursty_word = any([x in preproc for x in STRICTLY_ROCKBURST_WORDS])
    if has_bursty_word:
        return True
    # if not use spacy to parse
    doc = nlp(preproc)
    # if any of the rockbursty words are used as Nouns return True
    nouns = {str(x).lower() for x in doc if x.pos_ in {"NOUN", "PROPN"}}
    if nouns & bursty_set:
        return True
    # Try to determine if any of the bursty words are used as verbs
    can_burst_tokens = [x for x in doc if str(x) in THINGS_THAT_BURST]
    for token in can_burst_tokens:
        isnoun = token.pos_ in {"NOUN", "PROPN"}
        if str(token.head) in ROCKBURSTY_WORDS and isnoun:
            return True

    bursty_tokens = [x for x in doc if str(x) in ROCKBURSTY_WORDS]
    for token in bursty_tokens:
        if token.pos_ == "VERB":
            if (
                str(token.head) in THINGS_THAT_BURST
            ):  #  or str(token.head) in ROCKBURSTY_WORDS:
                # if str(token.head) in THINGS_THAT_BURST or str(token.head) in ROCKBURSTY_WORDS

                return True
    return False


def probably_burst(df):
    """return a series indicating if the accidents are likely 'rockbursty' """

    is_bumpy = df["narrative"].map(_is_bursty)
    return is_bumpy


# --- SKlearn stuff


def select_k_best_regression(
    feature_df, target, k=4, regressor=LinearRegression, **kwargs
):
    """
    Get the k best features for prediction.

    Parameters
    ----------
    feature_df
        The features
    target
        The target
    k
        The number of features to predict
    regressor
        A scikit learn regressor. Default is linear regression.

    kwargs are passed to the regressor.

    Returns
    -------
    A dataframe with the selected features.
    """

    def get_best_score(current, candidates):
        """Get the name of the next best feature"""
        # iterate each unused feature and track improvements to score
        scores = {}
        for name, series in candidates.iteritems():
            cur = np.atleast_2d(current.values)
            can = series.values[..., np.newaxis]
            X = np.hstack([cur, can])
            reg = regressor(**kwargs).fit(X, target.values)
            scores[name] = np.mean(abs(reg.predict(X) - target.values))
        return pd.Series(scores).argmin()

    selected = []
    while len(selected) < k:
        current = feature_df[selected]
        candidates = feature_df.drop(columns=selected)
        # bail out if not enough features remain
        if not len(candidates.columns):
            break
        name = get_best_score(current, candidates)
        selected.append(name)
    return feature_df[selected]


if __name__ == "__main__":
    bad = "While bolting top piece of coal rock fell and bounced off rt rib and back."
    test_str = "Employee was operating the shear on the longwall when a rock fell out of the roof on the face side of the shear and bounced off top of the shear, landing on employee's leg and foot causing fracture to ankle"
    breakpoint()
    _is_bursty(test_str)
