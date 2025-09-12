"""
UI Display Formatters

Handles user preference checking, unit conversion calls, and string formatting
for display in the UI. Separates conversion logic from presentation logic.
"""
from typing import Optional
from .unit_conversions import (
    mps_to_fps, celsius_to_fahrenheit, hpa_to_inhg, 
    mps_to_mph, meters_to_feet, joules_to_ftlb, kgms_to_grainft
)


def format_speed(speed_mps: Optional[float], user_unit_system: str = "Imperial") -> str:
    """Format speed for display based on user preferences"""
    if speed_mps is None:
        return "N/A"
    
    if user_unit_system == "Imperial":
        speed_fps = mps_to_fps(speed_mps)
        return f"{speed_fps:.1f} fps"
    else:
        return f"{speed_mps:.2f} m/s"


def format_delta_speed(delta_mps: Optional[float], user_unit_system: str = "Imperial") -> str:
    """Format delta speed for display based on user preferences"""
    if delta_mps is None:
        return "N/A"
        
    if user_unit_system == "Imperial":
        delta_fps = mps_to_fps(delta_mps)
        return f"{delta_fps:+.1f} fps"
    else:
        return f"{delta_mps:+.2f} m/s"


def format_energy(energy_j: Optional[float], user_unit_system: str = "Imperial") -> str:
    """Format kinetic energy for display based on user preferences"""
    if energy_j is None:
        return "N/A"
        
    if user_unit_system == "Imperial":
        energy_ftlb = joules_to_ftlb(energy_j)
        return f"{energy_ftlb:.1f} ft-lb"
    else:
        return f"{energy_j:.1f} J"


def format_temperature(temp_c: Optional[float], user_unit_system: str = "Imperial") -> str:
    """Format temperature for display based on user preferences"""
    if temp_c is None:
        return "N/A"
        
    if user_unit_system == "Imperial":
        temp_f = celsius_to_fahrenheit(temp_c)
        return f"{temp_f:.1f}°F"
    else:
        return f"{temp_c:.1f}°C"


def format_pressure(pressure_hpa: Optional[float], user_unit_system: str = "Imperial") -> str:
    """Format pressure for display based on user preferences"""
    if pressure_hpa is None:
        return "N/A"
        
    if user_unit_system == "Imperial":
        pressure_inhg = hpa_to_inhg(pressure_hpa)
        return f"{pressure_inhg:.2f} inHg"
    else:
        return f"{pressure_hpa:.1f} hPa"


def format_wind_speed(wind_mps: Optional[float], user_unit_system: str = "Imperial") -> str:
    """Format wind speed for display based on user preferences"""
    if wind_mps is None:
        return "N/A"
        
    if user_unit_system == "Imperial":
        wind_mph = mps_to_mph(wind_mps)
        return f"{wind_mph:.1f} mph"
    else:
        return f"{wind_mps:.1f} m/s"


def format_altitude(altitude_m: Optional[float], user_unit_system: str = "Imperial") -> str:
    """Format altitude for display based on user preferences"""
    if altitude_m is None:
        return "N/A"
        
    if user_unit_system == "Imperial":
        altitude_ft = meters_to_feet(altitude_m)
        return f"{altitude_ft:.0f} ft"
    else:
        return f"{altitude_m:.0f} m"


def format_power_factor(pf_kgms: Optional[float], user_unit_system: str = "Imperial") -> str:
    """Format power factor for display based on user preferences"""
    if pf_kgms is None:
        return "N/A"
        
    if user_unit_system == "Imperial":
        pf_grainft = kgms_to_grainft(pf_kgms)
        return f"{pf_grainft:.0f} gr⋅ft/s"
    else:
        return f"{pf_kgms:.2f} kg⋅m/s"


def format_velocity_range(min_mps: Optional[float], max_mps: Optional[float], 
                         user_unit_system: str = "Imperial") -> str:
    """Format velocity range for display based on user preferences"""
    if min_mps is None or max_mps is None:
        return "N/A"
        
    if user_unit_system == "Imperial":
        min_fps = mps_to_fps(min_mps)
        max_fps = mps_to_fps(max_mps)
        range_fps = max_fps - min_fps
        return f"{range_fps:.0f} fps"
    else:
        range_mps = max_mps - min_mps
        return f"{range_mps:.1f} m/s"


def format_average_speed(avg_mps: Optional[float], user_unit_system: str = "Imperial") -> str:
    """Format average speed for display based on user preferences"""
    if avg_mps is None:
        return "N/A"
    
    if user_unit_system == "Imperial":
        avg_fps = mps_to_fps(avg_mps)
        return f"{avg_fps:.0f} fps"
    else:
        return f"{avg_mps:.1f} m/s"


def format_std_dev(std_dev_mps: Optional[float], user_unit_system: str = "Imperial") -> str:
    """Format standard deviation for display based on user preferences"""
    if std_dev_mps is None:
        return "N/A"
        
    if user_unit_system == "Imperial":
        std_dev_fps = mps_to_fps(std_dev_mps)
        return f"{std_dev_fps:.1f} fps"
    else:
        return f"{std_dev_mps:.2f} m/s"