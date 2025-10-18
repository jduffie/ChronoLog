from typing import List, Optional

from .models import BulletModel


class BulletsService:
    """Service class for bullets database operations"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_all_bullets(self) -> List[BulletModel]:
        """Get all bullets from the database (globally available, admin-maintained)"""
        try:
            response = (
                self.supabase.table("bullets")
                .select("*")
                .order("manufacturer, model, weight_grains")
                .execute()
            )

            if not response.data:
                return []

            return BulletModel.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching bullets: {str(e)}")

    def get_bullet_by_id(self, bullet_id: str) -> Optional[BulletModel]:
        """Get a specific bullet by ID"""
        try:
            response = (
                self.supabase.table("bullets")
                .select("*")
                .eq("id", bullet_id)
                .single()
                .execute()
            )

            if not response.data:
                return None

            return BulletModel.from_supabase_record(response.data)

        except Exception as e:
            # If no rows found, return None (this is the expected behavior)
            if "PGRST116" in str(e) or "0 rows" in str(e):
                return None
            raise Exception(f"Error fetching bullet: {str(e)}")

    def create_bullet(self, bullet_data: dict) -> BulletModel:
        """Create a new bullet entry"""
        import uuid

        try:
            # Generate UUID for the bullet entry (database expects explicit
            # UUID)
            insert_data = bullet_data.copy()
            insert_data["id"] = str(uuid.uuid4())

            response = self.supabase.table(
                "bullets").insert(insert_data).execute()

            if not response.data:
                raise Exception("Failed to create bullet entry")

            return BulletModel.from_supabase_record(response.data[0])

        except Exception as e:
            if "duplicate key value violates unique constraint" in str(e):
                raise Exception("This bullet entry already exists")
            raise Exception(f"Error creating bullet: {str(e)}")

    def update_bullet(self, bullet_id: str, bullet_data: dict) -> BulletModel:
        """Update an existing bullet entry"""
        try:
            response = (
                self.supabase.table("bullets")
                .update(bullet_data)
                .eq("id", bullet_id)
                .execute()
            )

            if not response.data:
                raise Exception("Failed to update bullet entry")

            return BulletModel.from_supabase_record(response.data[0])

        except Exception as e:
            raise Exception(f"Error updating bullet: {str(e)}")

    def delete_bullet(self, bullet_id: str) -> bool:
        """Delete a bullet entry"""
        try:
            response = (
                self.supabase.table("bullets").delete().eq(
                    "id", bullet_id).execute())

            return bool(response.data)

        except Exception as e:
            raise Exception(f"Error deleting bullet: {str(e)}")

    def filter_bullets(
        self,
        manufacturer: Optional[str] = None,
        bore_diameter_mm: Optional[float] = None,
        weight_grains: Optional[int] = None,
    ) -> List[BulletModel]:
        """Filter bullets by various criteria"""
        try:
            query = self.supabase.table("bullets").select("*")

            if manufacturer:
                query = query.eq("manufacturer", manufacturer)
            if bore_diameter_mm:
                query = query.eq("bore_diameter_land_mm", bore_diameter_mm)
            if weight_grains:
                query = query.eq("weight_grains", weight_grains)

            response = query.order(
                "manufacturer, model, weight_grains").execute()

            if not response.data:
                return []

            return BulletModel.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error filtering bullets: {str(e)}")

    def get_unique_manufacturers(self) -> List[str]:
        """Get list of unique manufacturers"""
        try:
            bullets = self.get_all_bullets()
            manufacturers = list(
                set(bullet.manufacturer for bullet in bullets))
            return sorted(manufacturers)
        except Exception as e:
            raise Exception(f"Error getting manufacturers: {str(e)}")

    def get_unique_bore_diameters(self) -> List[float]:
        """Get list of unique bore diameters"""
        try:
            bullets = self.get_all_bullets()
            diameters = list(
                set(bullet.bore_diameter_land_mm for bullet in bullets))
            return sorted(diameters)
        except Exception as e:
            raise Exception(f"Error getting bore diameters: {str(e)}")

    def get_unique_weights(self) -> List[int]:
        """Get list of unique weights"""
        try:
            bullets = self.get_all_bullets()
            weights = list(set(bullet.weight_grains for bullet in bullets))
            return sorted(weights)
        except Exception as e:
            raise Exception(f"Error getting weights: {str(e)}")
