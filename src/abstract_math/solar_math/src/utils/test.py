
from __future__ import annotations
from abstract_math import *



result = distance_from_velocity_time_gravity(
    start_altitude=74,
    starting_velocity=17000,
    ending_velocity=25000,
    time_to_target=6.5 * 60,
    time_input_unit="s",
    input_dist_unit="mi",
    input_time_unit="h",
    output_dist_unit="mi",
    output_time_unit="h",
    planet="earth",
    as_radius=False,
)

print(result)
