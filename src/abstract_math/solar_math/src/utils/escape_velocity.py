# src/utils/escape_velocity.py
from ..imports import math, mul, div, add
from ..constants import (
    DEFAULT_DIST_UNIT,
    DEFAULT_TIME_UNIT,
    DEFAULT_PLANET,
    DEFAULT_START_ALTITUDE,
    DEFAULT_AS_RADIUS,
    get_smallest_unit_string
    )
from ..constants.planet_constants import get_body,get_R_mu,g_at_radius
from ..constants.distance_constants import dconvert,get_target_distance,get_normalized_distance
from ..constants.time_constants import get_time_unit_conversions, normalize_time_unit, seconds_per,tconvert
from .velocity_utils import normalized_velocity_conversion,get_velocity_conversion
def get_r_m(planet: str = DEFAULT_PLANET,start_altitude: float = DEFAULT_START_ALTITUDE,input_dist_unit: str = DEFAULT_DIST_UNIT,as_radius:bool = DEFAULT_AS_RADIUS):
    R,mu = get_R_mu(planet=planet)
    r_m = dconvert(start_altitude, input_dist_unit, DEFAULT_DIST_UNIT)
    # Determine radius from center in meters
    if not as_radius:
        r_m = add(R, r_m)
    if r_m <= 0:
        return {"ok": False, "error": "computed radius is non-positive"}
    return r_m
def get_vesc_mps(
    planet: str = DEFAULT_PLANET,
    start_altitude: float = DEFAULT_START_ALTITUDE,
    input_dist_unit: str = DEFAULT_DIST_UNIT,
    as_radius:bool = DEFAULT_AS_RADIUS
    ):
    R,mu = get_R_mu(planet=planet)
    r_m = get_r_m(planet=planet,start_altitude=start_altitude,input_dist_unit=input_dist_unit,as_radius=as_radius)
    vesc_mps = math.sqrt(mul(2.0, div(mu, r_m)))
    return vesc_mps

def get_normalized_starting_velocity(
    start_altitude: float = None, 
    starting_velocity: float = None, 
    input_dist_unit: str = DEFAULT_DIST_UNIT,    # distance part of starting_velocity & start_distance
    input_time_unit: str = DEFAULT_TIME_UNIT,         # time part of starting_velocity
    output_dist_unit: str = DEFAULT_DIST_UNIT,
    output_time_unit: str = DEFAULT_TIME_UNIT,
    planet: str = DEFAULT_PLANET
    ):
    start_altitude = start_altitude or 0
    if starting_velocity == None:
        starting_velocity = escape_velocity_at(planet=planet,
                                               start_altitude=start_altitude,
                                               input_time_unit=input_time_unit,
                                               input_dist_unit=input_dist_unit,
                                               output_time_unit=output_time_unit,
                                               output_dist_unit=output_dist_unit
                                               )
    return normalized_velocity_conversion(
        velocity=starting_velocity,
        input_time_unit=input_time_unit,
        input_dist_unit=input_dist_unit
        )

def escape_velocity_at(
    planet: str = DEFAULT_PLANET,
    start_altitude: float = DEFAULT_START_ALTITUDE,
    *,
    input_time_unit: str = DEFAULT_TIME_UNIT,     # how to interpret `distance`
    input_dist_unit: str = DEFAULT_DIST_UNIT,     # how to interpret `distance`
    output_dist_unit: str = DEFAULT_DIST_UNIT,    # distance unit for the *speed*
    output_time_unit: str = DEFAULT_TIME_UNIT,          # time unit for the *speed*
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

    r_m = get_r_m(planet=planet,
                  start_altitude=start_altitude,
                  input_dist_unit=input_dist_unit,
                  as_radius=as_radius
                  )
    r_conv = dconvert(r_m, input_dist_unit, output_dist_unit)
    v_escape_mps = get_vesc_mps(
        planet=planet,
        start_altitude=start_altitude,
        input_dist_unit=input_dist_unit,
        as_radius=as_radius
        )
    v_escape = get_velocity_conversion(velocity=v_escape_mps,
                                    input_time_unit= DEFAULT_TIME_UNIT,
                                    input_dist_unit= DEFAULT_DIST_UNIT,
                                    output_dist_unit= output_dist_unit,
                                    output_time_unit= output_time_unit)
    # Convert speed to <output_units>/<output_time>

    # Also return the radius in output_units for convenience
    
    
    g_o_mps = g_at_radius(mu, r_m)
    g_o_conv = get_velocity_conversion(velocity=g_o_mps,
                                    input_time_unit= DEFAULT_TIME_UNIT,
                                    input_dist_unit= DEFAULT_DIST_UNIT,
                                    output_dist_unit= output_dist_unit,
                                    output_time_unit= output_time_unit)
   
    smallest_time_unit = get_smallest_unit_string(output_time_unit)
    smallest_distance_unit = get_smallest_unit_string(output_dist_unit)
    return {
        "ok": True,
        "planet": planet,
        
        "v_escape": round(v_escape,6),
        "v_escape_mps": round(v_escape_mps,6),
        "units": {"distance": output_dist_unit, "time": output_time_unit},
        "r_m":round(r_m,6),
        "r": round(r_conv,6),
        "g_o_mps":round(g_o_mps,6),
        "g_o":round(g_o_conv,6),
        

        "units": {"distance": output_dist_unit, "time": output_time_unit},
        "radius_from_center": f"{round(r_conv,2)} {smallest_distance_unit}",
        "v_escape": f"{round(v_escape,2)} {smallest_distance_unit}/{smallest_time_unit}^2",
        "g_out": f"{round(g_o_conv,2)} {smallest_distance_unit}/{smallest_time_unit}^2",
        "escape_velocity": f"{round(v_escape,2)} {smallest_distance_unit}/{smallest_time_unit}^2"
      
    }
