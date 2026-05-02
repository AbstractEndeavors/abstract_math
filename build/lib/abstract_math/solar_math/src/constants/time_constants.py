#src/constants/time_constants.py
from ..imports import *

# -------------------------
# canonical duration factors
# -------------------------

second = 1.0
millisecond = 0.001 * second
minute = 60.0 * second
hour = 60.0 * minute
day = 24.0 * hour
week = 7.0 * day

# Approximate calendar durations
month = 30.0 * day
year = 365.0 * day

MILLISECONDS = {
    "strings": ["ms", "msec", "msecs", "millisecond", "milliseconds"],
    "conv": {"seconds": millisecond},
}

SECONDS = {
    "strings": ["s", "sec", "secs", "second", "seconds"],
    "conv": {"seconds": second},
}

MINUTES = {
    "strings": ["m", "min", "mins", "minute", "minutes"],
    "conv": {"seconds": minute},
}

HOURS = {
    "strings": ["h", "hr", "hrs", "hour", "hours"],
    "conv": {"seconds": hour},
}

DAYS = {
    "strings": ["d", "day", "days"],
    "conv": {"seconds": day},
}

WEEKS = {
    "strings": ["w", "wk", "wks", "week", "weeks"],
    "conv": {"seconds": week},
}

MONTHS = {
    "strings": ["mo", "mos", "month", "months"],
    "conv": {"seconds": month},
}

YEARS = {
    "strings": ["y", "yr", "yrs", "year", "years"],
    "conv": {"seconds": year},
}

TIME_CONVERSIONS = {
    "milliseconds": MILLISECONDS,
    "seconds": SECONDS,
    "minutes": MINUTES,
    "hours": HOURS,
    "days": DAYS,
    "weeks": WEEKS,
    "months": MONTHS,
    "years": YEARS,
}

ALL_TIME_UNITS = ("milliseconds","seconds", "minutes", "hours", "days","weeks","months","years")
DEFAULT_TIME_UNIT="s"
def get_smallest_time_unit_string(unit):
    for key,values in TIME_CONVERSIONS.items():
        if unit in values["strings"]:
            return values["strings"][0]
    return unit
def normalize_time_unit(time_unit: str) -> str:
    u = time_unit.strip().lower()
    if u in TIME_CONVERSIONS:
        return u
    for key, values in TIME_CONVERSIONS.items():
        if u in values.get("strings", []):
            return key
    raise ValueError(f"Unknown time unit '{time_unit}'. Supported: {list(TIME_CONVERSIONS.keys())}")

def get_time_unit_conversions(time_unit: str) -> dict:
    return TIME_CONVERSIONS[normalize_time_unit(time_unit)]

def time_factor(input_time_units: str, output_time_units: str) -> float:
    """
    multiplicative factor s.t.
      value_in_to = value_in_from * _time_factor(unit_from, unit_to)

    seconds per 1 unit_from  /  seconds per 1 unit_to
    """
    sf = get_time_unit_conversions(input_time_units)["conv"]["seconds"]  # sec / unit_from
    st = get_time_unit_conversions(output_time_units)["conv"]["seconds"]    # sec / unit_to
    return sf / st

def tconvert(value: float, input_time_units: str, output_time_units: str) -> float:
    return value * time_factor(input_time_units, output_time_units)

def seconds_per(unit: str) -> float:
    """Return seconds in one <unit> (unit aliases supported)."""
    return get_time_unit_conversions(normalize_time_unit(unit))["conv"]["seconds"]
convert_time = tconvert

