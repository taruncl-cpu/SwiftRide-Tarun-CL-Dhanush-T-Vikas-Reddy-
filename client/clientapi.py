# =============================================================================
# CLIENT API SERVER (NEW)
# =============================================================================

# client/api_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from client.services.api_client import MiniUberAPIWrapper
import uvicorn

# Client API server that can be called from Postman/curl
client_app = FastAPI(
    title="Mini-Uber Client API",
    description="Client-side API that forwards requests to the main server",
    version="1.0.0"
)

# Request models for client API
class RideSubmissionRequest(BaseModel):
    source_location: str
    dest_location: str
    user_id: str

# Initialize the API wrapper
api_wrapper = MiniUberAPIWrapper()

@client_app.on_event("shutdown")
async def shutdown():
    await api_wrapper.cleanup()

@client_app.get("/")
async def root():
    return {"message": "Mini-Uber Client API - Use /docs for API documentation"}

@client_app.post("/submit-ride")
async def submit_ride_endpoint(request: RideSubmissionRequest):
    """
    Submit a ride request
    This endpoint can be called from Postman or curl:
    
    curl -X POST "http://localhost:8001/submit-ride" \
         -H "Content-Type: application/json" \
         -d '{"source_location": "Koramangala", "dest_location": "Indiranagar", "user_id": "user123"}'
    """
    result = await api_wrapper.submit_ride(
        source_location=request.source_location,
        dest_location=request.dest_location,
        user_id=request.user_id
    )
    
    if result["success"]:
        return result["data"]
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@client_app.get("/user-rides/{user_id}")
async def get_user_rides_endpoint(user_id: str):
    """
    Get rides for a specific user
    
    curl -X GET "http://localhost:8001/user-rides/user123"
    """
    result = await api_wrapper.get_user_rides(user_id)
    
    if result["success"]:
        return result["data"]
    else:
        raise HTTPException(status_code=400, detail=result# Project Structure:
# mini-uber/
# ├── server/
# │   ├── __init__.py
# │   ├── main.py
# │   ├── api/
# │   │   ├── __init__.py
# │   │   └── endpoints.py
# │   ├── models/
# │   │   ├── __init__.py
# │   │   └── schemas.py
# │   └── core/
# │       ├── __init__.py
# │       └── config.py
# ├── client/
# │   ├── __init__.py
# │   ├── main.py
# │   ├── services/
# │   │   ├── __init__.py
# │   │   └── api_client.py
# │   └── utils/
# │       ├── __init__.py
# │       └── helpers.py
# └── requirements.txt

# =============================================================================
# SERVER CODE
# =============================================================================

# server/__init__.py
# Empty file

# server/main.py
from fastapi import FastAPI
from server.api.endpoints import router as api_router
from server.core.config import settings

app = FastAPI(
    title="Mini-Uber API",
    description="A simple ride-sharing API",
    version="1.0.0"
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Mini-Uber API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# server/core/__init__.py
# Empty file

# server/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Mini-Uber"
    debug: bool = True
    api_version: str = "v1"
    
    class Config:
        env_file = ".env"

settings = Settings()

# server/models/__init__.py
# Empty file

# server/models/schemas.py
from pydantic import BaseModel
from typing import Optional

class PingRequest(BaseModel):
    data: str

class PongResponse(BaseModel):
    message: str
    status: str

class RideRequest(BaseModel):
    pickup_location: str
    destination: str
    rider_name: str

class RideResponse(BaseModel):
    ride_id: str
    status: str
    driver_name: Optional[str] = None
    estimated_arrival: Optional[str] = None

# server/api/__init__.py
# Empty file

# server/api/endpoints.py
from fastapi import APIRouter, HTTPException
from server.models.schemas import PingRequest, PongResponse, RideRequest, RideResponse
import uuid
import random

router = APIRouter()

@router.post("/ping", response_model=PongResponse)
async def ping_pong(request: PingRequest):
    # BUG: Server doesn't properly validate the ping value
    # This should check if request.data == "ping" but has a typo
    if request.data == "pong":  # BUG: Wrong comparison value
        return PongResponse(message="pong", status="success")
    else:
        raise HTTPException(status_code=400, detail="Invalid ping data")

@router.post("/ride/request", response_model=RideResponse)
async def request_ride(ride_request: RideRequest):
    # Simple ride request simulation
    ride_id = str(uuid.uuid4())
    drivers = ["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown"]
    driver = random.choice(drivers)
    
    return RideResponse(
        ride_id=ride_id,
        status="confirmed",
        driver_name=driver,
        estimated_arrival="5-10 minutes"
    )

@router.get("/ride/{ride_id}")
async def get_ride_status(ride_id: str):
    # Mock ride status
    statuses = ["confirmed", "driver_assigned", "en_route", "arrived", "completed"]
    return {
        "ride_id": ride_id,
        "status": random.choice(statuses),
        "driver_location": {"lat": 12.9716, "lng": 77.5946}  # Bangalore coordinates
    }
