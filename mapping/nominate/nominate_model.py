import math
import requests
import streamlit as st
from geopy.distance import geodesic
from typing import List, Tuple, Dict, Any


class NominateModel:
    """Model for range nomination functionality including point management and calculations."""
    
    def __init__(self):
        self.points: List[List[float]] = []
        self.elevations_m: List[float] = []
        self.map_center: List[float] = [36.222278, -78.051833]
        self.zoom_level: int = 13
        self._cached_measurements: Dict[str, Any] = None
        self._measurements_cache_key: str = ""
        self._cached_partial_measurements: Dict[str, Any] = None
        self._partial_measurements_cache_key: str = ""

    def add_point(self, lat: float, lng: float) -> None:
        """Add a new point if less than 2 points exist."""
        if len(self.points) < 2:
            self.points.append([lat, lng])

    def reset_points(self) -> None:
        """Clear all points and elevations."""
        self.points = []
        self.elevations_m = []
        # Clear cached measurements
        self._cached_measurements = None
        self._measurements_cache_key = ""
        self._cached_partial_measurements = None
        self._partial_measurements_cache_key = ""

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

        # Create cache key from current state
        cache_key = f"{self.points[0]}-{self.points[1]}-{self.elevations_m[0]}-{self.elevations_m[1]}"
        
        # Return cached result if available and cache key matches
        if self._cached_measurements and self._measurements_cache_key == cache_key:
            return self._cached_measurements

        p1, p2 = self.points[0], self.points[1]
        start_alt, end_alt = self.elevations_m[0], self.elevations_m[1]
        
        # Calculate 2D and 3D distances
        distance_2d_m = geodesic(p1, p2).m
        elevation_diff_m = end_alt - start_alt
        distance_3d_m = math.sqrt(distance_2d_m**2 + elevation_diff_m**2)
        
        azimuth = self.calculate_bearing(p1, p2)
        elevation_angle = math.degrees(math.atan2(elevation_diff_m, distance_2d_m))

        # Get address data for both start and end points
        start_address_data = self.get_address_geojson_with_rate_limit(p1[0], p1[1])
        end_address_data = self.get_address_geojson_with_rate_limit(p2[0], p2[1])

        # Calculate bounding box [min_lon, min_lat, min_alt, max_lon, max_lat, max_alt]
        min_lon = min(p1[1], p2[1])
        max_lon = max(p1[1], p2[1])
        min_lat = min(p1[0], p2[0])
        max_lat = max(p1[0], p2[0])
        min_alt = min(start_alt, end_alt)
        max_alt = max(start_alt, end_alt)
        
        # Create comprehensive GeoJSON FeatureCollection
        geojson_features = {
            "type": "FeatureCollection",
            "bbox": [min_lon, min_lat, min_alt, max_lon, max_lat, max_alt],
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [p1[1], p1[0], start_alt]  # [lon, lat, alt]
                    },
                    "properties": {
                        "type": "firing_position",
                        "altitude_m": start_alt,
                        "azimuth_deg": azimuth,
                        "elevation_angle_deg": elevation_angle,
                        "elevation_change_m": elevation_diff_m,
                        **start_address_data.get('geojson', {}).get('features', [{}])[0].get('properties', {})
                    }
                },
                {
                    "type": "Feature", 
                    "geometry": {
                        "type": "Point",
                        "coordinates": [p2[1], p2[0], end_alt]  # [lon, lat, alt]
                    },
                    "properties": {
                        "type": "target_position",
                        "altitude_m": end_alt,
                        **end_address_data.get('geojson', {}).get('features', [{}])[0].get('properties', {})
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [p1[1], p1[0], start_alt],  # [lon, lat, alt]
                            [p2[1], p2[0], end_alt]     # [lon, lat, alt]
                        ]
                    },
                    "properties": {
                        "type": "range_line",
                        "distance_2d_m": distance_2d_m,
                        "distance_3d_m": distance_3d_m
                    }
                }
            ]
        }

        result = {
            "start_lat": f"{p1[0]:.6f}",
            "start_lon": f"{p1[1]:.6f}",
            "start_alt": f"{start_alt:.1f}",
            "start_address": start_address_data.get('display_name', ''),
            "end_lat": f"{p2[0]:.6f}",
            "end_lon": f"{p2[1]:.6f}",
            "end_alt": f"{end_alt:.1f}",
            "end_address": end_address_data.get('display_name', ''),
            "distance_2d": f"{distance_2d_m:.2f} m",
            "distance_3d": f"{distance_3d_m:.2f} m",
            "azimuth": f"{azimuth:.2f}°",
            "elevation_angle": f"{elevation_angle:.2f}°",
            "elevation_change": f"{elevation_diff_m:.1f} m",
            "address_geojson": geojson_features,
            "display_name": start_address_data.get('display_name', ''),
        }
        
        # Cache the result
        self._cached_measurements = result
        self._measurements_cache_key = cache_key
        
        return result

    def get_partial_measurements(self) -> Dict[str, Any]:
        """Get measurements with partial data when only one point exists."""
        if len(self.points) >= 1 and len(self.elevations_m) >= 1:
            # Create cache key from current state
            p1 = self.points[0]
            cache_key = f"{p1}-{self.elevations_m[0]}"
            
            # Return cached result if available and cache key matches
            if self._cached_partial_measurements and self._partial_measurements_cache_key == cache_key:
                return self._cached_partial_measurements
            
            # Get address GeoJSON for start position
            address_data = self.get_address_geojson_with_rate_limit(p1[0], p1[1])
            
            measurements = self._empty_measurements()
            measurements.update({
                "start_lat": f"{p1[0]:.6f}",
                "start_lon": f"{p1[1]:.6f}",
                "start_alt": f"{self.elevations_m[0]:.1f}",
                "start_address": address_data.get('display_name', ''),
                "address_geojson": address_data.get('geojson', {}),
                "display_name": address_data.get('display_name', ''),
            })
            
            # Cache the result
            self._cached_partial_measurements = measurements
            self._partial_measurements_cache_key = cache_key
            
            return measurements
        
        return self._empty_measurements()

    def _empty_measurements(self) -> Dict[str, Any]:
        """Return empty measurements template."""
        return {
            "start_lat": "",
            "start_lon": "",
            "start_alt": "",
            "start_address": "",
            "end_lat": "",
            "end_lon": "",
            "end_alt": "",
            "end_address": "",
            "distance_2d": "",
            "distance_3d": "",
            "azimuth": "",
            "elevation_angle": "",
            "elevation_change": "",
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
            feature_properties = data.get('features', [{}])[0].get('properties', {}) if data.get('features') else {}
            address_obj = feature_properties.get('address', {})
            
            return {
                'lat': lat,
                'lon': lon,
                'display_name': feature_properties.get('display_name', ''),
                'county': address_obj.get('county', ''),
                'state': address_obj.get('state', ''),
                'country': address_obj.get('country', ''),
                'geojson': data
            }
                
        except Exception as e:
            print(f"Error fetching address: {e}")
            return {
                'lat': lat,
                'lon': lon,
                'display_name': '',
                'county': '',
                'state': '',
                'country': '',
                'geojson': {}
            }

    def get_address_geojson_with_rate_limit(self, lat: float, lon: float) -> Dict[str, any]:
        """Get address GeoJSON with caching (rate limiting handled by Streamlit cache)."""
        return self.fetch_address_geojson(lat, lon)

    def save_range_submission(self, user_email: str, range_name: str, range_description: str, measurements: Dict[str, Any], supabase_client) -> bool:
        """Save range submission to the database."""
        try:
            # Parse numeric values from string representations
            start_lat = float(measurements.get("start_lat", 0))
            start_lon = float(measurements.get("start_lon", 0))
            end_lat = float(measurements.get("end_lat", 0))
            end_lon = float(measurements.get("end_lon", 0))
            
            # Parse altitude values (remove " m" suffix if present)
            start_alt_str = measurements.get("start_alt", "0")
            end_alt_str = measurements.get("end_alt", "0")
            start_alt = float(start_alt_str.replace(" m", "")) if start_alt_str else 0
            end_alt = float(end_alt_str.replace(" m", "")) if end_alt_str else 0
            
            # Parse distance (remove " m" suffix) - use 2D distance for compatibility
            distance_2d_str = measurements.get("distance_2d", "0")
            distance_3d_str = measurements.get("distance_3d", "0")
            distance_2d = float(distance_2d_str.replace(" m", "")) if distance_2d_str else 0
            distance_3d = float(distance_3d_str.replace(" m", "")) if distance_3d_str else 0
            
            # Parse angles (remove "°" suffix)
            azimuth_str = measurements.get("azimuth", "0")
            elevation_str = measurements.get("elevation_angle", "0")
            azimuth = float(azimuth_str.replace("°", "")) if azimuth_str else 0
            elevation_angle = float(elevation_str.replace("°", "")) if elevation_str else 0
            
            # Prepare data for insertion
            range_data = {
                "user_email": user_email,
                "range_name": range_name,
                "range_description": range_description,
                "start_lat": start_lat,
                "start_lon": start_lon,
                "start_altitude_m": start_alt,
                "end_lat": end_lat,
                "end_lon": end_lon,
                "end_altitude_m": end_alt,
                "distance_m": distance_2d,  # Use 2D distance for database compatibility
                "azimuth_deg": azimuth,
                "elevation_angle_deg": elevation_angle,
                "address_geojson": measurements.get("address_geojson", {}),
                "display_name": measurements.get("display_name", ""),
                "status": "Under Review",
                "review_reason": None
            }
            
            # Insert into database
            result = supabase_client.table("ranges_submissions").insert(range_data).execute()
            
            if result.data:
                print(f"Successfully saved range submission: {range_name}")
                return True
            else:
                print(f"Failed to save range submission: {range_name}")
                return False
                
        except Exception as e:
            print(f"Error saving range submission: {e}")
            return False

    def get_user_range_count(self, user_email: str, supabase_client) -> int:
        """Get the count of ranges submitted by a user."""
        try:
            result = supabase_client.table("ranges_submissions").select("id").eq("user_email", user_email).execute()
            return len(result.data) if result.data else 0
        except Exception as e:
            print(f"Error getting user range count: {e}")
            return 0