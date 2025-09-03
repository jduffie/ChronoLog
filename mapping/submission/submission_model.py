from typing import Any, Dict, List


class SubmissionModel:
    """Model for user range submission management."""

    def get_user_range_count(self, user_id: str, supabase_client) -> int:
        """Get the count of ranges submitted by a user."""
        try:
            result = (
                supabase_client.table("ranges_submissions")
                .select("id")
                .eq("user_id", user_id)
                .execute()
            )
            return len(result.data) if result.data else 0
        except Exception as e:
            print(f"Error getting user range count: {e}")
            return 0

    def get_user_ranges(self, user_id: str, supabase_client) -> List[Dict[str, Any]]:
        """Get all ranges submitted by a user."""
        try:
            result = (
                supabase_client.table("ranges_submissions")
                .select(
                    "id, range_name, range_description, start_lat, start_lon, end_lat, end_lon, distance_m, azimuth_deg, elevation_angle_deg, display_name, submitted_at, status, review_reason, start_altitude_m, end_altitude_m, address_geojson"
                )
                .eq("user_id", user_id)
                .order("submitted_at", desc=True)
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting user ranges: {e}")
            return []

    def delete_user_ranges(
        self, user_id: str, range_ids: List[str], supabase_client
    ) -> bool:
        """Delete selected ranges for a user."""
        try:
            deleted_count = 0
            for range_id in range_ids:
                print(
                    f"Attempting to delete range ID: {range_id} for user: {user_id}"
                )

                # First check if the range exists and belongs to the user
                check_result = (
                    supabase_client.table("ranges_submissions")
                    .select("id")
                    .eq("id", range_id)
                    .eq("user_id", user_id)
                    .execute()
                )
                print(f"Range exists check: {check_result.data}")

                if not check_result.data:
                    print(
                        f"Range {range_id} not found or doesn't belong to user {user_id}"
                    )
                    continue

                # Perform the deletion
                result = (
                    supabase_client.table("ranges_submissions")
                    .delete()
                    .eq("id", range_id)
                    .eq("user_id", user_id)
                    .execute()
                )
                print(f"Delete result for {range_id}: {result}")

                # Check if deletion was successful
                if hasattr(result, "data") and result.data is not None:
                    deleted_count += 1
                    print(f"Successfully deleted range {range_id}")
                elif hasattr(result, "count") and result.count > 0:
                    deleted_count += 1
                    print(f"Successfully deleted range {range_id} (count method)")
                else:
                    print(
                        f"Failed to delete range with ID: {range_id} - result: {result}"
                    )

            print(f"Total ranges deleted: {deleted_count} out of {len(range_ids)}")
            return deleted_count > 0

        except Exception as e:
            print(f"Error deleting ranges: {e}")
            import traceback

            traceback.print_exc()
            return False

    def get_user_submission_by_id(
        self, user_id: str, submission_id: str, supabase_client
    ) -> Dict[str, Any]:
        """Get a specific submission by ID for a user."""
        try:
            result = (
                supabase_client.table("ranges_submissions")
                .select("*")
                .eq("id", submission_id)
                .eq("user_id", user_id)
                .execute()
            )
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error getting user submission: {e}")
            return {}

    def update_user_submission(
        self,
        user_id: str,
        submission_id: str,
        updates: Dict[str, Any],
        supabase_client,
    ) -> bool:
        """Update a user's submission."""
        try:
            result = (
                supabase_client.table("ranges_submissions")
                .update(updates)
                .eq("id", submission_id)
                .eq("user_id", user_id)
                .execute()
            )

            if result.data:
                print(f"Successfully updated submission {submission_id}")
                return True
            else:
                print(f"Failed to update submission {submission_id}")
                return False

        except Exception as e:
            print(f"Error updating submission: {e}")
            return False
