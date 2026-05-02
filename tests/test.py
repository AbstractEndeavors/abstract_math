from __future__ import annotations
from imports import *
planet= "earth"
INIT_VELOCITY = 17900
INIT_ALTITUDE = 74
SATURN_V_TARGET_VELOCITY = 24200
SATURN_V_TIME_TO_TARGET = 6.5
DISTANCE_TO_MOON=238855
FLIGHT_PATH_ANGLE_DEG = 15


burn = distance_from_velocity_time_gravity(
    start_altitude=INIT_ALTITUDE,
    starting_velocity=INIT_VELOCITY,
    ending_velocity=SATURN_V_TARGET_VELOCITY,
    time_to_target=SATURN_V_TIME_TO_TARGET,
    time_input_unit="min",
    input_dist_unit="mi",
    input_time_unit="h",
    output_dist_unit="mi",
    output_time_unit="h",
    planet=planet,
    as_radius=False,
)
burn_path_distance = burn["distance_traveled"]

altitude_gain = radial_component(
    burn_path_distance,
    flight_path_angle_deg=FLIGHT_PATH_ANGLE_DEG,
)

start_altitude = INIT_ALTITUDE + altitude_gain
input(start_altitude)
result = radial_travel(
    start_altitude=start_altitude,
    starting_velocity=SATURN_V_TARGET_VELOCITY,
    target_distance=DISTANCE_TO_MOON,
    flight_path_angle_deg=FLIGHT_PATH_ANGLE_DEG,
    input_dist_unit="mi",
    input_time_unit="h",
    output_dist_unit="mi",
    output_time_unit="h",
    planet="earth",
)

input(result)

##input(radial_travel('earth',output_dist_unit='mi',output_time_unit='hr'))
