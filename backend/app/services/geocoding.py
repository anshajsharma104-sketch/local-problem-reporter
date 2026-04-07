import httpx
from typing import Optional, Tuple
import asyncio


class GeocodingService:
    """Service for reverse geocoding coordinates to addresses using Nominatim API"""
    
    BASE_URL = "https://nominatim.openstreetmap.org"
    
    @staticmethod
    async def get_address_from_coordinates(latitude: float, longitude: float) -> Optional[str]:
        """
        Convert latitude and longitude to human-readable address
        Uses Nominatim API (free, no API key required)
        
        Args:
            latitude: Issue latitude
            longitude: Issue longitude
            
        Returns:
            Human-readable address or None if lookup fails
        """
        try:
            # Nominatim reverse geocoding endpoint
            url = f"{GeocodingService.BASE_URL}/reverse"
            params = {
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "zoom": 18,  # Zoom level for detail
                "addressdetails": 1
            }
            
            # Use httpx for async requests
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, 
                    params=params,
                    headers={"User-Agent": "LocalProblemReporter/1.0"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Return the formatted address
                    return data.get("address", {}).get("road") or data.get("display_name", "Unknown Location")
                    
        except Exception as e:
            print(f"Error in reverse geocoding: {e}")
            
        return None
    
    @staticmethod
    def get_address_from_coordinates_sync(latitude: float, longitude: float) -> Optional[str]:
        """Synchronous wrapper for reverse geocoding"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(
                GeocodingService.get_address_from_coordinates(latitude, longitude)
            )
        except Exception as e:
            print(f"Error in sync geocoding: {e}")
            return None
