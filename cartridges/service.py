"""
Cartridge Service

Service layer for cartridge-related database operations.
"""

from typing import List, Optional
from .models import CartridgeModel


class CartridgeService:
    """Service class for cartridge database operations"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_cartridges_for_user(self, user_id: str) -> List[CartridgeModel]:
        """Get all cartridges for user with bullet details
        
        Returns cartridges owned by the user or global cartridges (owner_id is null)
        with related bullet information joined in.
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of CartridgeModel objects with bullet details
        """
        try:
            response = (
                self.supabase.table("cartridges")
                .select("""
                    *,
                    bullets!bullet_id (
                        manufacturer,
                        model,
                        weight_grains,
                        bullet_diameter_groove_mm,
                        bore_diameter_land_mm,
                        bullet_length_mm,
                        ballistic_coefficient_g1,
                        ballistic_coefficient_g7,
                        sectional_density,
                        min_req_twist_rate_in_per_rev,
                        pref_twist_rate_in_per_rev
                    )
                """)
                .or_(f"owner_id.eq.{user_id},owner_id.is.null")
                .execute()
            )
            
            if not response.data:
                return []
                
            cartridges = []
            for record in response.data:
                # Flatten bullet data into the cartridge record
                if record.get("bullets"):
                    bullet_data = record["bullets"]
                    record["bullet_manufacturer"] = bullet_data.get("manufacturer")
                    record["bullet_model"] = bullet_data.get("model")
                    record["bullet_weight_grains"] = bullet_data.get("weight_grains")
                    record["bullet_diameter_groove_mm"] = bullet_data.get("bullet_diameter_groove_mm")
                    record["bore_diameter_land_mm"] = bullet_data.get("bore_diameter_land_mm")
                    record["bullet_length_mm"] = bullet_data.get("bullet_length_mm")
                    record["ballistic_coefficient_g1"] = bullet_data.get("ballistic_coefficient_g1")
                    record["ballistic_coefficient_g7"] = bullet_data.get("ballistic_coefficient_g7")
                    record["sectional_density"] = bullet_data.get("sectional_density")
                    record["min_req_twist_rate_in_per_rev"] = bullet_data.get("min_req_twist_rate_in_per_rev")
                    record["pref_twist_rate_in_per_rev"] = bullet_data.get("pref_twist_rate_in_per_rev")
                
                cartridges.append(CartridgeModel.from_supabase_record(record))
            
            return cartridges
            
        except Exception as e:
            raise Exception(f"Error fetching cartridges: {str(e)}")

    def get_cartridge_by_id(self, cartridge_id: str, user_id: str) -> Optional[CartridgeModel]:
        """Get a specific cartridge by ID with bullet details
        
        Args:
            cartridge_id: The cartridge ID
            user_id: The user's ID (for access control)
            
        Returns:
            CartridgeModel object with bullet details or None
        """
        try:
            response = (
                self.supabase.table("cartridges")
                .select("""
                    *,
                    bullets!bullet_id (
                        manufacturer,
                        model,
                        weight_grains,
                        bullet_diameter_groove_mm,
                        bore_diameter_land_mm,
                        bullet_length_mm,
                        ballistic_coefficient_g1,
                        ballistic_coefficient_g7,
                        sectional_density,
                        min_req_twist_rate_in_per_rev,
                        pref_twist_rate_in_per_rev
                    )
                """)
                .eq("id", cartridge_id)
                .or_(f"owner_id.eq.{user_id},owner_id.is.null")
                .single()
                .execute()
            )
            
            if not response.data:
                return None
                
            record = response.data
            # Flatten bullet data into the cartridge record
            if record.get("bullets"):
                bullet_data = record["bullets"]
                record["bullet_manufacturer"] = bullet_data.get("manufacturer")
                record["bullet_model"] = bullet_data.get("model")
                record["bullet_weight_grains"] = bullet_data.get("weight_grains")
                record["bullet_diameter_groove_mm"] = bullet_data.get("bullet_diameter_groove_mm")
                record["bore_diameter_land_mm"] = bullet_data.get("bore_diameter_land_mm")
                record["bullet_length_mm"] = bullet_data.get("bullet_length_mm")
                record["ballistic_coefficient_g1"] = bullet_data.get("ballistic_coefficient_g1")
                record["ballistic_coefficient_g7"] = bullet_data.get("ballistic_coefficient_g7")
                record["sectional_density"] = bullet_data.get("sectional_density")
                record["min_req_twist_rate_in_per_rev"] = bullet_data.get("min_req_twist_rate_in_per_rev")
                record["pref_twist_rate_in_per_rev"] = bullet_data.get("pref_twist_rate_in_per_rev")
            
            return CartridgeModel.from_supabase_record(record)
            
        except Exception as e:
            raise Exception(f"Error fetching cartridge: {str(e)}")

    def get_cartridge_types(self) -> List[str]:
        """Get all available cartridge types
        
        Returns:
            Sorted list of cartridge type names
        """
        try:
            response = (
                self.supabase.table("cartridge_types")
                .select("name")
                .execute()
            )
            
            if not response.data:
                return []
                
            return sorted([item["name"] for item in response.data])
            
        except Exception as e:
            raise Exception(f"Error fetching cartridge types: {str(e)}")