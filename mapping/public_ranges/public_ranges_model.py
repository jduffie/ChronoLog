from typing import Any, Dict, List


class PublicRangesModel:
    """Model for public ranges management."""

    def get_public_ranges(self, supabase_client) -> List[Dict[str, Any]]:
        """Get all public ranges from the ranges table."""
        try:
            result = (
                supabase_client.table("ranges") .select(
                    "id, range_name, range_description, start_lat, start_lon, end_lat, end_lon, "
                    "start_altitude_m, end_altitude_m, distance_m, azimuth_deg, elevation_angle_deg, "
                    "display_name, submitted_at, address_geojson") .order(
                    "submitted_at", desc=True) .execute())
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting public ranges: {e}")
            return []

    def get_public_range_by_id(
            self, range_id: str, supabase_client) -> Dict[str, Any]:
        """Get a specific public range by ID."""
        try:
            result = (supabase_client.table("ranges").select(
                "*").eq("id", range_id).execute())
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error getting public range by ID: {e}")
            return {}

    def delete_public_range(self, range_id: str, supabase_client) -> bool:
        """Delete a range from the public ranges table."""
        try:
            result = (
                supabase_client.table("ranges").delete().eq(
                    "id", range_id).execute())
            if hasattr(result, "data") and result.data is not None:
                print(f"Successfully deleted public range {range_id}")
                return True
            elif hasattr(result, "count") and result.count > 0:
                print(
                    f"Successfully deleted public range {range_id} (count method)")
                return True
            else:
                print(f"Failed to delete public range {range_id}")
                return False
        except Exception as e:
            print(f"Error deleting public range: {e}")
            return False

    def search_public_ranges(
        self, search_term: str, supabase_client
    ) -> List[Dict[str, Any]]:
        """Search public ranges by name or description."""
        try:
            result = (
                supabase_client.table("ranges")
                .select(
                    "id, range_name, range_description, start_lat, start_lon, end_lat, end_lon, "
                    "start_altitude_m, end_altitude_m, distance_m, azimuth_deg, elevation_angle_deg, "
                    "display_name, submitted_at, address_geojson"
                )
                .or_(
                    f"range_name.ilike.%{search_term}%,range_description.ilike.%{search_term}%,display_name.ilike.%{search_term}%"
                )
                .order("submitted_at", desc=True)
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            print(f"Error searching public ranges: {e}")
            return []

    def get_ranges_by_location(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        supabase_client,
    ) -> List[Dict[str, Any]]:
        """Get public ranges within a geographic bounding box."""
        try:
            result = (
                supabase_client.table("ranges") .select(
                    "id, range_name, range_description, start_lat, start_lon, end_lat, end_lon, "
                    "start_altitude_m, end_altitude_m, distance_m, azimuth_deg, elevation_angle_deg, "
                    "display_name, submitted_at, address_geojson") .gte(
                    "start_lat",
                    min_lat) .lte(
                    "start_lat",
                    max_lat) .gte(
                    "start_lon",
                    min_lon) .lte(
                        "start_lon",
                        max_lon) .order(
                            "submitted_at",
                    desc=True) .execute())
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting ranges by location: {e}")
            return []

    def get_ranges_by_distance(
        self, min_distance: float, max_distance: float, supabase_client
    ) -> List[Dict[str, Any]]:
        """Get public ranges filtered by distance range."""
        try:
            result = (
                supabase_client.table("ranges") .select(
                    "id, range_name, range_description, start_lat, start_lon, end_lat, end_lon, "
                    "start_altitude_m, end_altitude_m, distance_m, azimuth_deg, elevation_angle_deg, "
                    "display_name, submitted_at, address_geojson") .gte(
                    "distance_m", min_distance) .lte(
                    "distance_m", max_distance) .order(
                    "distance_m", desc=False) .execute())
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting ranges by distance: {e}")
            return []

    def get_range_statistics(self, supabase_client) -> Dict[str, Any]:
        """Get statistics about public ranges."""
        try:
            result = supabase_client.table(
                "ranges").select("distance_m").execute()
            if not result.data:
                return {}

            distances = [r["distance_m"]
                         for r in result.data if r["distance_m"] is not None]
            if not distances:
                return {}

            return {
                "total_ranges": len(result.data),
                "min_distance_m": min(distances),
                "max_distance_m": max(distances),
                "avg_distance_m": sum(distances) / len(distances),
                "total_distance_m": sum(distances),
            }
        except Exception as e:
            print(f"Error getting range statistics: {e}")
            return {}

    def add_public_range(
            self, range_data: Dict[str, Any], supabase_client) -> bool:
        """Add a new public range directly (admin function)."""
        try:
            result = supabase_client.table(
                "ranges").insert(range_data).execute()
            if result.data:
                print(
                    f"Successfully added public range: {range_data.get('range_name', 'Unknown')}"
                )
                return True
            else:
                print(
                    f"Failed to add public range: {range_data.get('range_name', 'Unknown')}"
                )
                return False
        except Exception as e:
            print(f"Error adding public range: {e}")
            return False

    def update_public_range(
        self, range_id: str, updates: Dict[str, Any], supabase_client
    ) -> bool:
        """Update a public range."""
        try:
            result = (
                supabase_client.table("ranges")
                .update(updates)
                .eq("id", range_id)
                .execute()
            )
            if result.data:
                print(f"Successfully updated public range {range_id}")
                return True
            else:
                print(f"Failed to update public range {range_id}")
                return False
        except Exception as e:
            print(f"Error updating public range: {e}")
            return False
