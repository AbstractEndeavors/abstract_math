from abstract_math import *
def apogee_from_speed_angle(
    start_altitude: float,
    starting_velocity: float,
    flight_path_angle_deg: float,
    target_altitude: float = None,
    input_dist_units: str = DEFAULT_DIST_UNIT,
    input_time_units: str = DEFAULT_TIME_UNIT,
    output_dist_units: str = DEFAULT_DIST_UNIT,
    planet: str = DEFAULT_PLANET,
):
    """
    Derive max altitude from initial altitude, speed, and flight-path angle.

    flight_path_angle_deg:
        0 deg  = tangential / horizontal
        90 deg = radial outward

    Uses:
        ε = v²/2 - μ/r
        h = r * v_tangential
        e = sqrt(1 + 2εh²/μ²)
        a = -μ/(2ε)
        r_apogee = a(1+e)
    """
    R, mu = get_R_mu(planet=planet)

    r0 = add(
        R,
        dconvert(start_altitude, input_dist_units, DEFAULT_DIST_UNIT),
    )

    v0 = distance_per_time_to_mps(
        v=starting_velocity,
        dist_unit=input_dist_units,
        time_unit=input_time_units,
    )

    gamma = math.radians(flight_path_angle_deg)

    v_radial = mul(v0, math.sin(gamma))
    v_tangential = mul(v0, math.cos(gamma))

    energy = sub(
        div(mul(v0, v0), 2.0),
        div(mu, r0),
    )

    h = mul(r0, v_tangential)

    result = {
        "ok": True,
        "planet": planet,
        "start_radius_m": r0,
        "start_altitude_m": sub(r0, R),
        "starting_velocity_mps": v0,
        "v_radial_mps": v_radial,
        "v_tangential_mps": v_tangential,
        "specific_energy": energy,
        "specific_angular_momentum": h,
        "flight_path_angle_deg": flight_path_angle_deg,
    }

    # Escape or parabolic trajectory.
    if energy >= 0:
        result.update({
            "trajectory": "escape_or_hyperbolic",
            "reaches_target": True if target_altitude is not None else None,
            "apogee_radius_m": None,
            "apogee_altitude_m": None,
            "apogee_altitude": None,
        })
        return result

    eccentricity = math.sqrt(
        add(
            1.0,
            div(
                mul(2.0, energy, h, h),
                mul(mu, mu),
            ),
        )
    )

    semi_major_axis = -div(
        mu,
        mul(2.0, energy),
    )

    apogee_radius = mul(
        semi_major_axis,
        add(1.0, eccentricity),
    )

    apogee_altitude_m = sub(
        apogee_radius,
        R,
    )

    result.update({
        "trajectory": "elliptic",
        "eccentricity": eccentricity,
        "semi_major_axis_m": semi_major_axis,
        "apogee_radius_m": apogee_radius,
        "apogee_altitude_m": apogee_altitude_m,
        "apogee_altitude": dconvert(
            apogee_altitude_m,
            DEFAULT_DIST_UNIT,
            output_dist_units,
        ),
    })

    if target_altitude is not None:
        target_altitude_m = dconvert(
            target_altitude,
            input_dist_units,
            DEFAULT_DIST_UNIT,
        )

        result["target_altitude_m"] = target_altitude_m
        result["reaches_target"] = apogee_altitude_m >= target_altitude_m

    return result

result = apogee_from_speed_angle(
    start_altitude=150,
    starting_velocity=24200,
    flight_path_angle_deg=15,
    target_altitude=238000,
    input_dist_units="mi",
    input_time_units="h",
    output_dist_units="mi",
    planet="earth",
)

print(result)
