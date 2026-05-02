# src/constants/planet_constants.py
from ..imports import *
from .distance_constants import *
from .time_constants import *

# -------------------------
# Physical constants (SI)
# -------------------------
G = 6.67430e-11  # m^3 kg^-1 s^-2
g0 = 9.80665     # m/s^2

try:
    MU_MOON
except NameError:
    MU_MOON = 4.9048695e12  # m^3/s^2

# -------------------------
# Bodies
# `parent` names the body this one orbits. Orbital elements
# (a, e, m0_deg, peri_lon_deg) are measured against that parent.
# Sun has no parent (heliocentric origin); Moon's parent is Earth,
# everything else's parent is the Sun. Hill/SOI computations key
# off this so heliocentric vs geocentric stays honest.
# -------------------------
PLANETS = [
    { "name":'Sun',     "parent":None,    "m0_deg":0,            "mu":1.32712440018e20, "a":0,            "e":0,          "radiusPx":20, "color":'yellow',    "radius":696000000, "escapeVel":61770, "n":0, "peri_lon_deg":0 },
    { "name":'Mercury', "parent":"sun",   "m0_deg":252.25032350, "mu":2.20320e13,       "a":5.7909927e10, "e":0.20563593, "radiusPx":4,  "color":'#a6a6a6',   "radius":2440000,   "escapeVel":4300,  "n":1, "peri_lon_deg":77.45779628 },
    { "name":'Venus',   "parent":"sun",   "m0_deg":181.97909950, "mu":3.24859e14,       "a":1.0820948e11, "e":0.00677672, "radiusPx":7,  "color":'#e0c16b',   "radius":6052000,   "escapeVel":10400, "n":2, "peri_lon_deg":131.60246718 },
    { "name":'Earth',   "parent":"sun",   "m0_deg":100.46457166, "mu":3.98600e14,       "a":1.49598261e11,"e":0.01671123, "radiusPx":8,  "color":'#4e6ef2',   "radius":6371000,   "escapeVel":11200, "n":3, "peri_lon_deg":102.93768193 },
    { "name":'Mars',    "parent":"sun",   "m0_deg":-4.55343205,  "mu":4.28284e13,       "a":2.2793664e11, "e":0.09339410, "radiusPx":6,  "color":'#c1440e',   "radius":3390000,   "escapeVel":5030,  "n":4, "peri_lon_deg":-23.94362959 },
    { "name":'Jupiter', "parent":"sun",   "m0_deg":34.39644051,  "mu":1.26687e17,       "a":7.7841200e11, "e":0.04838624, "radiusPx":14, "color":'#d2a679',   "radius":71492000,  "escapeVel":59500, "n":5, "peri_lon_deg":14.72847983 },
    { "name":'Saturn',  "parent":"sun",   "m0_deg":49.95424423,  "mu":3.79312e16,       "a":1.4267254e12, "e":0.05386179, "radiusPx":12, "color":'#e3c168',   "radius":60268000,  "escapeVel":35500, "n":6, "peri_lon_deg":92.59887831 },
    { "name":'Uranus',  "parent":"sun",   "m0_deg":313.23810451, "mu":5.79394e15,       "a":2.8706582e12, "e":0.04725744, "radiusPx":10, "color":'#7fbde8',   "radius":25559000,  "escapeVel":21300, "n":7, "peri_lon_deg":170.95427630 },
    { "name":'Neptune', "parent":"sun",   "m0_deg":-55.12002969, "mu":6.83653e15,       "a":4.4983964e12, "e":0.00859048, "radiusPx":10, "color":'#4363d8',   "radius":24764000,  "escapeVel":23500, "n":8, "peri_lon_deg":44.96476227 },
    { "name":'Moon',    "parent":"earth", "m0_deg":0,            "mu":MU_MOON,          "a":3.844e8,      "e":0.0549,     "radiusPx":5,  "color":'lightgray', "radius":1.737e6,   "escapeVel":2380,  "n":9, "peri_lon_deg":0 },
]
DEFAULT_PLANET='earth'
DEFAULT_AS_RADIUS=False

# -------------------------
# Body enrichment + lookup
# -------------------------
def _enrich_body(b: Dict[str, Any]) -> Dict[str, Any]:
    """Add derived diameter, mass, surface g. Body-intrinsic only;
    Hill/SOI are NOT cached here because they depend on the parent
    and belong with the equation, not the body."""
    mu = b["mu"]
    r  = b["radius"]
    if "diameter" not in b or not b["diameter"]:
        b["diameter"] = mul(2.0, r)
    b["mass"] = div(mu, G)
    surf_g = div(mu, mul(r, r))
    b["surface_g"] = surf_g
    b["surface_g_g0"] = div(surf_g, g0)
    return b

_NAME_ALIASES = {"sol": "sun", "terra": "earth", "luna": "moon"}
def _normalize_name(planet: str) -> str:
    if not isinstance(planet, str):
        raise TypeError(f"Expected str for body name, got {type(planet).__name__}: {planet!r}")
    n = planet.lower()
    return _NAME_ALIASES.get(n, n)

_BODY_BY_NAME: Dict[str, Dict[str, Any]] = {}
for entry in PLANETS:
    _BODY_BY_NAME[entry["name"].lower()] = _enrich_body(dict(entry))

# -------------------------
# Lookup
# -------------------------
def get_body(planet: str) -> Dict[str, Any]:
    key = _normalize_name(planet=planet)
    body = _BODY_BY_NAME.get(key)
    if not body:
        raise KeyError(f"Unknown body '{planet}'. Available: {sorted(_BODY_BY_NAME.keys())}")
    return body

def get_planet_vars(planet: str, output_dist_unit: str = "meters") -> Dict[str, Any]:
    """
    Return body properties with radius/diameter in `dist_unit`.
    Mass in kg; mu in m^3/s^2; surface_g in m/s^2.
    """
    body = get_body(planet=planet)
    dist_unit_norm = normalize_distance_unit(output_dist_unit)
    r_m = body["radius"]
    d_m = body["diameter"]

    out = dict(body)
    out["radius"] = dconvert(r_m, input_dist_unit="meters", output_dist_unit=dist_unit_norm)
    out["diameter"] = dconvert(d_m, input_dist_unit="meters", output_dist_unit=dist_unit_norm)
    out["radius_unit"] = dist_unit_norm
    out["diameter_unit"] = dist_unit_norm
    return out

# -------------------------
# Public API: scalar getters
# -------------------------
def planet_radius(planet: str = "earth", input_dist_unit: str = "meters") -> float:
    return get_planet_vars(planet=planet, input_dist_unit=input_dist_unit)["radius"]

def planet_diameter(planet: str = "earth", input_dist_unit: str = "meters") -> float:
    return get_planet_vars(planet=planet, input_dist_unit=input_dist_unit)["diameter"]

def full_planet_surface_area(planet: str = "earth", input_dist_unit: str = 'meters') -> float:
    r = planet_radius(planet=planet, input_dist_unit=input_dist_unit)
    return mul(4 * pi(), exp(r, 2))

def planet_volume(planet: str = "earth", input_dist_unit: str = 'meters') -> float:
    r = planet_radius(planet=planet, input_dist_unit=input_dist_unit)
    return mul((4.0/3.0) * pi(), exp(r, 3))

def planet_circumference(planet: str = "earth", input_dist_unit: str = 'meters') -> float:
    r = planet_radius(planet=planet, input_dist_unit=input_dist_unit)
    return mul(2 * pi(), r)

def planet_mass(planet: str = "earth") -> float:
    return get_planet_vars(planet=planet)["mass"]

def planet_surface_g(planet: str = "earth", as_g0: bool = False, input_dist_unit: str = "meters") -> float:
    v = get_planet_vars(planet=planet, input_dist_unit=input_dist_unit)["surface_g"]
    return div(v, g0) if as_g0 else v

def escape_velocity(planet: str = "earth", altitude: float = 0.0, input_dist_unit: str = "meters") -> float:
    """Escape velocity (m/s) from `altitude` above surface."""
    body = get_body(planet=planet)
    mu = body["mu"]
    r  = body["radius"]  # meters
    h_m = dconvert(altitude, input_dist_unit=input_dist_unit, output_dist_unit="meters")
    R = add(r, h_m)
    return math.sqrt(mul(2.0, div(mu, R)))

# -------------------------
# Gravity reach
# Three definitions, none of them a single constant:
#   - hill_radius:   gravitational dominance vs parent body
#   - soi_radius:    Laplace sphere of influence (patched-conic boundary)
#   - gravity_reach: radius where g drops below a chosen threshold
# Hill and SOI use the body's encoded `parent` so we never silently
# mix heliocentric and geocentric frames.
# -------------------------
def hill_radius(
    planet: str = "earth",
    output_dist_unit: str = "meters",
    to_dict=False
    ) -> float:
    """r_H ≈ a * (m / 3M)^(1/3), evaluated against the body's encoded parent."""
    normalized_output_dist_unit = normalize_distance_unit(output_dist_unit)
    input_dist_unit="m"
    b = get_body(planet=planet)
    parent_name = b.get("parent")
    if not parent_name:
        raise ValueError(f"'{planet}' has no parent body; Hill radius is undefined.")
    if not b.get("a"):
        raise ValueError(f"'{planet}' has no semi-major axis; Hill radius is undefined.")
    p = get_body(parent_name)
    ratio = div(b["mu"], mul(3.0, p["mu"]))
    r_m = mul(b["a"], exp(ratio, 1.0/3.0))
    hill_rad =  dconvert(r_m,input_dist_unit=input_dist_unit , output_dist_unit=normalized_output_dist_unit)
    if not to_dict:
        return per_sec_to_mps
    return {
            "input": {
                "planet":planet,
                "input_dist_unit": normalized_output_dist_unit
            },
            "output": {
                "hill_radius": hill_rad,
                "output_dist_unit": normalized_output_dist_unit,
            }
        }
def soi_radius(
    planet: str = "earth",
    output_dist_unit: str = "meters",
    to_dict=False
    ) -> float:
    """r_SOI ≈ a * (m/M)^(2/5), evaluated against the body's encoded parent."""
    normalized_output_dist_unit = normalize_distance_unit(output_dist_unit)
    input_dist_unit= "m"
    b = get_body(planet=planet)
    parent_name = b.get("parent")
    if not parent_name:
        raise ValueError(f"'{planet}' has no parent body; SOI is undefined.")
    if not b.get("a"):
        raise ValueError(f"'{planet}' has no semi-major axis; SOI is undefined.")
    p = get_body(planet=parent_name)
    ratio = div(b["mu"], p["mu"])
    r_m = mul(b["a"], exp(ratio, 2.0/5.0))
    soi_rad =  dconvert(r_m,input_dist_unit=input_dist_unit , output_dist_unit=normalized_output_dist_unit)
    if not to_dict:
        return soi_rad
    return {
            "input": {
                "planet":planet,
                "input_dist_unit": normalized_output_dist_unit
            },
            "output": {
                "soi_radius": soi_rad,
                "output_dist_unit": normalized_output_dist_unit,
            }
        }
def gravity_reach(
    planet: str = "earth",
    a_threshold: float = 1e-6,
    output_dist_unit: str = "meters",
    to_dict=False
    ) -> float:
    """
    Distance from body center at which gravitational acceleration falls
    below `a_threshold` (m/s^2). Pure two-body; no parent involved.
    Default 1e-6 m/s^2 is roughly the threshold used in many "edge of
    influence" rules of thumb — caller should override per use case.
    """

    if a_threshold <= 0:
        raise ValueError(f"a_threshold must be > 0, got {a_threshold}")
    normalized_output_dist_unit = normalize_distance_unit(output_dist_unit)
    input_dist_unit="m"
    mu = get_body(planet=planet)["mu"]
    r_m = math.sqrt(div(mu, a_threshold))
    grav_reach = dconvert(r_m,input_dist_unit=input_dist_unit , output_dist_unit=normalized_output_dist_unit)
    if not to_dict:
        return grav_reach
    return {
            "input": {
                "planet":planet,
                "a_threshold":a_threshold,
                "input_dist_unit": normalized_output_dist_unit
            },
            "output": {
                "gravity_reach": grav_reach,
                "output_dist_unit": normalized_output_dist_unit,
            }
        }
# -------------------------
# Earth-centric geometry utils (unit-consistent)
# -------------------------
def pi() -> float:
    return math.pi

def earth_radius(
    input_dist_unit: str = 'meters',
    to_dict=False
    ) -> float:
    radius = planet_radius(planet='earth', input_dist_unit=input_dist_unit)
    if not to_dict:
        return radius
    return {
            "input": {
                "input_dist_unit": input_dist_unit,
            },
            "output": {
                "radius": radius,
                "output_dist_unit": 'meters',
            }
        }
def earth_diameter(
    input_dist_unit: str = 'meters',
    to_dict=False
    ) -> float:
    diameter = planet_diameter(planet='earth', input_dist_unit=input_dist_unit)
    if not to_dict:
        return diameter
    return {
            "input": {
                "input_dist_unit": input_dist_unit,
            },
            "output": {
                "diameter": diameter,
                "output_dist_unit": 'meters',
            }
        }
def full_earth_surface_area(
    input_dist_unit: str = 'meters',
    to_dict=False
    ) -> float:
    r = earth_radius(input_dist_unit=input_dist_unit)
    earth_surface_area = mul(4 * pi(), exp(r, 2))
    if not to_dict:
        return earth_surface_area
    return {
            "input": {
                "input_dist_unit": input_dist_unit,
            },
            "output": {
                "earth_surface_area": earth_surface_area,
                "output_dist_unit": 'm^2',
            }
        }
def earth_volume(
    input_dist_unit: str = 'meters',
    to_dict=False
    ) -> float:
    r = earth_radius(input_dist_unit=input_dist_unit)
    volume = mul((4.0/3.0) * pi(), exp(r, 3))
    if not to_dict:
        return volume
    return {
            "input": {
                "input_dist_unit": input_dist_unit,
            },
            "output": {
                "volume": volume,
                "output_dist_unit": 'm^3',
            }
        }
def earth_circumference(
    input_dist_unit: str = 'meters',
    to_dict=False
    ) -> float:
    r = earth_radius(input_dist_unit=input_dist_unit)
    circumference = mul(2 * pi(), r)
    if not to_dict:
        return circumference
    return {
            "input": {
                "input_dist_unit": input_dist_unit,
            },
            "output": {
                "circumference": circumference,
                "output_dist_unit": 'm',
            }
        }
# =========================
# Radial toy + single-call wrapper
# =========================
def distance_per_sec_to_mps(
    v_per_sec: float,
    input_dist_unit: str,
    to_dict=False
    ) -> float:
    """Convert a speed given in `dist_unit`/s into m/s."""
    normalized_input_dist_unit = _normalize_unit(input_dist_unit=input_dist_unit)
    per_sec_to_mps = mul(v_per_sec, get_distance_unit_conversions(normalized_input_dist_unit)["conv"]["meters"])
    if not to_dict:
        return per_sec_to_mps
    return {
            "input": {
                "input_dist_unit": normalized_input_dist_unit,
                "input_time_unit": "s",
                "units": f"{input_dist_unit}/s",
                "v_per_sec":v_per_sec
            },
            "output": {
                "per_sec_to_mps": per_sec_to_mps,
                "output_dist_unit": "m",
                "output_time_unit": "s",
                "units": "m/s",
            }
        }
def g_at_radius(
    mu: float,
    r_m: float,
    to_dict=False
    ) -> float:
    at_radius = div(mu, mul(r_m, r_m))
    if not to_dict:
        return at_radius
    return {
            "input": {
                "input_dist_unit": "m",
                "radius":r_m
            },
            "output": {
                "at_radius": at_radius,
                "output_dist_unit": "m",
            }
        }
def get_R_mu(planet: str = DEFAULT_PLANET):
    body = get_body(planet=planet)
    mu = body.get("mu")     # m^3/s^2
    R  = body.get("radius") # m
    return R, mu
