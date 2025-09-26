# adapt_units_api.py  (or wherever you glue this in)
from typing import *
from .src.constants.distance_constants import dconvert, _factor as dfactor
from .src.constants.time_constants import seconds_per
from .src.constants.planet_constants import planet_radius, get_body, g_at_radius
from .src.utils.geometry_utils import visible_area_flat, visible_surface_angle
from .src.utils import get_R_mu,get_normalized_distance,get_normalized_starting_velocity
from .src.imports import math, mul, div, add  # your abstract_math ops
from .src.constants import (
    DEFAULT_UNITS,
    DEFAULT_TIME,
    DEFAULT_PLANET,
    DEFAULT_START_ALTITUDE,
    DEFAULT_AS_RADIUS
    )
def normalize_inputs(
    planet: str,
    start_altitude: float,
    starting_velocity: float,
    input_units: str,
    input_time: str,
    target_distance: float = None,
) -> dict:
    """Normalize input altitudes and velocities into SI (meters, seconds)."""
    start_alt_m = get_normalized_distance(start_altitude, input_units)
    target_alt_m = get_normalized_distance(target_distance, input_units)

    v0_mps = get_normalized_starting_velocity(
        start_altitude=start_alt_m,
        starting_velocity=starting_velocity,
        input_units=input_units,
        input_time=input_time,
        planet=planet,
    )

    return {
        "start_alt_m": start_alt_m,
        "target_alt_m": target_alt_m,
        "v0_mps": v0_mps,
    }
# --- Analyzer (prints a scan; no blocking input) ---
def analyze_visible_surface(
    altitude_step: float = 200.0,
    max_steps: int = 20,
    fov_range: tuple[int, int] = (20, 160),
    fov_interval: int = 10,
    input_units: str = DEFAULT_UNITS,      # how to interpret altitude numbers
    display_units: str = DEFAULT_UNITS,    # how to print areas/radii
    planet: str = DEFAULT_PLANET,
    printit: bool = False
):
    """
    Scan altitudes/FOVs. Altitudes are interpreted in `input_units`.
    Results are printed in `display_units`.
    """
    # Planet radius and full area (compute in meters, convert for display)
    r_m = planet_radius(planet, DEFAULT_UNITS)
    full_area_m2 = 4.0 * math.pi * (r_m ** 2)
    k_disp = dfactor(DEFAULT_UNITS, display_units)      # linear meter->display factor
    full_area_disp = full_area_m2 * (k_disp ** 2)  # convert area to display units^2

    all_stats = {"output": "", "input_units": input_units,
                 "display_units": display_units, "vars": []}

    for i in range(1, max_steps + 1):
        all_stats["vars"].append({})
        altitude_in = altitude_step * i                       # input_units
        altitude_m  = dconvert(altitude_in, input_units, DEFAULT_UNITS)

        all_stats["vars"][-1]['altitude_input'] = altitude_in
        all_stats["vars"][-1]['input_units']    = input_units
        all_stats["vars"][-1]['fov']            = []

        alt_pretty = dconvert(altitude_in, input_units, display_units)
        all_stats["output"] += (
            f"\n=== Altitude: {altitude_in} {input_units} (≈ {alt_pretty:.3f} {display_units}) ===\n"
        )

        for fov in range(fov_range[0], fov_range[1] + 1, fov_interval):
            # Compute visible area/radius in meters, convert to display units
            area_m2, vis_radius_m = visible_area_flat(fov, altitude_m, DEFAULT_UNITS)
            area_disp = area_m2 * (k_disp ** 2)
            vis_radius_disp = dconvert(vis_radius_m, DEFAULT_UNITS, display_units)

            # Span uses geometry only; r_m is in meters
            _, angle_deg = visible_surface_angle(vis_radius_m, r_m)

            coverage_pct = 100.0 * (area_disp / full_area_disp)

            fov_output = (
                f"FOV: {fov:>3}° | "
                f"Area: {area_disp:>12.2f} {display_units}² | "
                f"Span: {angle_deg:>7.2f}° | "
                f"Flat-visible: {coverage_pct:>6.3f}% | "
                f"visR≈{vis_radius_disp:.3f} {display_units}"
            )
            all_stats["output"] += fov_output + "\n"

            all_stats["vars"][-1]['fov'].append({
                "FOV": fov,
                "area": area_disp,
                "angle_deg": angle_deg,
                "coverage_pct": coverage_pct,
                "visible_radius": vis_radius_disp,
                "output": fov_output
            })

    if printit:
        print(all_stats.get('output'))
    return all_stats
# --- core integrator step ---
def calculate_avrt(mu, v, r, t=0.0, dt_s=1.0, steps=0):
    """Single Euler step update for radial motion."""
    a = - div(mu, mul(r, r))  # inward accel
    v = add(v, mul(a, dt_s))
    r = add(r, mul(v, dt_s))
    t = add(t, dt_s)
    steps += 1
    return v, r, t, steps


# --- tracker helper ---
def init_tracker(r0: float) -> dict:
    """Initialize stats tracker."""
    return {
        "furthest_r": r0,
        "time_at_furthest": 0.0,
        "furthest_step": 0,
        "total_distance": 0.0,
    }


# --- SI integrator with tracking ---
def simulate_radial_flight_si(
    v0_mps: float,
    start_alt_m: float,
    planet: str,
    dt_s: float = 1.0,
    max_steps: int = 5_000_000,
    target_alt_m: float = None
) -> dict:
    """Forward-Euler radial integrator, SI only (meters/seconds)."""
    R, mu = get_R_mu(planet=planet)
    r0 = add(R, start_alt_m)
    r  = r0
    v  = v0_mps
    t  = 0.0
    prev_r = r0
    r_target = add(R, target_alt_m) if target_alt_m else float("inf")
    traveled_m = 0.0

    hit_surface, hit_target, turned_back = False, False, False
    steps = 0
    tracker = init_tracker(r0)

    for _ in range(max_steps):
        if r <= R:
            hit_surface = True
            break
        if target_alt_m and r >= r_target:
            hit_target = True
            break

        v, r, t, steps = calculate_avrt(mu, v, r, t, dt_s, steps)

        # update traveled distance
        traveled_step = abs(r - prev_r)
        traveled_m += traveled_step
        tracker["total_distance"] += traveled_step
        prev_r = r

        # update furthest distance tracker
        if r > tracker["furthest_r"]:
            tracker["furthest_r"] = r
            tracker["time_at_furthest"] = t
            tracker["furthest_step"] = steps

        # detect turnaround
        if not target_alt_m and v < 0 and r < r0:
            turned_back = True
            break

    altitude_m = max(0.0, r - R)
    g_end      = g_at_radius(mu, r)
    g_surface  = g_at_radius(mu, R)

    return {
        "ok": True,
        "planet": planet,
        "r_m": r,
        "altitude_m": altitude_m,
        "vEnd_mps": v,
        "time_s": t,
        "g_end_mps2": g_end,
        "g_ratio_surface": div(g_end, g_surface),
        "steps": steps,
        "hit_surface": hit_surface,
        "hit_target": hit_target,
        "turned_back": turned_back,
        "traveled_m": traveled_m,
        "vesc_end_mps": math.sqrt(mul(2.0, div(mu, r))),

        # extended stats
        "furthest_r": tracker["furthest_r"],
        "furthest_altitude_m": tracker["furthest_r"] - R,
        "time_at_furthest": tracker["time_at_furthest"],
        "total_distance_m": tracker["total_distance"],
    }


# --- wrapper with unit conversions ---
def radial_travel(
    starting_velocity: float = None,
    start_altitude: float = None,
    input_units: str = DEFAULT_UNITS,
    input_time: str = DEFAULT_TIME,
    output_units: str = DEFAULT_UNITS,
    output_time: str = DEFAULT_TIME,
    *,
    planet: str = DEFAULT_PLANET,
    dt_s: float = 1.0,
    max_steps: int = 5_000_000,
    target_distance: float = None
) -> dict:
    """Wrapper: handles units, runs SI integrator, converts outputs."""
    norm = normalize_inputs(
        planet=planet, start_altitude=start_altitude, starting_velocity=starting_velocity,
        input_units=input_units, input_time=input_time, target_distance=target_distance
    )

    sim = simulate_radial_flight_si(
        v0_mps=norm["v0_mps"],
        start_alt_m=norm["start_alt_m"],
        planet=planet,
        dt_s=dt_s,
        max_steps=max_steps,
        target_alt_m=norm["target_alt_m"],
    )
    if not sim.get("ok"):
        return sim

    # Output conversions
    sec_per_out = seconds_per(output_time)
    conv = lambda m: dconvert(m, DEFAULT_UNITS, output_units)

    return {
        "ok": True,
        "planet": planet,
        "inputs": {
            "start_altitude": start_altitude,
            "starting_velocity": starting_velocity,
            "input_units": input_units,
            "input_time": input_time,
            "output_units": output_units,
            "output_time": output_time,
            "target_distance": target_distance,
        },
        # final state
        "altitude": conv(sim["altitude_m"]),
        "radius_from_center": conv(sim["r_m"]),
        "distance_traveled": conv(sim["traveled_m"]),
        "velocity": mul(dconvert(sim["vEnd_mps"], DEFAULT_UNITS, output_units), sec_per_out),
        "velocity_escape_end": mul(dconvert(sim["vesc_end_mps"], DEFAULT_UNITS, output_units), sec_per_out),
        "time": div(sim["time_s"], sec_per_out),
        "time_unit": output_time,
        "g_end_mps2": sim["g_end_mps2"],
        "g_ratio_surface": sim["g_ratio_surface"],
        "steps": sim["steps"],
        "hit_surface": sim["hit_surface"],
        "hit_target": sim["hit_target"],
        "turned_back": sim["turned_back"],

        # extended stats (converted)
        "furthest_distance": conv(sim["furthest_altitude_m"]),
        "furthest_radius": conv(sim["furthest_r"]),
        "time_at_furthest": div(sim["time_at_furthest"], sec_per_out),
        "total_distance": conv(sim["total_distance_m"]),
    }

