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
                        "address": start_address_data.get('display_name', ''),
                        "altitude_m": start_alt,
                        "azimuth_deg": azimuth,
                        "elevation_angle_deg": elevation_angle,
                        "elevation_change_m": elevation_diff_m
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
                        "address": end_address_data.get('display_name', ''),
                        "altitude_m": end_alt
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

        return {
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
                "start_address": address_data.get('display_name', ''),
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
    
    def get_user_range_count(self, user_email: str, supabase_client) -> int:
        """Get the count of ranges submitted by a user."""
        try:
            result = supabase_client.table("ranges_submissions").select("id").eq("user_email", user_email).execute()
            return len(result.data) if result.data else 0
        except Exception as e:
            print(f"Error getting user range count: {e}")
            return 0

    def get_user_ranges(self, user_email: str, supabase_client) -> List[Dict[str, Any]]:
        """Get all ranges submitted by a user."""
        try:
            result = supabase_client.table("ranges_submissions").select(
                "id, range_name, range_description, start_lat, start_lon, end_lat, end_lon, distance_m, azimuth_deg, elevation_angle_deg, display_name, submitted_at, status, review_reason, start_altitude_m, end_altitude_m"
            ).eq("user_email", user_email).order("submitted_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting user ranges: {e}")
            return []

    def delete_user_ranges(self, user_email: str, range_ids: List[str], supabase_client) -> bool:
        """Delete selected ranges for a user."""
        try:
            deleted_count = 0
            for range_id in range_ids:
                print(f"Attempting to delete range ID: {range_id} for user: {user_email}")
                
                # First check if the range exists and belongs to the user
                check_result = supabase_client.table("ranges_submissions").select("id").eq("id", range_id).eq("user_email", user_email).execute()
                print(f"Range exists check: {check_result.data}")
                
                if not check_result.data:
                    print(f"Range {range_id} not found or doesn't belong to user {user_email}")
                    continue
                
                # Perform the deletion
                result = supabase_client.table("ranges_submissions").delete().eq("id", range_id).eq("user_email", user_email).execute()
                print(f"Delete result for {range_id}: {result}")
                
                # Check if deletion was successful
                if hasattr(result, 'data') and result.data is not None:
                    deleted_count += 1
                    print(f"Successfully deleted range {range_id}")
                elif hasattr(result, 'count') and result.count > 0:
                    deleted_count += 1
                    print(f"Successfully deleted range {range_id} (count method)")
                else:
                    print(f"Failed to delete range with ID: {range_id} - result: {result}")
                    
            print(f"Total ranges deleted: {deleted_count} out of {len(range_ids)}")
            return deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting ranges: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_all_pending_submissions(self, supabase_client) -> List[Dict[str, Any]]:
        """Get all range submissions that are pending review."""
        try:
            result = supabase_client.table("ranges_submissions").select(
                "id, user_email, range_name, range_description, start_lat, start_lon, end_lat, end_lon, "
                "start_altitude_m, end_altitude_m, distance_m, azimuth_deg, elevation_angle_deg, "
                "display_name, submitted_at, status, review_reason"
            ).eq("status", "Under Review").order("submitted_at", desc=False).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting pending submissions: {e}")
            return []

    def approve_submission(self, submission_id: str, review_reason: str, supabase_client) -> bool:
        """Approve a submission and copy it to the ranges table."""
        try:
            # First get the submission details
            submission_result = supabase_client.table("ranges_submissions").select("*").eq("id", submission_id).execute()
            if not submission_result.data:
                print(f"Submission {submission_id} not found")
                return False
            
            submission = submission_result.data[0]
            
            # Copy to ranges table (without id, status, review_reason)
            range_data = {
                "user_email": submission["user_email"],
                "range_name": submission["range_name"],
                "range_description": submission["range_description"],
                "start_lat": submission["start_lat"],
                "start_lon": submission["start_lon"],
                "start_altitude_m": submission["start_altitude_m"],
                "end_lat": submission["end_lat"],
                "end_lon": submission["end_lon"],
                "end_altitude_m": submission["end_altitude_m"],
                "distance_m": submission["distance_m"],
                "azimuth_deg": submission["azimuth_deg"],
                "elevation_angle_deg": submission["elevation_angle_deg"],
                "address_geojson": submission["address_geojson"],
                "display_name": submission["display_name"],
                "submitted_at": submission["submitted_at"]
            }
            
            # Insert into ranges table
            ranges_result = supabase_client.table("ranges").insert(range_data).execute()
            if not ranges_result.data:
                print("Failed to insert into ranges table")
                return False
            
            # Update submission status
            update_result = supabase_client.table("ranges_submissions").update({
                "status": "Accepted",
                "review_reason": review_reason
            }).eq("id", submission_id).execute()
            
            if update_result.data:
                print(f"Successfully approved submission {submission_id}")
                return True
            else:
                print(f"Failed to update submission status for {submission_id}")
                return False
                
        except Exception as e:
            print(f"Error approving submission: {e}")
            return False

    def deny_submission(self, submission_id: str, review_reason: str, supabase_client) -> bool:
        """Deny a submission with reason."""
        try:
            result = supabase_client.table("ranges_submissions").update({
                "status": "Denied",
                "review_reason": review_reason
            }).eq("id", submission_id).execute()
            
            if result.data:
                print(f"Successfully denied submission {submission_id}")
                return True
            else:
                print(f"Failed to deny submission {submission_id}")
                return False
                
        except Exception as e:
            print(f"Error denying submission: {e}")
            return False

    def reset_submission_status(self, submission_id: str, supabase_client) -> bool:
        """Reset submission status back to Under Review."""
        try:
            result = supabase_client.table("ranges_submissions").update({
                "status": "Under Review",
                "review_reason": None
            }).eq("id", submission_id).execute()
            
            if result.data:
                print(f"Successfully reset status for submission {submission_id}")
                return True
            else:
                print(f"Failed to reset status for submission {submission_id}")
                return False
                
        except Exception as e:
            print(f"Error resetting submission status: {e}")
            return False

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

    def get_public_ranges(self, supabase_client) -> List[Dict[str, Any]]:
        """Get all public ranges from the ranges table."""
        try:
            result = supabase_client.table("ranges").select(
                "id, user_email, range_name, range_description, start_lat, start_lon, end_lat, end_lon, "
                "start_altitude_m, end_altitude_m, distance_m, azimuth_deg, elevation_angle_deg, "
                "display_name, submitted_at"
            ).order("submitted_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting public ranges: {e}")
            return []

    def delete_public_range(self, range_id: str, supabase_client) -> bool:
        """Delete a range from the public ranges table."""
        try:
            result = supabase_client.table("ranges").delete().eq("id", range_id).execute()
            if hasattr(result, 'data') and result.data is not None:
                print(f"Successfully deleted public range {range_id}")
                return True
            elif hasattr(result, 'count') and result.count > 0:
                print(f"Successfully deleted public range {range_id} (count method)")
                return True
            else:
                print(f"Failed to delete public range {range_id}")
                return False
        except Exception as e:
            print(f"Error deleting public range: {e}")
            return False