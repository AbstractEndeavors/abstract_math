#src/constants/distance_constants.py
from ..imports import *

# -------------------------
# distance unit schema
# -------------------------

MILES = {
    "strings": ["mi", "mile", "miles"],
    "conv": {
        "miles": 1.0,
        "meters": 1609.34,
        "kilometers": 1.60934,
        "centimeters": 160934.0,
        "millimeters": 1609340.0,
        "feet": 5280.0,
        "inch": 63360.0,
    },
}

METER = {
    "strings": ["m", "meter", "meters"],
    "conv": {
        "miles": 0.000621371,
        "meters": 1.0,
        "kilometers": 0.001,
        "centimeters": 100.0,
        "millimeters": 1000.0,
        "feet": 3.28084,
        "inch": 39.37008,
    },
}

KILOMETER = {
    "strings": ["km", "kilo", "kilometer", "kilometers"],
    "conv": {
        "miles": 0.621371,
        "meters": 1000.0,
        "kilometers": 1.0,
        "centimeters": 100000.0,
        "millimeters": 1000000.0,
        "feet": 3280.84,
        "inch": 39370.08,
    },
}

CENTIMETER = {
    "strings": ["cm", "centimeter", "centimeters"],
    "conv": {
        "miles": 0.00000621371,
        "meters": 0.01,
        "kilometers": 0.00001,
        "centimeters": 1.0,
        "millimeters": 10.0,
        "feet": 0.0328084,
        "inch": 0.3937008,
    },
}

MILLIMETER = {
    "strings": ["mm", "millimeter", "millimeters"],
    "conv": {
        "miles": 0.000000621371,
        "meters": 0.001,
        "kilometers": 0.000001,
        "centimeters": 0.1,
        "millimeters": 1.0,
        "feet": 0.00328084,
        "inch": 0.03937008,
    },
}

FEET = {
    "strings": ["ft", "foot", "feet", "foots", "feets"],
    "conv": {
        "miles": 0.000189394,
        "meters": 0.3048,
        "kilometers": 0.0003048,
        "centimeters": 30.48,
        "millimeters": 304.8,
        "feet": 1.0,
        "inch": 12.0,
    },
}

INCH = {
    "strings": ["in", "inch", "inches"],
    "conv": {
        "miles": 0.0000157828,
        "meters": 0.0254,
        "kilometers": 0.0000254,
        "centimeters": 2.54,
        "millimeters": 25.4,
        "feet": 1 / 12,
        "inch": 1.0,
    },
}

DISTANCE_CONVERSIONS: Dict[str, Dict[str, Any]] = {
    "miles": MILES,
    "meters": METER,
    "kilometers": KILOMETER,
    "centimeters": CENTIMETER,
    "millimeters": MILLIMETER,
    "feet": FEET,
    "inch": INCH,
}

ALL_DISTANCE_UNITS = ("meters", "kilometers", "miles", "feet", "inch","millimeters","centimeters")
DEFAULT_DIST_UNIT="m"
DEFAULT_START_ALTITUDE=0.0
def get_smallest_dist_unit_string(unit):
    for key,values in DISTANCE_CONVERSIONS.items():
        if unit in values["strings"]:
            return values["strings"][0]
    return unit
# -------------------------
# Unit helpers
# -------------------------
def normalize_distance_unit(unit: str) -> str:
    u = unit.strip().lower()
    if u in DISTANCE_CONVERSIONS:
        return u
    for key, values in DISTANCE_CONVERSIONS.items():
        if u in values.get("strings", []):
            return key
    # was: CONVERSIONS
    raise ValueError(f"Unknown unit '{unit}'. Supported: {list(DISTANCE_CONVERSIONS.keys())}")

def get_distance_unit_conversions(dist_unit: str) -> Dict[str, Dict[str, float]]:
    return DISTANCE_CONVERSIONS[normalize_distance_unit(dist_unit)]

def _factor(input_dist_units: str, output_dist_units: str) -> float:
    """Multiplicative factor s.t. value_in_to = value_in_from * factor."""
    uf = get_distance_unit_conversions(input_dist_units)["conv"]["meters"]  # meters per 1 from-unit
    ut = get_distance_unit_conversions(output_dist_units)["conv"]["meters"]    # meters per 1 to-unit
    return div(uf, ut)

def dconvert(value: float, input_dist_units: str, output_dist_units: str) -> float:
    return  mul(value, _factor(input_dist_units, output_dist_units))

def dconvert_dict(value: float, input_dist_units: str, output_dist_units: str) -> float:
    return {"value":dconvert(value=value, input_dist_units=input_dist_units, output_dist_units=output_dist_units),"dist_units":output_dist_units}

def get_normalized_distance(
    distance: Optional[float] = None,
    input_dist_units: str = DEFAULT_DIST_UNIT
    ):
    distance = target_alt_m = distance or 0
    if distance is not None:
        target_alt_m = dconvert(value=distance,
                input_dist_units=input_dist_units,
                output_dist_units=DEFAULT_DIST_UNIT
                )
    return target_alt_m
def get_target_distance(
    distance: Optional[float] = None,
    input_dist_units: str = DEFAULT_DIST_UNIT,
    output_dist_units: str = DEFAULT_DIST_UNIT,
    ):
    distance = target_distance = distance or 0
    if distance is not None:
        target_distance = dconvert(value=distance,
                              input_dist_units=input_dist_units,
                              output_dist_units=output_dist_units)
    return target_distance
