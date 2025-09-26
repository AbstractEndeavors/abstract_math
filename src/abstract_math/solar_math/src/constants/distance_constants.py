#src/constants/distaance_constants.py
from ..imports import *
# -------------------------
# distance Unit schema
# -------------------------
MILES = {"strings": ['mi', 'mile', 'miles'],
         "conv": {"miles": 1.0, "meters": 1609.34, "kilometers": 1.60934, 'feet': 5280.0}}
METER = {"strings": ['m', 'meter', 'meters'],
         "conv": {"miles": 0.00621371, "meters": 1.0, "kilometers": 0.001, 'feet': 3.28084}}
KILOMETER = {"strings": ['km', 'kilo', 'kilometer', 'kilometers'],
             "conv": {"miles": 0.621371, "meters": 1000.0, "kilometers": 1.0, 'feet': 3280.84}}
FEET = {"strings": ['ft', 'foot', 'feet', 'foots', 'feets'],
        "conv": {"miles": 0.000189394, "meters": 0.3048, "kilometers": 0.0003048, 'feet': 1.0}}

DISTANCE_CONVERSIONS: Dict[str, Dict[str, Dict[str, float]]] = {
    "miles": MILES,
    "meters": METER,
    "kilometers": KILOMETER,
    "feet": FEET
}
ALL_DISTANCE_UNITS = ("meters", "kilometers", "miles", "feet")
DEFAULT_UNITS="meters"
DEFAULT_START_ALTITUDE=0.0
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

def get_distance_unit_conversions(unit: str) -> Dict[str, Dict[str, float]]:
    return DISTANCE_CONVERSIONS[normalize_distance_unit(unit)]

def _factor(unit_from: str, unit_to: str) -> float:
    """Multiplicative factor s.t. value_in_to = value_in_from * factor."""
    uf = get_distance_unit_conversions(unit_from)["conv"]["meters"]  # meters per 1 from-unit
    ut = get_distance_unit_conversions(unit_to)["conv"]["meters"]    # meters per 1 to-unit
    return div(uf, ut)

def dconvert(value: float, unit_from: str, unit_to: str) -> float:
    return mul(value, _factor(unit_from, unit_to))
def get_normalized_distance(
    distance: Optional[float] = None,
    input_units: str = DEFAULT_UNITS
    ):
    distance = target_alt_m = distance or 0
    if distance is not None:
        target_alt_m = dconvert(value=distance,
                unit_from=input_units,
                unit_to=DEFAULT_UNITS
                )
    return target_alt_m
def get_target_distance(
    distance: Optional[float] = None,
    input_units: str = DEFAULT_UNITS,
    output_units: str = DEFAULT_UNITS,
    ):
    distance = target_distance = distance or 0
    if distance is not None:
        target_distance = dconvert(value=distance,
                              unit_from=input_units,
                              unit_to=output_units)
    return target_distance
