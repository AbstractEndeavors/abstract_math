#src/utils/velocity_utils.py
from ..imports import *
from ..constants import *

def distance_per_time_to_mps(v: float, dist_units: str, time_units: str) -> float:
    """
    Convert <v> in (<dist_units>/<time_units>) to m/s.
    """
    # distance: unit -> meters
    norm_dist_unit = normalize_distance_unit(dist_units)   # <-- was normalize_time_unit
    meters_per_unit = get_distance_unit_conversions(norm_dist_unit)["conv"]["meters"]
    v_meters_per_timeunit = mul(v, meters_per_unit)

    # time: timeunit -> seconds
    sec_per_time = seconds_per(time_units)                 # from time_constants.py
    return div(v_meters_per_timeunit, sec_per_time)

def mps_to_distance_per_time(v_mps: float, dist_units: str, time_units: str) -> float:
    """
    Convert m/s to <dist_units>/<time_units>.
    """
    norm_dist_unit = normalize_distance_unit(dist_units)
    meters_per_unit = get_distance_unit_conversions(norm_dist_unit)["conv"]["meters"]
    v_units_per_sec = div(v_mps, meters_per_unit)          # [dist_units / s]
    sec_per_time = seconds_per(time_units)
    return mul(v_units_per_sec, sec_per_time)              # [dist_units / time_units]




def get_velocity_conversioin(
    velocity,
    input_time: str = DEFAULT_TIME,
    input_units: str = DEFAULT_UNITS,
    output_units: str = DEFAULT_UNITS,
    output_time: str = DEFAULT_TIME,
    ):
    v0_mps = distance_per_time_to_mps(v=velocity, dist_units=input_units, time_units=input_time)
    v0_unit_p_time = mps_to_distance_per_time(v_mps=v0_mps, dist_units=output_units, time_units=output_time)
    return v0_unit_p_time

def normalized_velocity_conversioin(
    velocity,
    input_time: str = DEFAULT_TIME,
    input_units: str = DEFAULT_UNITS
    ):
    v0_mps = get_velocity_conversioin(
        velocity=velocity,
        input_time=input_time,
        input_units=input_units
        )
    return v0_mps
