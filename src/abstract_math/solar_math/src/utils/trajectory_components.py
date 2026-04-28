from ..imports import math, mul


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


def tangential_component(
    value: float,
    flight_path_angle_deg: float,
) -> float:
    """
    Tangential component of total velocity/path.
    """
    return mul(
        value,
        math.cos(math.radians(flight_path_angle_deg)),
    )
