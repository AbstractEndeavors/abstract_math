from __future__ import annotations
from imports import *
FLIGHT_PATH_ANGLE_DEG = 1.72

def radial_component(
    value: float,
    flight_path_angle_deg: float,
) -> float:
    """
    Convert total path/velocity value into radial component.

    angle convention:
        0 deg  = tangential / horizontal
        90 deg = radial outward

    Applies to both:
        radial_velocity = total_velocity * sin(angle)
        radial_gain     = path_distance  * sin(angle)
    """
    return mul(
        value,
        math.sin(math.radians(flight_path_angle_deg)),
    )
burn_path_distance = 2450
angle = 90
altitude_gain = radial_component(
    burn_path_distance,
    flight_path_angle_deg=FLIGHT_PATH_ANGLE_DEG,
)
altitude_gain = input(altitude_gain)
