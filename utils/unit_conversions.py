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