from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import Rifle


class RifleService:
    """Service class for rifle database operations"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_rifles_for_user(self, user_id: str) -> List[Rifle]:
        """Get all rifles for a user, ordered by creation date descending"""
        try:
            response = (
                self.supabase.table("rifles")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )

            if not response.data:
                return []

            return Rifle.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching rifles: {str(e)}")

    def get_rifle_by_id(self, rifle_id: str, user_id: str) -> Optional[Rifle]:
        """Get a specific rifle by ID"""
        try:
            response = (
                self.supabase.table("rifles")
                .select("*")
                .eq("id", rifle_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            if not response.data:
                return None

            return Rifle.from_supabase_record(response.data)

        except Exception as e:
            raise Exception(f"Error fetching rifle: {str(e)}")

    def get_rifle_by_name(self, user_id: str, name: str) -> Optional[Rifle]:
        """Get a rifle by name"""
        try:
            response = (
                self.supabase.table("rifles")
                .select("*")
                .eq("user_id", user_id)
                .eq("name", name)
                .single()
                .execute()
            )

            if not response.data:
                return None

            return Rifle.from_supabase_record(response.data)

        except Exception as e:
            return None

    def get_rifles_filtered(
        self,
        user_id: str,
        cartridge_type: Optional[str] = None,
        twist_ratio: Optional[str] = None,
    ) -> List[Rifle]:
        """Get filtered rifles"""
        try:
            query = (
                self.supabase.table("rifles")
                .select("*")
                .eq("user_id", user_id)
            )

            if cartridge_type and cartridge_type != "All":
                query = query.eq("cartridge_type", cartridge_type)

            if twist_ratio and twist_ratio != "All":
                query = query.eq("barrel_twist_ratio", twist_ratio)

            response = query.order("created_at", desc=True).execute()

            if not response.data:
                return []

            return Rifle.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching filtered rifles: {str(e)}")

    def get_unique_cartridge_types(self, user_id: str) -> List[str]:
        """Get unique cartridge types for a user"""
        try:
            response = (
                self.supabase.table("rifles")
                .select("cartridge_type")
                .eq("user_id", user_id)
                .execute()
            )

            if not response.data:
                return []

            cartridge_types = list(
                set(
                    [
                        record["cartridge_type"]
                        for record in response.data
                        if record.get("cartridge_type")
                    ]
                )
            )
            return sorted(cartridge_types)

        except Exception as e:
            raise Exception(f"Error fetching cartridge types: {str(e)}")

    def get_unique_twist_ratios(self, user_id: str) -> List[str]:
        """Get unique twist ratios for a user"""
        try:
            response = (
                self.supabase.table("rifles")
                .select("barrel_twist_ratio")
                .eq("user_id", user_id)
                .execute()
            )

            if not response.data:
                return []

            twist_ratios = list(
                set(
                    [
                        record["barrel_twist_ratio"]
                        for record in response.data
                        if record.get("barrel_twist_ratio")
                    ]
                )
            )
            return sorted(twist_ratios)

        except Exception as e:
            raise Exception(f"Error fetching twist ratios: {str(e)}")

    def create_rifle(self, rifle_data: dict) -> str:
        """Create a new rifle"""
        try:
            response = (
                self.supabase.table("rifles").insert(rifle_data).execute()
            )

            if not response.data:
                raise Exception("Failed to create rifle")

            return response.data[0]["id"]

        except Exception as e:
            raise Exception(f"Error creating rifle: {str(e)}")

    def update_rifle(self, rifle_id: str, user_id: str, updates: dict) -> None:
        """Update a rifle"""
        try:
            updates["updated_at"] = datetime.now().isoformat()
            self.supabase.table("rifles").update(updates).eq("id", rifle_id).eq("user_id", user_id).execute()

        except Exception as e:
            raise Exception(f"Error updating rifle: {str(e)}")

    def delete_rifle(self, rifle_id: str, user_id: str) -> None:
        """Delete a rifle"""
        try:
            self.supabase.table("rifles").delete().eq("id", rifle_id).eq("user_id", user_id).execute()

        except Exception as e:
            raise Exception(f"Error deleting rifle: {str(e)}")

    def save_rifle(self, rifle: Rifle) -> str:
        """Save a Rifle entity to Supabase"""
        try:
            rifle_data = {
                "id": rifle.id,
                "user_id": rifle.user_id,
                "name": rifle.name,
                "cartridge_type": rifle.cartridge_type,
                "barrel_twist_ratio": rifle.barrel_twist_ratio,
                "barrel_length": rifle.barrel_length,
                "sight_offset": rifle.sight_offset,
                "trigger": rifle.trigger,
                "scope": rifle.scope,
                "created_at": rifle.created_at.isoformat() if rifle.created_at else None,
                "updated_at": rifle.updated_at.isoformat() if rifle.updated_at else None,
            }
            
            response = self.supabase.table("rifles").insert(rifle_data).execute()
            
            if not response.data:
                raise Exception("Failed to save rifle")
            
            return response.data[0]["id"]
            
        except Exception as e:
            raise Exception(f"Error saving rifle: {str(e)}")