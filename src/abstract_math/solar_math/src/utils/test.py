
from __future__ import annotations
from abstract_math import *

from dataclasses import dataclass
import math
from typing import Optional




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
