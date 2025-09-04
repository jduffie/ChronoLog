from typing import Any, Dict, List


class AdminModel:
    """Model for admin range submission review functionality."""

    def get_all_pending_submissions(
            self, supabase_client) -> List[Dict[str, Any]]:
        """Get all range submissions that are pending review."""
        try:
            result = (
                supabase_client.table("ranges_submissions") .select(
                    "id, user_email, range_name, range_description, start_lat, start_lon, end_lat, end_lon, "
                    "start_altitude_m, end_altitude_m, distance_m, azimuth_deg, elevation_angle_deg, "
                    "display_name, submitted_at, status, review_reason, address_geojson") .eq(
                    "status", "Under Review") .order(
                    "submitted_at", desc=False) .execute())
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting pending submissions: {e}")
            return []

    def get_all_submissions(self, supabase_client) -> List[Dict[str, Any]]:
        """Get all range submissions regardless of status."""
        try:
            result = (
                supabase_client.table("ranges_submissions") .select(
                    "id, user_email, range_name, range_description, start_lat, start_lon, end_lat, end_lon, "
                    "start_altitude_m, end_altitude_m, distance_m, azimuth_deg, elevation_angle_deg, "
                    "display_name, submitted_at, status, review_reason, address_geojson") .order(
                    "submitted_at", desc=True) .execute())
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting all submissions: {e}")
            return []

    def get_submissions_by_status(
        self, status: str, supabase_client
    ) -> List[Dict[str, Any]]:
        """Get submissions filtered by status."""
        try:
            result = (
                supabase_client.table("ranges_submissions") .select(
                    "id, user_email, range_name, range_description, start_lat, start_lon, end_lat, end_lon, "
                    "start_altitude_m, end_altitude_m, distance_m, azimuth_deg, elevation_angle_deg, "
                    "display_name, submitted_at, status, review_reason, address_geojson") .eq(
                    "status", status) .order(
                    "submitted_at", desc=False) .execute())
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting submissions by status: {e}")
            return []

    def approve_submission(
        self, submission_id: str, review_reason: str, supabase_client
    ) -> bool:
        """Approve a submission and copy it to the ranges table."""
        try:
            # First get the submission details
            submission_result = (
                supabase_client.table("ranges_submissions")
                .select("*")
                .eq("id", submission_id)
                .execute()
            )
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
                "submitted_at": submission["submitted_at"],
            }

            # Insert into ranges table
            ranges_result = supabase_client.table(
                "ranges").insert(range_data).execute()
            if not ranges_result.data:
                print("Failed to insert into ranges table")
                return False

            # Update submission status
            update_result = (
                supabase_client.table("ranges_submissions")
                .update({"status": "Accepted", "review_reason": review_reason})
                .eq("id", submission_id)
                .execute()
            )

            if update_result.data:
                print(f"Successfully approved submission {submission_id}")
                return True
            else:
                print(
                    f"Failed to update submission status for {submission_id}")
                return False

        except Exception as e:
            print(f"Error approving submission: {e}")
            return False

    def deny_submission(
        self, submission_id: str, review_reason: str, supabase_client
    ) -> bool:
        """Deny a submission with reason."""
        try:
            result = (
                supabase_client.table("ranges_submissions")
                .update({"status": "Denied", "review_reason": review_reason})
                .eq("id", submission_id)
                .execute()
            )

            if result.data:
                print(f"Successfully denied submission {submission_id}")
                return True
            else:
                print(f"Failed to deny submission {submission_id}")
                return False

        except Exception as e:
            print(f"Error denying submission: {e}")
            return False

    def reset_submission_status(
            self,
            submission_id: str,
            supabase_client) -> bool:
        """Reset submission status back to Under Review."""
        try:
            result = (
                supabase_client.table("ranges_submissions")
                .update({"status": "Under Review", "review_reason": None})
                .eq("id", submission_id)
                .execute()
            )

            if result.data:
                print(
                    f"Successfully reset status for submission {submission_id}")
                return True
            else:
                print(f"Failed to reset status for submission {submission_id}")
                return False

        except Exception as e:
            print(f"Error resetting submission status: {e}")
            return False

    def get_submission_by_id(
        self, submission_id: str, supabase_client
    ) -> Dict[str, Any]:
        """Get a specific submission by ID."""
        try:
            result = (
                supabase_client.table("ranges_submissions")
                .select("*")
                .eq("id", submission_id)
                .execute()
            )
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error getting submission by ID: {e}")
            return {}

    def update_submission_review(
            self,
            submission_id: str,
            status: str,
            review_reason: str,
            supabase_client) -> bool:
        """Update submission review status and reason."""
        try:
            result = (
                supabase_client.table("ranges_submissions")
                .update({"status": status, "review_reason": review_reason})
                .eq("id", submission_id)
                .execute()
            )

            if result.data:
                print(
                    f"Successfully updated submission {submission_id} to {status}")
                return True
            else:
                print(f"Failed to update submission {submission_id}")
                return False

        except Exception as e:
            print(f"Error updating submission review: {e}")
            return False
