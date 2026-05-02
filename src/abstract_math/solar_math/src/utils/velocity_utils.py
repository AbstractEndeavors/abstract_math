# src/utils/velocity_utils.py
from ..imports import *
from ..constants import *


def distance_per_time_to_mps(
    v: float,
    input_dist_units: str,
    input_time_units: str,
    to_dict=False
    ) -> float:
    """
    Convert <v> in (<dist_unit>/<time_unit>) to m/s.
    """
    norm_dist_unit = normalize_distance_unit(input_dist_units)
    meters_per_unit = get_distance_unit_conversions(norm_dist_unit)["conv"]["meters"]

    v_meters_per_timeunit = mul(v, meters_per_unit)

    sec_per_time = seconds_per(input_time_units)
    distance_per_mps =  div(v_meters_per_timeunit, sec_per_time)

    if not to_dict:
        return distance_per_mps

    return {
            "input": {
                "input_dist_units": input_dist_units,
                "input_time_units": input_time_units,
                "units": f"{input_dist_units}/{input_time_units}",
                "velocity": v,

            },
            "output": {
                "velocity": distance_per_mps ,
                "output_dist_units": "m",
                "output_time_units": "s",
                "units": "m/s",
            }
        }

def mps_to_distance_per_time(v_mps: float,
                             output_dist_units: str,
                             output_time_units: str,
                             to_dict=False
                             ) -> float:
    """
    Convert m/s to <dist_unit>/<time_unit>.
    """
    norm_dist_unit = normalize_distance_unit(output_dist_units)
    meters_per_unit = get_distance_unit_conversions(norm_dist_unit)["conv"]["meters"]

    v_unit_per_sec = div(v_mps, meters_per_unit)
    sec_per_time = seconds_per(output_time_units)
    distance_per_time = mul(v_unit_per_sec, sec_per_time)

    if not to_dict:
        return distance_per_time

    return {
            "input": {
               
                "input_dist_units": "m",
                "input_time_units": "s",
                "units": "m/s",
                "velocity": v_mps,

            },
            "output": {
                "velocity": distance_per_time,
                "output_dist_units": output_dist_units,
                "output_time_units": output_time_units,
                "units": f"{output_dist_units}/{output_time_units}",
            }
        }

def get_velocity_conversion(
    velocity,
    input_dist_units: str = DEFAULT_DIST_UNIT,
    input_time_units: str = DEFAULT_TIME_UNIT,
    output_dist_units: str = DEFAULT_DIST_UNIT,
    output_time_units: str = DEFAULT_TIME_UNIT,
    to_dict: bool = False,
):
    """
    Convert velocity from input distance/time units to output distance/time units.

    If to_dict is False:
        returns the converted numeric value.

    If to_dict is True:
        returns a metadata-rich dictionary including input/output units.
    """
    v0_mps = distance_per_time_to_mps(
        v=velocity,
        input_dist_units=input_dist_units,
        input_time_units=input_time_units,
    )

    converted_velocity = mps_to_distance_per_time(
        v_mps=v0_mps,
        output_dist_units=output_dist_units,
        output_time_units=output_time_units,
    )

    if not to_dict:
        return converted_velocity

    return {
        "input": {
            "velocity": velocity,
            "dist_unit": input_dist_units,
            "time_unit": input_time_units,
            "units": f"{input_dist_units}/{input_time_units}",
        },
        "normalized": {
            "velocity": v0_mps,
            "dist_unit": "m",
            "time_unit": "s",
            "units": "m/s",
        },
        "output": {
            "velocity": converted_velocity,
            "dist_unit": output_dist_units,
            "time_unit": output_time_units,
            "unitsd": f"{output_dist_units}/{output_time_units}",
        },
    }


def normalized_velocity_conversion(
    velocity,
    input_time_units: str = DEFAULT_TIME_UNIT,
    input_dist_units: str = DEFAULT_DIST_UNIT,
    to_dict: bool = False,
):
    """
    Normalize a velocity into m/s.

    If to_dict is False:
        returns the numeric m/s value.

    If to_dict is True:
        returns a metadata-rich dictionary.
    """
    v0_mps = get_velocity_conversion(
        velocity=velocity,
        input_time_units=input_time_units,
        input_dist_units=input_dist_units,
        output_dist_units="m",
        output_time_units="s",
        to_dict=False,
    )

    if not to_dict:
        return v0_mps

    return {
        "input": {
            "velocity": velocity,
            "input_dist_units": input_dist_units,
            "input_time_units": input_time_units,
            "units": f"{input_dist_units}/{input_time_units}",
        },
        "output": {
            "velocity": v0_mps,
            "output_dist_units": "m",
            "output_time_units": "s",
            "units": "m/s",
        },
    }
