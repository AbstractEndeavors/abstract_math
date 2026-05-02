# adapt_units_api.py  (or wherever you glue this in)
from typing import *
from .src.constants.distance_constants import dconvert, _factor as dfactor
from .src.constants.time_constants import seconds_per
from .src.constants.planet_constants import planet_radius, get_body, g_at_radius
from .src.utils.geometry_utils import visible_area_flat, visible_surface_angle
from .src.utils import tangential_component,radial_component,get_R_mu,get_normalized_distance,get_normalized_starting_velocity
from .src.imports import math, mul, div, add, exp  # your abstract_math ops
from .src.constants import (
    DEFAULT_DIST_UNIT,
    DEFAULT_TIME_UNIT,
    DEFAULT_PLANET,
    DEFAULT_START_ALTITUDE,
    DEFAULT_AS_RADIUS
    )

def normalize_inputs(
    planet: str,
    start_altitude: float,
    starting_velocity: float,
    input_dist_unit: str,
    input_time_unit: str,
    target_distance: float = None,
    flight_path_angle_deg: float = 90.0
) -> dict:
    """
    **Description:** Acts as the input sanitization layer. It takes human-readable inputs with arbitrary distance and time units and converts them into strict SI units (meters, seconds, meters/second). Crucially, it also uses the `flight_path_angle_deg` to extract the purely radial (vertical) component of the starting velocity, ignoring lateral motion.

    **Parameters:**
    * `planet` (*str*): The identifier for the celestial body being simulated.
    * `start_altitude` (*float*): The initial altitude above the planet's surface.
    * `starting_velocity` (*float*): The total initial velocity vector magnitude.
    * `input_dist_unit` (*str*): The unit string for input distances (e.g., 'km', 'mi').
    * `input_time_unit` (*str*): The unit string for input times (e.g., 's', 'hr').
    * `target_distance` (*float*, optional): The desired target altitude to reach.
    * `flight_path_angle_deg` (*float*, default: 90.0): The angle of the velocity vector relative to the local horizon (90° = straight up).

    **Returns:** * *dict*: A dictionary containing normalized SI values (`start_alt_m`, `target_alt_m`, `v0_mps` [radial velocity], `total_v0_mps`, and `flight_path_angle_deg`).
    """
    start_alt_m = get_normalized_distance(start_altitude, input_dist_unit)
    target_alt_m = get_normalized_distance(target_distance, input_dist_unit)

    total_v0_mps = get_normalized_starting_velocity(
        start_altitude=start_alt_m,
        starting_velocity=starting_velocity,
        input_dist_unit=input_dist_unit,
        input_time_unit=input_time_unit,
        planet=planet,
    )
    v0_radial_mps = radial_component(
        total_v0_mps,
        flight_path_angle_deg,
    )
    return {
        "start_alt_m": start_alt_m,
        "target_alt_m": target_alt_m,
        "v0_mps": v0_radial_mps,
        "total_v0_mps": total_v0_mps,
        "flight_path_angle_deg": flight_path_angle_deg,
    }

# --- Analyzer (prints a scan; no blocking input) ---
def analyze_visible_surface(
    altitude_step: float = 200.0,
    max_steps: int = 20,
    fov_range: tuple[int, int] = (20, 160),
    fov_interval: int = 10,
    input_dist_unit: str = DEFAULT_DIST_UNIT,      # how to interpret altitude numbers
    display_units: str = DEFAULT_DIST_UNIT,    # how to print areas/radii
    planet: str = DEFAULT_PLANET,
    printit: bool = False
):
    """
    **Description:** A diagnostic utility that generates a scan of visible surface areas from a planet at incrementally increasing altitudes and different camera Fields of View (FOV). It calculates the spherical cap area visible to an observer and converts the mathematical outputs (in meters) directly into the requested display units. It does not return data to the integrator; it is purely for analysis and reporting.

    **Parameters:**
    * `altitude_step` (*float*): The increment added to the altitude for each step in the scan.
    * `max_steps` (*int*): The total number of altitude increments to calculate.
    * `fov_range` (*tuple[int, int]*): The min and max Field of View angles in degrees.
    * `fov_interval` (*int*): The step size between FOV calculations.
    * `input_dist_unit` (*str*): The unit system used to interpret the `altitude_step`.
    * `display_units` (*str*): The unit system used for printing output areas and radii.
    * `planet` (*str*): The celestial body being observed.
    * `printit` (*bool*): If True, prints the generated scan to the console.

    **Returns:**
    * *dict*: A structured dictionary (`all_stats`) containing the raw text output, units used, and a nested list of variables calculated at every altitude/FOV combination.
    """
    # Planet radius and full area (compute in meters, convert for display)
    r_m = planet_radius(planet, DEFAULT_DIST_UNIT)
    full_area_m2 = 4.0 * math.pi * (r_m ** 2)
    k_disp = dfactor(DEFAULT_DIST_UNIT, display_units)      # linear meter->display factor
    full_area_disp = full_area_m2 * (k_disp ** 2)  # convert area to display units^2

    all_stats = {"output": "", "input_dist_unit": input_dist_unit,
                 "display_units": display_units, "vars": []}

    for i in range(1, max_steps + 1):
        all_stats["vars"].append({})
        altitude_in = altitude_step * i                       # input_dist_unit
        altitude_m  = dconvert(altitude_in, input_dist_unit, DEFAULT_DIST_UNIT)

        all_stats["vars"][-1]['altitude_input'] = altitude_in
        all_stats["vars"][-1]['input_dist_unit']    = input_dist_unit
        all_stats["vars"][-1]['fov']            = []

        alt_pretty = dconvert(altitude_in, input_dist_unit, display_units)
        all_stats["output"] += (
            f"\n=== Altitude: {altitude_in} {input_dist_unit} (≈ {alt_pretty:.3f} {display_units}) ===\n"
        )

        for fov in range(fov_range[0], fov_range[1] + 1, fov_interval):
            # Compute visible area/radius in meters, convert to display units
            area_m2, vis_radius_m = visible_area_flat(fov, altitude_m, DEFAULT_DIST_UNIT)
            area_disp = area_m2 * (k_disp ** 2)
            vis_radius_disp = dconvert(vis_radius_m, DEFAULT_DIST_UNIT, display_units)

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
    """
    **Description:** The core physics step function. It performs a single iteration of a Forward-Euler numerical integration to update the kinematic state of an object in a radial gravity field. It calculates local gravitational acceleration using the formula $a = -\frac{\mu}{r^2}$.

    **Parameters:**
    * `mu` (*float*): The standard gravitational parameter of the planet ($GM$).
    * `v` (*float*): Current radial velocity in m/s.
    * `r` (*float*): Current distance from the planet's center in meters.
    * `t` (*float*): Current simulation time in seconds.
    * `dt_s` (*float*): The time-step delta in seconds.
    * `steps` (*int*): The current iteration count.

    **Returns:**
    * *tuple*: The updated kinematic state `(v, r, t, steps)`.
    """
    a = - div(mu, mul(r, r))  # inward accel
    v = add(v, mul(a, dt_s))
    r = add(r, mul(v, dt_s))
    t = add(t, dt_s)
    steps += 1
    return v, r, t, steps


# --- tracker helper ---
def init_tracker(r0: float) -> dict:
    """
    **Description:** A lightweight helper function that initializes the state dictionary used to track maximums and totals during the simulation loop.

    **Parameters:**
    * `r0` (*float*): The initial radius from the center of the planet.

    **Returns:**
    * *dict*: A tracking dictionary with default values for apoapsis tracking (`furthest_r`, `time_at_furthest`, etc.).
    """
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
    """
    **Description:** The main simulation loop. It repeatedly calls `calculate_avrt` to advance the object's state through time using strict SI units. The loop monitors for specific exit conditions: hitting the planet's surface, reaching a predefined target altitude, or turning back (reaching apoapsis and falling).

    **Parameters:**
    * `v0_mps` (*float*): Initial radial velocity in m/s.
    * `start_alt_m` (*float*): Initial altitude above the surface in meters.
    * `planet` (*str*): The celestial body dictating the gravity field.
    * `dt_s` (*float*, default: 1.0): The integration time-step.
    * `max_steps` (*int*): The maximum allowed loop iterations before timing out.
    * `target_alt_m` (*float*, optional): The altitude that triggers a successful "hit_target" exit.

    **Returns:**
    * *dict*: The final simulation state, including boolean flags for how the simulation ended (`hit_surface`, `hit_target`, `turned_back`), final kinematics, local gravity data, and extended tracking stats (like max altitude reached).
    """
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
        "vesc_end_mps": exp(mul(2.0, div(mu, r)),-2),

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
    input_dist_unit: str = DEFAULT_DIST_UNIT,
    input_time_unit: str = DEFAULT_TIME_UNIT,
    output_dist_unit: str = DEFAULT_DIST_UNIT,
    output_time_unit: str = DEFAULT_TIME_UNIT,
    *,
    planet: str = DEFAULT_PLANET,
    dt_s: float = 1.0,
    max_steps: int = 5_000_000,
    target_distance: float = None,
    flight_path_angle_deg: float = 90.0,
) -> dict:
    """
    **Description:** The primary public-facing wrapper API. It orchestrates the entire lifecycle of a simulation request. It uses `normalize_inputs` to sanitize the user data, feeds it into `simulate_radial_flight_si`, and finally converts all output data from SI meters/seconds back into the user's specified `output_dist_unit` and `output_time_unit`.

    **Parameters:**
    * `starting_velocity` (*float*): Initial velocity magnitude.
    * `start_altitude` (*float*): Initial altitude above the surface.
    * `input_dist_unit` (*str*): Units for input distance/altitude.
    * `input_time_unit` (*str*): Units for input time.
    * `output_dist_unit` (*str*): Desired units for the returned distances/altitudes.
    * `output_time_unit` (*str*): Desired units for the returned time/velocities.
    * `planet` (*str*): Target celestial body.
    * `dt_s` (*float*): Simulation time-step resolution.
    * `max_steps` (*int*): Simulation iteration limit.
    * `target_distance` (*float*, optional): Goal altitude to trigger simulation halt.
    * `flight_path_angle_deg` (*float*, default: 90.0): Launch angle.

    **Returns:**
    * *dict*: A highly detailed dictionary containing a recap of the inputs, the final converted kinematic state (altitude, velocity, time), completion flags, gravity metrics, and apoapsis (furthest distance) statistics. Returns an error dict if the simulation fails to initialize.
    """
    norm = normalize_inputs(
        planet=planet,
        start_altitude=start_altitude,
        starting_velocity=starting_velocity,
        input_dist_unit=input_dist_unit,
        input_time_unit=input_time_unit,
        target_distance=target_distance,
        flight_path_angle_deg=flight_path_angle_deg,
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

    sec_per_out = seconds_per(output_time_unit)
    conv = lambda m: dconvert(m, DEFAULT_DIST_UNIT, output_dist_unit)

    return {
        "ok": True,
        "planet": planet,
        "inputs": {
            "start_altitude": start_altitude,
            "starting_velocity_total": starting_velocity,
            "flight_path_angle_deg": flight_path_angle_deg,
            "input_dist_unit": input_dist_unit,
            "input_time_unit": input_time_unit,
            "output_dist_unit": output_dist_unit,
            "output_time_unit": output_time_unit,
            "target_distance": target_distance,
        },
        "altitude": conv(sim["altitude_m"]),
        "radius_from_center": conv(sim["r_m"]),
        "distance_traveled_radial": conv(sim["traveled_m"]),
        "velocity_radial": mul(
            dconvert(sim["vEnd_mps"], DEFAULT_DIST_UNIT, output_dist_unit),
            sec_per_out,
        ),
        "time": div(sim["time_s"], sec_per_out),
        "time_unit": output_time_unit,
        "g_end_mps2": sim["g_end_mps2"],
        "g_ratio_surface": sim["g_ratio_surface"],
        "steps": sim["steps"],
        "hit_surface": sim["hit_surface"],
        "hit_target": sim["hit_target"],
        "turned_back": sim["turned_back"],
        "furthest_distance": conv(sim["furthest_altitude_m"]),
        "furthest_radius": conv(sim["furthest_r"]),
        "time_at_furthest": div(sim["time_at_furthest"], sec_per_out),
        "total_radial_distance": conv(sim["total_distance_m"]),
    }
