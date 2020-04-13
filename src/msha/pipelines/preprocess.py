"""
The pipelines used in
"""
from kedro.pipeline import node, Pipeline

from msha.nodes.preprocess import (
    dummy_download,
    preproc_accidents,
    preproce_mines,
    preproce_production,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=dummy_download,
                inputs=[],
                outputs="msha_accidents",
                name="download accidents",
            ),
            node(
                func=dummy_download,
                inputs=[],
                outputs="msha_mines",
                name="download mines",
            ),
            node(
                func=dummy_download,
                inputs=[],
                outputs="msha_production",
                name="download productions",
            ),
            node(
                func=preproc_accidents,
                inputs="msha_accidents",
                outputs="accidents_preproc",
                name="pp_accidents",
            ),
            node(
                func=preproce_mines,
                inputs="msha_mines",
                outputs="mines_preproc",
                name="pp_mines",
            ),
            node(
                func=preproce_production,
                inputs="msha_production",
                outputs="production_preproc",
                name="preproc_production",
            ),
        ]
    )
