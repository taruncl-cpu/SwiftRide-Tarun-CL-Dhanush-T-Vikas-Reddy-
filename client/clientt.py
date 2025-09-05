# =============================================================================
# CLIENT CODE
# =============================================================================

# client/__init__.py
# Empty file

# client/main.py
import asyncio
from client.services.api_client import MiniUberClient
from client.utils.helpers import display_response

async def main():
    client = MiniUberClient()
    
    print("=== Mini-Uber Client Demo ===")
    
    # Test ping-pong endpoint
    print("\n1. Testing Ping-Pong:")
    try:
        response = await client.ping()
        display_response("Ping", response)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test ride request
    print("\n2. Requesting a ride:")
    try:
        ride_data = {
            "pickup_location": "Koramangala",
            "destination": "Indiranagar", 
            "rider_name": "Test User"
        }
        response = await client.request_ride(ride_data)
        display_response("Ride Request", response)
        
        # Get ride status
        if response.get("ride_id"):
            print("\n3. Checking ride status:")
            status_response = await client.get_ride_status(response["ride_id"])
            display_response("Ride Status", status_response)
            
    except Exception as e:
        print(f"Error: {e}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())

# client/services/__init__.py
# Empty file

# client/services/api_client.py
import aiohttp
import json
from typing import Dict, Any

class MiniUberClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def ping(self) -> Dict[str, Any]:
        """Test the ping-pong endpoint"""
        session = await self._get_session()
        
        # BUG: Client sends wrong data format
        # Should send {"data": "ping"} but sends wrong key
        payload = {"message": "ping"}  # BUG: Wrong key name
        
        async with session.post(
            f"{self.base_url}/api/v1/ping",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def request_ride(self, ride_data: Dict[str, str]) -> Dict[str, Any]:
        """Request a new ride"""
        session = await self._get_session()
        
        async with session.post(
            f"{self.base_url}/api/v1/ride/request",
            json=ride_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def get_ride_status(self, ride_id: str) -> Dict[str, Any]:
        """Get the status of a ride"""
        session = await self._get_session()
        
        async with session.get(
            f"{self.base_url}/api/v1/ride/{ride_id}"
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()

# client/utils/__init__.py
# Empty file

# client/utils/helpers.py
import json
from typing import Any, Dict

def display_response(title: str, response: Dict[str, Any]):
    """Pretty print API responses"""
    print(f"\n{title} Response:")
    print("-" * 40)
    print(json.dumps(response, indent=2))
    print("-" * 40)

def format_ride_info(ride_data: Dict[str, Any]) -> str:
    """Format ride information for display"""
    if not ride_data:
        return "No ride data available"
    
    info = f"Ride ID: {ride_data.get('ride_id', 'N/A')}\n"
    info += f"Status: {ride_data.get('status', 'Unknown')}\n"
    
    if ride_data.get('driver_name'):
        info += f"Driver: {ride_data['driver_name']}\n"
    
    if ride_data.get('estimated_arrival'):
        info += f"ETA: {ride_data['estimated_arrival']}\n"
    
    return info

# =============================================================================
# REQUIREMENTS FILE
# =============================================================================

# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
aiohttp==3.9.1
python-multipart==0.0.6