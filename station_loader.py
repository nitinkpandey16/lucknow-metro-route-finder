from datetime import datetime
import heapq
from fastapi import HTTPException
import polars as pl
from pathlib import Path

def load_stations():
    """Load station data with Polars lazy evaluation"""
    try:
        # Use lazy scan for RAM efficiency
        CSV_PATH = Path(__file__).resolve().parent / "stations.csv"
        df = pl.scan_csv(str(CSV_PATH))

        # Filter only relevant stations (lazy)
        df = df.filter(pl.col("capacity") >= 300)

        # Convert to eager (for FastAPI response)
        df = df.collect()

        # Parse connections into dictionary
        stations = {}
        for row in df.iter_rows():
            name, line, capacity, crowd, connections = row
            stations[name] = {
                "line": line,
                "capacity": capacity,
                "current_crowd": crowd,
                "connections": connections.split(", ")
            }
        return stations

    except FileNotFoundError:
        raise HTTPException(
            status_code=500, detail="Station data missing - check CSV path"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Data loading error: {str(e)}"
        )


def dijkstra_bidirectional(stations: dict, start: str, end: str):
    """Bidirectional Dijkstra for faster pathfinding."""
    if start not in stations or end not in stations:
        return None
    if start == end:
        return [start]

    # Forward search structures
    dist_start = {s: float("inf") for s in stations}
    dist_start[start] = 0.0
    pq_start = [(0.0, start)]
    parent_start = {s: None for s in stations}
    visited_start = set()

    # Backward search structures
    dist_end = {s: float("inf") for s in stations}
    dist_end[end] = 0.0
    pq_end = [(0.0, end)]
    parent_end = {s: None for s in stations}
    visited_end = set()

    meeting_node = None
    best_cost = float("inf")

    while pq_start and pq_end:
        # Step Forward
        d_fwd, curr_fwd = heapq.heappop(pq_start)
        if d_fwd <= dist_start[curr_fwd]:
            visited_start.add(curr_fwd)

            if curr_fwd in visited_end:
                meeting_node = curr_fwd
                break

            for neighbor in stations[curr_fwd]["connections"]:
                if neighbor not in stations:
                    continue
                cap = stations[neighbor]["capacity"] or 1.0
                weight = 1.0 + (stations[neighbor]["current_crowd"] / cap)
                new_d = d_fwd + weight

                if new_d < dist_start[neighbor]:
                    dist_start[neighbor] = new_d
                    parent_start[neighbor] = curr_fwd
                    heapq.heappush(pq_start, (new_d, neighbor))

        # Step Backward
        d_bwd, curr_bwd = heapq.heappop(pq_end)
        if d_bwd <= dist_end[curr_bwd]:
            visited_end.add(curr_bwd)

            if curr_bwd in visited_start:
                meeting_node = curr_bwd
                break

            for neighbor in stations[curr_bwd]["connections"]:
                if neighbor not in stations:
                    continue
                cap = stations[neighbor]["capacity"] or 1.0
                weight = 1.0 + (stations[neighbor]["current_crowd"] / cap)
                new_d = d_bwd + weight

                if new_d < dist_end[neighbor]:
                    dist_end[neighbor] = new_d
                    parent_end[neighbor] = curr_bwd
                    heapq.heappush(pq_end, (new_d, neighbor))

    if not meeting_node:
        return None

    # Reconstruct: start -> meeting_node
    path_forward = []
    curr = meeting_node
    while curr is not None:
        path_forward.append(curr)
        curr = parent_start[curr]
    path_forward.reverse()

    # Reconstruct: meeting_node -> end
    curr = parent_end[meeting_node]
    while curr is not None:
        path_forward.append(curr)
        curr = parent_end[curr]

    return path_forward


def get_time_based_route(
    stations: dict, start: str, end: str, current_time: datetime = None
):
    """Optimizes route based on current time rush-hour constraints."""
    if current_time is None:
        current_time = datetime.now()

    hour = current_time.hour
    is_rush_hour = (7 <= hour <= 9) or (17 <= hour <= 19)

    # During rush hour, multiply crowd impact to heavily favor empty routes
    if is_rush_hour:
        for s in stations.values():
            s["current_crowd"] *= 1.5

    return dijkstra_bidirectional(stations, start, end)