"""
Pure Unit Conversion Math

Contains only mathematical conversion functions with no formatting or UI logic.
All functions convert from metric (database storage) to imperial (display).
"""
from typing import Optional


def mps_to_fps(speed_mps: Optional[float]) -> Optional[float]:
    """Convert meters per second to feet per second"""
    return speed_mps / 0.3048 if speed_mps is not None else None


def celsius_to_fahrenheit(temp_c: Optional[float]) -> Optional[float]:
    """Convert Celsius to Fahrenheit"""
    return (temp_c * 9.0/5.0) + 32 if temp_c is not None else None


def hpa_to_inhg(pressure_hpa: Optional[float]) -> Optional[float]:
    """Convert hectopascals to inches of mercury"""
    return pressure_hpa / 33.8639 if pressure_hpa is not None else None


def mps_to_mph(wind_mps: Optional[float]) -> Optional[float]:
    """Convert meters per second to miles per hour"""
    return wind_mps * 2.237 if wind_mps is not None else None


def meters_to_feet(distance_m: Optional[float]) -> Optional[float]:
    """Convert meters to feet"""
    return distance_m / 0.3048 if distance_m is not None else None


def joules_to_ftlb(energy_j: Optional[float]) -> Optional[float]:
    """Convert joules to foot-pounds"""
    return energy_j / 1.35582 if energy_j is not None else None


def kgms_to_grainft(pf_kgms: Optional[float]) -> Optional[float]:
    """Convert kg⋅m/s to grain⋅ft/s"""
    if pf_kgms is None:
        return None
    # 1 kg = 15432.36 grains, 1 m = 3.28084 ft
    return pf_kgms * 15432.36 * 3.28084


# Reverse conversions (Imperial to Metric) for editing functionality

def fps_to_mps(speed_fps: Optional[float]) -> Optional[float]:
    """Convert feet per second to meters per second"""
    return speed_fps * 0.3048 if speed_fps is not None else None


def fahrenheit_to_celsius(temp_f: Optional[float]) -> Optional[float]:
    """Convert Fahrenheit to Celsius"""
    return (temp_f - 32) * 5.0/9.0 if temp_f is not None else None


def inhg_to_hpa(pressure_inhg: Optional[float]) -> Optional[float]:
    """Convert inches of mercury to hectopascals"""
    return pressure_inhg * 33.8639 if pressure_inhg is not None else None


def mph_to_mps(wind_mph: Optional[float]) -> Optional[float]:
    """Convert miles per hour to meters per second"""
    return wind_mph / 2.237 if wind_mph is not None else None


def feet_to_meters(distance_ft: Optional[float]) -> Optional[float]:
    """Convert feet to meters"""
    return distance_ft * 0.3048 if distance_ft is not None else None


def ftlb_to_joules(energy_ftlb: Optional[float]) -> Optional[float]:
    """Convert foot-pounds to joules"""
    return energy_ftlb * 1.35582 if energy_ftlb is not None else None


def grainft_to_kgms(pf_grainft: Optional[float]) -> Optional[float]:
    """Convert grain⋅ft/s to kg⋅m/s"""
    if pf_grainft is None:
        return None
    # 1 kg = 15432.36 grains, 1 m = 3.28084 ft
    return pf_grainft / (15432.36 * 3.28084)