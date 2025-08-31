"""
Unit Mapping Service Interface Layer
Handles external service interactions for unit mapping data
"""
from typing import Dict


class UnitMappingService:
    """Service interface for unit mapping operations"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def get_garmin_units_mapping(self) -> Dict[str, Dict[str, str]]:
        """Load the Garmin units mapping from Supabase table"""
        try:
            response = self.supabase.table("garmin_shot_table_units").select("*").execute()
            
            unit_mapping = {}
            for record in response.data:
                header_raw = record['header_raw']
                unit_mapping[header_raw] = {
                    'measurement': record['measurement'],
                    'header_stripped': record['header_stripped'],
                    'imperial': record['imperial_units'].strip(),
                    'metric': record['metric_units'].strip()
                }
            
            return unit_mapping
        except Exception as e:
            raise Exception(f"Error loading Garmin units mapping: {e}")
    
    def get_kestrel_units_mapping(self) -> Dict[str, Dict[str, str]]:
        """Load the Kestrel units mapping from Supabase table"""
        try:
            response = self.supabase.table("kestrel_unit_mappings").select("*").execute()
            
            unit_mapping = {}
            for record in response.data:
                measurement = record['measurement']
                unit_mapping[measurement] = {
                    'imperial': record['imperial_units'].strip(),
                    'metric': record['metric_units'].strip()
                }
            
            return unit_mapping
        except Exception as e:
            raise Exception(f"Error loading Kestrel units mapping: {e}")