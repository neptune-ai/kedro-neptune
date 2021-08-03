import math
from typing import Any, Dict

import fastai.tabular.model
import optuna
from neptune import new as neptune
from neptune.new.integrations.fastai import NeptuneCallback
import neptune.new.integrations.optuna as optuna_utils

import pandas as pd
from kedro.pipeline import Pipeline, node
from fastai.tabular.all import (
    TabularDataLoaders,
    Categorify,
    FillMissing,
    Normalize,
    RandomSplitter,
    range_of,
    tabular_learner,
    SaveModelCallback,
    accuracy,
    TabDataLoader
)


# ------- Number of moons predictor --------
def prepare_dataset(planets: pd.DataFrame):
    planets['Has Many Moons'] = planets['Number of Moons'].apply(lambda moons: moons > 10)

    return TabularDataLoaders.from_df(
        planets,
        procs=[Categorify, FillMissing, Normalize],
        cont_names=[
            'Mass (1024kg)',
            'Diameter (km)'
        ],
        cat_names=[
            'Has Many Moons'
        ],
        y_names='Has Many Moons',
        bs=2,
        splits=RandomSplitter(valid_pct=0.4)(range_of(planets))
    )


def prepare_model(dataset: TabDataLoader) -> Any:
    return tabular_learner(dataset, metrics=accuracy)


class Objective(object):
    def __init__(self,
                 neptune_run: neptune.Run,
                 model: fastai.tabular.model.TabularModel
                 ):
        self.neptune_run = neptune_run
        self.model = model
        self.test_dataset = pd.DataFrame(
                {
                    'Mass (1024kg)': [1000, 1000000],
                    'Diameter (km)': [40, 7000],
                    'Has Many Moons': [False, True]
                },
                index=range(2)
            )

    def __call__(self, trial: optuna.trial.Trial):
        params = {
            "wd": trial.suggest_loguniform("weight_decay", 0.001, 0.1),
        }

        self.model.fit_one_cycle(
            2,
            **params,
            cbs=[
                SaveModelCallback(),
                NeptuneCallback(
                    run=self.neptune_run,
                    base_namespace=f"kedro/moons_classifier/trials/trials/{trial._trial_id}"
                )
            ]
        )

        row, clas, probs = self.model.predict(
            self.test_dataset.iloc[0],
        )

        return probs[0]


def optimize(neptune_metadata: neptune.run.Handler, model: fastai.tabular.model.TabularModel):
    study = optuna.create_study(direction="minimize")
    study.optimize(
        Objective(neptune_run=neptune_metadata._run, model=model),
        n_trials=5,
        callbacks=[
            optuna_utils.NeptuneCallback(
                run=neptune_metadata._run,
                base_namespace='kedro/moons_classifier'
            )
        ]
    )
    neptune_metadata._run.wait()

    return study.best_params


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                prepare_dataset,
                ["planets"],
                'dataset',
                name="prepare_dataset",
            ),
            node(
                prepare_model,
                ["dataset"],
                'model',
                name="prepare_model",
            ),
            node(
                optimize,
                ["neptune_metadata", "model"],
                'best_params',
                name="optimize",
            )
        ]
    )
