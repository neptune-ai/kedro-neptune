import math
from typing import (
    Any,
    Dict,
)

import neptune
import pandas as pd
from kedro.pipeline import (
    Pipeline,
    node,
)


# ------ Looking for furthest planet -------
def distances(planets: pd.DataFrame) -> Any:
    planets["Distance from Sun"] = planets["Distance from Sun (106 km)"].apply(lambda row: row * 1e6)

    return planets[["Planet", "Distance from Sun"]]


def furthest(distances_to_planets: pd.DataFrame) -> Dict[str, Any]:
    furthest_planet = distances_to_planets.iloc[distances_to_planets["Distance from Sun"].argmax()]
    return dict(
        furthest_planet_name=furthest_planet.Planet,
        furthest_planet_distance=furthest_planet["Distance from Sun"],
    )


def travel_time(furthest_planet_distance: float, furthest_planet_name: str, travel_speed: float) -> float:
    travel_hours = furthest_planet_distance / travel_speed

    neptune_run = neptune.init_run(
        capture_stdout=False,
        capture_stderr=False,
        capture_hardware_metrics=False,
        source_files=[],
    )

    neptune_run["furthest_planet/name"] = furthest_planet_name
    neptune_run["furthest_planet/travel_hours"] = travel_hours
    neptune_run["furthest_planet/travel_days"] = math.ceil(travel_hours / 24.0)
    neptune_run["furthest_planet/travel_months"] = math.ceil(travel_hours / 720.0)
    neptune_run["furthest_planet/travel_years"] = math.ceil(travel_hours / 720.0 / 365.0)

    neptune_run.sync()

    return travel_hours


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                distances,
                ["planets"],
                "distances_to_planets",
                name="distances",
            ),
            node(
                furthest,
                ["distances_to_planets"],
                dict(
                    furthest_planet_name="furthest_planet_name",
                    furthest_planet_distance="furthest_planet_distance",
                ),
                name="furthest",
            ),
            node(
                travel_time,
                [
                    "furthest_planet_distance",
                    "furthest_planet_name",
                    "params:travel_speed",
                ],
                "travel_hours",
                name="travel_time",
            ),
        ]
    )
