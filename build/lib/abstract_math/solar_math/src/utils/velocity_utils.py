#src/utils/velocity_utils.py
from ..imports import *
from ..constants import *

def distance_per_time_to_mps(v: float, dist_unit: str, time_unit: str) -> float:
    """
    Convert <v> in (<dist_unit>/<time_unit>) to m/s.
    """
    # distance: unit -> meters
    norm_dist_unit = normalize_distance_unit(
        dist_unit
        )   # <-- was normalize_time_unit
    meters_per_unit = get_distance_unit_conversions(
        norm_dist_unit
        )["conv"]["meters"]
    v_meters_per_timeunit = mul(
        v,
        meters_per_unit
        )

    # time: timeunit -> seconds
    sec_per_time = seconds_per(
        time_unit
        )                 # from time_constants.py
    return div(
        v_meters_per_timeunit,
        sec_per_time
        )

def mps_to_distance_per_time(v_mps: float, dist_unit: str, time_unit: str) -> float:
    """
    Convert m/s to <dist_unit>/<time_unit>.
    """
    norm_dist_unit = normalize_distance_unit(
        dist_unit
        )
    meters_per_unit = get_distance_unit_conversions(
        norm_dist_unit
        )["conv"]["meters"]
    v_unit_per_sec = div(v_mps, meters_per_unit)          # [dist_unit / s]
    sec_per_time = seconds_per(
        time_unit
        )
    return mul(
        v_unit_per_sec,
        sec_per_time
        )              # [dist_unit / time_unit]




def get_velocity_conversion(
    velocity,
    input_time_unit: str = DEFAULT_TIME_UNIT,
    input_dist_unit: str = DEFAULT_DIST_UNIT,
    output_dist_unit: str = DEFAULT_DIST_UNIT,
    output_time_unit: str = DEFAULT_TIME_UNIT,
    ):
    v0_mps = distance_per_time_to_mps(v=velocity, dist_unit=input_dist_unit, time_unit=input_time_unit)
    v0_unit_p_time = mps_to_distance_per_time(v_mps=v0_mps, dist_unit=output_dist_unit, time_unit=output_time_unit)
    return v0_unit_p_time

def normalized_velocity_conversion(
    velocity,
    input_time_unit: str = DEFAULT_TIME_UNIT,
    input_dist_unit: str = DEFAULT_DIST_UNIT,
    ):
    v0_mps = get_velocity_conversion(
        velocity=velocity,
        input_time_unit=input_time_unit,
        input_dist_unit=input_dist_unit
        )
    return v0_mps

