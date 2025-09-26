# src/utils/escape_velocity.py
from ..imports import math, mul, div, add
from ..constants import (
    DEFAULT_UNITS,
    DEFAULT_TIME,
    DEFAULT_PLANET,
    DEFAULT_START_ALTITUDE,
    DEFAULT_AS_RADIUS
    )
from ..constants.planet_constants import get_body,get_R_mu
from ..constants.distance_constants import dconvert,get_target_distance,get_normalized_distance
from ..constants.time_constants import get_time_unit_conversions, normalize_time_unit, seconds_per
from .velocity_utils import normalized_velocity_conversioin
def get_r_m(planet: str = DEFAULT_PLANET,start_altitude: float = DEFAULT_START_ALTITUDE,input_units: str = DEFAULT_UNITS,as_radius:bool = DEFAULT_AS_RADIUS):
    R,mu = get_R_mu(planet=planet)
    r_m = dconvert(start_altitude, input_units, DEFAULT_UNITS)
    # Determine radius from center in meters
    if not as_radius:
        r_m = add(R, r_m)
    if r_m <= 0:
        return {"ok": False, "error": "computed radius is non-positive"}
    return r_m
def get_vesc_mps(
    planet: str = DEFAULT_PLANET,
    start_altitude: float = DEFAULT_START_ALTITUDE,
    input_units: str = DEFAULT_UNITS,
    as_radius:bool = DEFAULT_AS_RADIUS
    ):
    R,mu = get_R_mu(planet=planet)
    r_m = get_r_m(planet=planet,start_altitude=start_altitude,input_units=input_units,as_radius=as_radius)
    vesc_mps = math.sqrt(mul(2.0, div(mu, r_m)))
    return vesc_mps



def get_normalized_starting_velocity(
    start_altitude: float = None, 
    starting_velocity: float = None, 
    input_units: str = DEFAULT_UNITS,    # distance part of starting_velocity & start_distance
    input_time: str = DEFAULT_TIME,          # time part of starting_velocity
    output_units: str = DEFAULT_UNITS,
    output_time: str = DEFAULT_TIME,
    planet: str = DEFAULT_PLANET
    ):
    start_altitude = start_altitude or 0
    if starting_velocity == None:
        starting_velocity = escape_velocity_at(planet=planet,
                                               start_altitude=start_altitude,
                                               input_time=input_time,
                                               input_units=input_units,
                                               output_time=input_time,
                                               output_units=input_units
                                               )
    return normalized_velocity_conversioin(
        velocity=starting_velocity,
        input_time=input_time,
        input_units=input_units
        )

def escape_velocity_at(
    planet: str = DEFAULT_PLANET,
    start_altitude: float = DEFAULT_START_ALTITUDE,
    *,
    input_time: str = DEFAULT_TIME,     # how to interpret `distance`
    input_units: str = DEFAULT_UNITS,     # how to interpret `distance`
    output_units: str = DEFAULT_UNITS,    # distance unit for the *speed*
    output_time: str = DEFAULT_TIME,          # time unit for the *speed*
    as_radius: bool = DEFAULT_AS_RADIUS          # False => `distance` is altitude above surface; True => radius from center
) -> dict:
    """
    Compute v_escape at a given location around `planet`.

    Args:
        planet: body name (must exist in PLANETS)
        start_altitude: if as_radius=False => altitude above surface; if as_radius=True => radius from center
        input_units: units of `distance`
        output_units: distance unit of the returned speed
        output_time: time unit of the returned speed ('s'|'min'|'h' etc.)
        as_radius: interpret `distance` as radius-from-center when True

    Returns:
        {
          "ok": True,
          "planet": str,
          "radius_from_center": <float in output_units>,
          "v_escape": <float in output_units/output_time>,
          "v_escape_mps": <float in m/s>,
          "units": {"distance": output_units, "time": output_time}
        }
    """
    if not (isinstance(start_altitude, (int, float)) and math.isfinite(start_altitude) and start_altitude >= 0):
        return {"ok": False, "error": "distance must be a non-negative number"}
    R,mu = get_R_mu(planet=planet)
    # v_esc (m/s)
    r_m = get_r_m(planet=planet,start_altitude=start_altitude,input_units=input_units,as_radius=as_radius)
    vesc_mps = get_vesc_mps(planet=planet,start_altitude=start_altitude,input_units=input_units,as_radius=as_radius)
    # Convert speed to <output_units>/<output_time>
    vesc_units_per_time = dconvert(vesc_mps, DEFAULT_UNITS, output_units)
    time_per = seconds_per(output_time)         # seconds per 1 output_time
    vesc_out = mul(vesc_units_per_time, time_per)  # <output_units>/<output_time>
    # Also return the radius in output_units for convenience
    r_out = dconvert(r_m, DEFAULT_UNITS, output_units)

    return {
        "ok": True,
        "planet": planet,
        "radius_from_center": r_out,
        "v_escape": vesc_out,
        "v_escape_mps": vesc_mps,
        "units": {"distance": output_units, "time": output_time}
    }
