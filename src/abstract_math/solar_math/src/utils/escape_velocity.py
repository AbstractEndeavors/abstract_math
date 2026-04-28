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
def distance_from_velocity_time_gravity(
    start_altitude: float = DEFAULT_START_ALTITUDE,
    starting_velocity: float = None,
    ending_velocity: float = None,
    time_to_target: float = None,
    input_dist_unit: str = DEFAULT_DIST_UNIT,
    input_time_unit: str = DEFAULT_TIME_UNIT,
    output_dist_unit: str = DEFAULT_DIST_UNIT,
    output_time_unit: str = DEFAULT_TIME_UNIT,
    time_input_unit: str = DEFAULT_TIME_UNIT,
    planet: str = DEFAULT_PLANET,
    as_radius: bool = DEFAULT_AS_RADIUS,
    steps: int = 10000,
):
    """
    Distance traveled when starting at v0, ending at v1, over time t,
    while gravity changes with radius.

    Assumption:
        applied acceleration is constant
        gravity varies by radius: g(r) = mu / r^2

    Model:
        dr/dt = v
        dv/dt = a_applied - mu / r^2

    The function solves for a_applied that makes final velocity == ending_velocity.
    """
    if starting_velocity is None:
        return {"ok": False, "error": "starting_velocity is required"}

    if ending_velocity is None:
        return {"ok": False, "error": "ending_velocity is required"}

    if time_to_target is None:
        return {"ok": False, "error": "time_to_target is required"}

    if steps <= 0:
        return {"ok": False, "error": "steps must be positive"}

    _R, mu = get_R_mu(planet=planet)

    r0_m = get_r_m(
        planet=planet,
        start_altitude=start_altitude,
        input_dist_unit=input_dist_unit,
        as_radius=as_radius,
    )

    if isinstance(r0_m, dict):
        return r0_m

    v0_mps = get_normalized_starting_velocity(
        start_altitude=start_altitude,
        starting_velocity=starting_velocity,
        input_dist_unit=input_dist_unit,
        input_time_unit=input_time_unit,
        output_dist_unit=DEFAULT_DIST_UNIT,
        output_time_unit=DEFAULT_TIME_UNIT,
        planet=planet,
    )

    v1_target_mps = get_normalized_starting_velocity(
        start_altitude=start_altitude,
        starting_velocity=ending_velocity,
        input_dist_unit=input_dist_unit,
        input_time_unit=input_time_unit,
        output_dist_unit=DEFAULT_DIST_UNIT,
        output_time_unit=DEFAULT_TIME_UNIT,
        planet=planet,
    )

    total_seconds = mul(
        time_to_target,
        seconds_per(time_input_unit),
    )

    if total_seconds <= 0:
        return {"ok": False, "error": "time_to_target must be positive"}

    dt = div(total_seconds, steps)

    def integrate(applied_accel_mps2: float):
        r_m = r0_m
        v_mps = v0_mps

        for _ in range(steps):
            gravity_mps2 = div(mu, mul(r_m, r_m))
            net_accel_mps2 = sub(applied_accel_mps2, gravity_mps2)

            v_mps = add(v_mps, mul(net_accel_mps2, dt))
            r_m = add(r_m, mul(v_mps, dt))

            if r_m <= 0:
                break

        return r_m, v_mps

    gravity_start_mps2 = div(mu, mul(r0_m, r0_m))

    net_accel_guess_mps2 = div(
        sub(v1_target_mps, v0_mps),
        total_seconds,
    )

    applied_guess_mps2 = add(
        net_accel_guess_mps2,
        gravity_start_mps2,
    )

    low = sub(applied_guess_mps2, 100.0)
    high = add(applied_guess_mps2, 100.0)

    for _ in range(100):
        _r_low, v_low = integrate(low)
        _r_high, v_high = integrate(high)

        if v_low <= v1_target_mps <= v_high:
            break

        low = sub(low, 100.0)
        high = add(high, 100.0)

    for _ in range(100):
        mid = div(add(low, high), 2.0)
        _r_mid, v_mid = integrate(mid)

        if v_mid < v1_target_mps:
            low = mid
        else:
            high = mid

    applied_accel_mps2 = div(add(low, high), 2.0)
    r1_m, v1_actual_mps = integrate(applied_accel_mps2)

    distance_m = sub(r1_m, r0_m)
    avg_mps = div(distance_m, total_seconds)

    return {
        "ok": True,
        "planet": planet,

        "start_radius_m": r0_m,
        "end_radius_m": r1_m,

        "distance_traveled_m": distance_m,
        "distance_traveled": dconvert(
            distance_m,
            DEFAULT_DIST_UNIT,
            output_dist_unit,
        ),

        "starting_velocity_mps": v0_mps,
        "ending_velocity_target_mps": v1_target_mps,
        "ending_velocity_actual_mps": v1_actual_mps,

        "time_to_target_seconds": total_seconds,

        "gravity_start_mps2": gravity_start_mps2,
        "gravity_end_mps2": div(mu, mul(r1_m, r1_m)),

        "applied_acceleration_mps2": applied_accel_mps2,
        "net_acceleration_start_mps2": sub(
            applied_accel_mps2,
            gravity_start_mps2,
        ),
        "net_acceleration_end_mps2": sub(
            applied_accel_mps2,
            div(mu, mul(r1_m, r1_m)),
        ),

        "average_velocity_mps": avg_mps,
        "average_velocity": get_velocity_conversion(
            velocity=avg_mps,
            input_dist_unit=DEFAULT_DIST_UNIT,
            input_time_unit=DEFAULT_TIME_UNIT,
            output_dist_unit=output_dist_unit,
            output_time_unit=output_time_unit,
        ),

        "units": {
            "distance": output_dist_unit,
            "input_velocity": f"{input_dist_unit}/{input_time_unit}",
            "average_velocity": f"{output_dist_unit}/{output_time_unit}",
            "time_input": time_input_unit,
        },
    }
