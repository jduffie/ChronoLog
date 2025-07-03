import math
import requests
import streamlit as st
import time
from geopy.distance import geodesic
from typing import List, Tuple, Dict, Any


class MappingModel:
    def __init__(self):
        self.points: List[List[float]] = []
        self.elevations_m: List[float] = []
        self.map_center: List[float] = [36.222278, -78.051833]
        self.zoom_level: int = 13

    def add_point(self, lat: float, lng: float) -> None:
        """Add a new point if less than 2 points exist."""
        if len(self.points) < 2:
            self.points.append([lat, lng])

    def reset_points(self) -> None:
        """Clear all points and elevations."""
        self.points = []
        self.elevations_m = []

    def get_elevation(self, lat: float, lng: float) -> float:
        """Get elevation in meters from Open Elevation API."""
        try:
            url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lng}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            elevation_m = data['results'][0]['elevation']
            return elevation_m
        except Exception:
            return 0.0

    def fetch_missing_elevations(self) -> None:
        """Fetch elevation data for points that don't have it yet."""
        for i in range(len(self.elevations_m), len(self.points)):
            point = self.points[i]
            elevation_m = self.get_elevation(point[0], point[1])
            self.elevations_m.append(elevation_m)

    def calculate_bearing(self, point_a: List[float], point_b: List[float]) -> float:
        """Calculate bearing/azimuth from point A to point B."""
        lat1, lon1 = math.radians(point_a[0]), math.radians(point_a[1])
        lat2, lon2 = math.radians(point_b[0]), math.radians(point_b[1])
        dLon = lon2 - lon1
        x = math.sin(dLon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
        initial_bearing = math.atan2(x, y)
        return (math.degrees(initial_bearing) + 360) % 360

    def calculate_measurements(self) -> Dict[str, Any]:
        """Calculate all measurements when two points are available."""
        if len(self.points) != 2 or len(self.elevations_m) != 2:
            return self._empty_measurements()

        p1, p2 = self.points[0], self.points[1]
        distance_m = geodesic(p1, p2).m
        azimuth = self.calculate_bearing(p1, p2)
        
        # Calculate elevation angle
        elevation_diff_m = self.elevations_m[1] - self.elevations_m[0]
        elevation_angle = math.degrees(math.atan2(elevation_diff_m, distance_m))

        # Get address GeoJSON for start position
        address_data = self.get_address_geojson_with_rate_limit(p1[0], p1[1])

        return {
            "start_lat": f"{p1[0]:.6f}",
            "start_lon": f"{p1[1]:.6f}",
            "start_alt": f"{self.elevations_m[0]:.1f}",
            "end_lat": f"{p2[0]:.6f}",
            "end_lon": f"{p2[1]:.6f}",
            "end_alt": f"{self.elevations_m[1]:.1f}",
            "distance": f"{distance_m:.2f} m",
            "azimuth": f"{azimuth:.2f}°",
            "elevation_angle": f"{elevation_angle:.2f}°",
            "address_geojson": address_data.get('geojson', {}),
            "display_name": address_data.get('display_name', ''),
        }

    def get_partial_measurements(self) -> Dict[str, Any]:
        """Get measurements with partial data when only one point exists."""
        measurements = self._empty_measurements()
        
        if len(self.points) >= 1 and len(self.elevations_m) >= 1:
            p1 = self.points[0]
            
            # Get address GeoJSON for start position
            address_data = self.get_address_geojson_with_rate_limit(p1[0], p1[1])
            
            measurements.update({
                "start_lat": f"{p1[0]:.6f}",
                "start_lon": f"{p1[1]:.6f}",
                "start_alt": f"{self.elevations_m[0]:.1f}",
                "address_geojson": address_data.get('geojson', {}),
                "display_name": address_data.get('display_name', ''),
            })
        
        return measurements

    def _empty_measurements(self) -> Dict[str, Any]:
        """Return empty measurements template."""
        return {
            "start_lat": "",
            "start_lon": "",
            "start_alt": "",
            "end_lat": "",
            "end_lon": "",
            "end_alt": "",
            "distance": "",
            "azimuth": "",
            "elevation_angle": "",
            "address_geojson": {},
            "display_name": "",
        }

    def update_map_state(self, center: Dict[str, float] = None, zoom: int = None) -> None:
        """Update map center and zoom level."""
        if center:
            self.map_center = [center["lat"], center["lng"]]
        if zoom is not None:
            self.zoom_level = zoom

    def needs_elevation_fetch(self) -> bool:
        """Check if elevation data needs to be fetched."""
        return len(self.points) > 0 and len(self.elevations_m) < len(self.points)

    @staticmethod
    @st.cache_data
    def fetch_address_geojson(lat: float, lon: float) -> Dict[str, any]:
        """Fetch GeoJSON response from coordinates using reverse geocoding API with caching."""
        try:
            # Use OpenStreetMap Nominatim API for reverse geocoding
            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                'format': 'geojson',
                'lat': lat,
                'lon': lon,
                'zoom': 18,
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'ChronoLog-App/1.0 (mapping application)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            # pretty print the response
            import json
            print(f"Reverse geocoding API response for {lat}, {lon}:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("=" * 50)

            # Return the full GeoJSON with metadata
            return {
                'lat': lat,
                'lon': lon,
                'geojson': data,
                'display_name': data.get('features', [{}])[0].get('properties', {}).get('display_name', '') if data.get('features') else ''
            }
                
        except Exception as e:
            print(f"Error fetching address: {e}")
            return {
                'lat': lat,
                'lon': lon,
                'geojson': {},
                'display_name': ''
            }

    def get_address_geojson_with_rate_limit(self, lat: float, lon: float) -> Dict[str, any]:
        """Get address GeoJSON with rate limiting."""
        # Add a small delay to respect API rate limits
        time.sleep(0.1)
        return self.fetch_address_geojson(lat, lon)