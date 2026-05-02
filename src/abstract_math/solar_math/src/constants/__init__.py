# src/constants/__init__.py
from .distance_constants import (
    DISTANCE_CONVERSIONS, ALL_DISTANCE_UNITS,
    normalize_distance_unit, get_distance_unit_conversions,
    _factor, dconvert,DEFAULT_DIST_UNIT,DEFAULT_START_ALTITUDE,
    get_smallest_dist_unit_string
)
from .time_constants import (
    TIME_CONVERSIONS, ALL_TIME_UNITS,
    normalize_time_unit, get_time_unit_conversions,tconvert,
    time_factor, convert_time, seconds_per,DEFAULT_TIME_UNIT,
    get_smallest_time_unit_string
)
from .planet_constants import (
    PLANETS, G, g0, MU_MOON,
    get_planet_vars, planet_radius, planet_diameter,
    full_planet_surface_area, planet_volume, planet_circumference,
    planet_mass, planet_surface_g, escape_velocity,
    earth_radius, earth_diameter, full_earth_surface_area,
    earth_volume, earth_circumference,DEFAULT_PLANET,DEFAULT_AS_RADIUS,
    distance_per_sec_to_mps,hill_radius,soi_radius,gravity_reach
)
from .geometric_constants import (
    pi,
    radius_from_circumference,
    radius_from_diameter,
    radius
    )
def get_smallest_unit_string(unit):
    for key,values in DISTANCE_CONVERSIONS.items():
        if unit in values["strings"]:
            return values["strings"][0]
    for key,values in TIME_CONVERSIONS.items():
        if unit in values["strings"]:
            return values["strings"][0]
    return unit
