#src/constants/time_constants.py
# --- Time unit schema (seconds-per-unit) ---
second = 1.0
minute = 60.0 * second
hour   = 60.0 * minute
day    = 24.0 * hour

SECONDS = {"strings": ['s', 'sec', 'secs', 'second', 'seconds'],
           "conv": {"seconds": 1.0}}
MINUTES = {"strings": ['min', 'mins', 'minute', 'minutes'],
           "conv": {"seconds": minute}}
HOURS   = {"strings": ['h', 'hr', 'hrs', 'hour', 'hours'],
           "conv": {"seconds": hour}}
DAYS    = {"strings": ['d', 'day', 'days'],
           "conv": {"seconds": day}}

TIME_CONVERSIONS = {
    "seconds": SECONDS,
    "minutes": MINUTES,
    "hours":   HOURS,
    "days":    DAYS,
}
ALL_TIME_UNITS = ("seconds", "minutes", "hours", "days")
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

def time_factor(time_unit_from: str, time_unit_to: str) -> float:
    """
    multiplicative factor s.t.
      value_in_to = value_in_from * _time_factor(unit_from, unit_to)

    seconds per 1 unit_from  /  seconds per 1 unit_to
    """
    sf = get_time_unit_conversions(time_unit_from)["conv"]["seconds"]  # sec / unit_from
    st = get_time_unit_conversions(time_unit_to)["conv"]["seconds"]    # sec / unit_to
    return sf / st

def tconvert(value: float, time_unit_from: str, time_unit_to: str) -> float:
    return value * time_factor(time_unit_from, time_unit_to)

def seconds_per(unit: str) -> float:
    """Return seconds in one <unit> (unit aliases supported)."""
    return get_time_unit_conversions(normalize_time_unit(unit))["conv"]["seconds"]
convert_time = tconvert

