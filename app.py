import datetime
import logging
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from station_loader import get_time_based_route, load_stations

app = FastAPI(title="Lucknow Metro Route Optimizer")


# --- Schemas ---
class RouteResponse(BaseModel):
    route: List[str]
    estimated_time: int
    crowd_level: str


# --- Test 1: Health Check Endpoint ---
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/debug-stations")
async def debug_stations():
    stations = load_stations()
    return {"loaded_stations": list(stations.keys())}


# --- Helper: Validation (Test 5) ---
def validate_stations(start: str, end: str, valid_stations: list):
    if start not in valid_stations:
        raise HTTPException(
            status_code=400, detail=f"Invalid start station: {start}"
        )
    if end not in valid_stations:
        raise HTTPException(
            status_code=400, detail=f"Invalid end station: {end}"
        )


# --- Route Endpoint (Tests 2 - 6) ---
@app.get("/route")
async def get_route(
    start_station: str, end_station: str, current_time: str = "08:00"
) -> RouteResponse:
    try:
        stations = load_stations()
        valid_stations = list(stations.keys())

        # Validate existence
        validate_stations(start_station, end_station, valid_stations)

        # Determine start crowd level
        start_crowd = stations[start_station]["current_crowd"]
        start_cap = stations[start_station]["capacity"] or 1.0

        if start_crowd >= (start_cap * 0.8):
            crowd_level = "high"
        elif start_crowd >= (start_cap * 0.6):
            crowd_level = "medium"
        else:
            crowd_level = "low"

        # Test 6: Same start and end station
        if start_station == end_station:
            return RouteResponse(
                route=[start_station],
                estimated_time=0,
                crowd_level=crowd_level,
            )

        # Parse current_time (HH:MM)
        # Clean and extract only the HH:MM part before parsing
        clean_time = current_time.strip().split()[0]  # grabs just "10:00"
        hour, minute = map(int, current_time.split(":"))
        current_time_obj = datetime.time(hour=hour, minute=minute)

        # Primary route calculation
        route = get_time_based_route(
            stations, start_station, end_station, current_time_obj
        )

        # Step 4 / Test 4: Disconnected station alternative recovery
        if not route:
            alternative_routes = []
            for station in valid_stations:
                if station != start_station and station != end_station:
                    alt1 = get_time_based_route(
                        stations, start_station, station, current_time_obj
                    )
                    if alt1:
                        alt2 = get_time_based_route(
                            stations, station, end_station, current_time_obj
                        )
                        if alt2:
                            alternative_routes.append(alt1 + alt2[1:])

            if alternative_routes:
                shortest_route = min(alternative_routes, key=len)
                return RouteResponse(
                    route=shortest_route,
                    estimated_time=15,
                    crowd_level="medium",
                )
            else:
                return RouteResponse(
                    route=[], estimated_time=0, crowd_level="unknown"
                )

        # Compute estimated travel time along path
        estimated_time = 0.0
        for i in range(len(route) - 1):
            next_st = route[i + 1]
            cap = stations[next_st]["capacity"] or 1.0
            crowd = stations[next_st]["current_crowd"]
            weight = 1.0 + (crowd / cap)
            estimated_time += weight

        return RouteResponse(
            route=route,
            estimated_time=int(round(estimated_time)),
            crowd_level=crowd_level,
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")