# Lucknow Metro Route Optimizer & Real-Time Traffic API

An asynchronous REST API and route optimization engine designed to mitigate peak-hour bottlenecks across the Lucknow Metro network by combining dynamic crowd weighting, rush-hour heuristics, and bidirectional graph pathfinding.

---

## Architecture Overview

- **High-Throughput Ingestion**: Loads and filters transit graph topologies using **Polars** lazy evaluation (`pl.scan_csv`) to minimize memory allocation and execution overhead.
- **Bidirectional Dijkstra Search**: Executes simultaneous forward and backward graph traversals, reducing node evaluation space by ~50% compared to traditional single-source Dijkstra.
- **Dynamic Congestion Cost Function**: Incorporates real-time crowd density into edge calculations:
  $$\text{Weight} = 1.0 + \left(\frac{\text{Current Crowd}}{\text{Capacity}}\right)$$
- **Rush-Hour Multipliers**: Automatically scales crowd penalties during peak commuter intervals (07:00–09:00 and 17:00–19:00) to reroute passengers through less congested paths.
- **Fallback Composite Recovery**: Detects network disconnections or missing direct paths and reconstructs optimal two-hop alternative routes across available junctions.

---

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI (ASGI)
- **Data Processing**: Polars
- **Data Structures**: Priority Queue (`heapq`), Adjacency Mapping
- **Validation & Schemas**: Pydantic v2
- **Documentation**: OpenAPI / Swagger UI

---

## Project Structure

```text
lucknow_metro/
├── app.py              # FastAPI application, route validation, and REST controllers
├── station_loader.py   # Polars data loader, Bidirectional Dijkstra, and time heuristics
├── stations.csv        # Station network metadata, capacities, and connection topology
├── requirement.txt     # Locked production dependencies
└── README.md           # Engineering documentation


```

### Should Your Code Files Be Public?

Yes, keep `app.py` and `station_loader.py` public.

Engineering managers and technical interviewers do not consider 2–3 cleanly written Python files "bulky". When an engineer evaluates a GitHub link, they check:

1. **The README**: To understand architecture, impact, and API contracts within 60 seconds.

2. **The Code**: To verify clean structure, typing, edge-case safety, and genuine algorithmic competence rather than just generic claims.

Hiding your code leaves a repository looking incomplete or unverified. What hiring managers **do not** want to see are clutter files: virtual environments (`.venv/`), database binaries (`metro.db`), compile caches (`__pycache__/`), or loose drafts. Your repo is currently clean with just `app.py`, `station_loader.py`, `requirement.txt`, and `README.md`.

---

### What to Fix in Your Current README

Your raw file contains AI study notes (`"Why this content matters"`, `"Commanded AI"`, `"Reawakened CSE soul"`, and internal prompt tables). These look like raw study course prompts and should be removed.

A professional repository README presents:

- Problem, solution, and key architectural metrics.

- Live API request and response samples.

- Algorithmic design decisions (why Bidirectional Dijkstra over standard Dijkstra).

- Clear setup and local run instructions.

---

### Professional `README.md`

Replace your entire `README.md` content with the following markdown:

````markdown
# Lucknow Metro Route Optimizer & Real-Time Traffic API

An asynchronous REST API and route optimization engine designed to mitigate peak-hour bottlenecks across the Lucknow Metro network by combining dynamic crowd weighting, rush-hour heuristics, and bidirectional graph pathfinding.

---

## Architecture Overview

- **High-Throughput Ingestion**: Loads and filters transit graph topologies using **Polars** lazy evaluation (`pl.scan_csv`) to minimize memory allocation and execution overhead.
- **Bidirectional Dijkstra Search**: Executes simultaneous forward and backward graph traversals, reducing node evaluation space by ~50% compared to traditional single-source Dijkstra.
- **Dynamic Congestion Cost Function**: Incorporates real-time crowd density into edge calculations:
  $$\text{Weight} = 1.0 + \left(\frac{\text{Current Crowd}}{\text{Capacity}}\right)$$
- **Rush-Hour Multipliers**: Automatically scales crowd penalties during peak commuter intervals (07:00–09:00 and 17:00–19:00) to reroute passengers through less congested paths.
- **Fallback Composite Recovery**: Detects network disconnections or missing direct paths and reconstructs optimal two-hop alternative routes across available junctions.

---

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI (ASGI)
- **Data Processing**: Polars
- **Data Structures**: Priority Queue (`heapq`), Adjacency Mapping
- **Validation & Schemas**: Pydantic v2
- **Documentation**: OpenAPI / Swagger UI

---

## Project Structure

```text
lucknow_metro/
├── app.py              # FastAPI application, route validation, and REST controllers
├── station_loader.py   # Polars data loader, Bidirectional Dijkstra, and time heuristics
├── stations.csv        # Station network metadata, capacities, and connection topology
├── requirement.txt     # Locked production dependencies
└── README.md           # Engineering documentation
```
````

---

## Getting Started

### 1. Prerequisites & Installation

Clone the repository and configure the virtual environment:

```bash
 git clone [https://github.com/nitinkpandey16/lucknow-metro-route-finder.git](https://github.com/nitinkpandey16/lucknow-metro-route-finder.git)
 cd lucknow_metro
 python -m venv .venv

# On Windows (PowerShell):
 .\.venv\Scripts\Activate.ps1

# Install required packages:
 pip install -r requirement.txt

```

### 2. Running the Service

Start the local ASGI development server:

```bash
 uvicorn app:app --reload

```

Once initialized, navigate to:

- **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`
- **Alternative Documentation (ReDoc)**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

---

## API Reference

### `GET /route`

    Calculates the optimal route between two stations factoring in time and congestion.

#### Query Parameters

| Parameter       | Type     | Required | Default   | Description                      |
| --------------- | -------- | -------- | --------- | -------------------------------- |
| `start_station` | `string` | Yes      | -         | Name of departure station        |
| `end_station`   | `string` | Yes      | -         | Name of destination station      |
| `current_time`  | `string` | No       | `"08:00"` | 24-hour departure time (`HH:MM`) |

#### Sample Request

```http
   GET /route?start_station=Charbagh&end_station=Hazratganj&current_time=10:00 HTTP/1.1
   Host: localhost:8000

```

#### Sample Response (`200 OK`)

````json
{
  "route": [
  "Charbagh",
  "Hazratganj"
  ],
  "estimated_time": 2,
  "crowd_level": "high"
  }

 ```

#### Error Handling

 * **`400 Bad Request`**: Raised if a station does not exist in the transit network graph.

  ```json
 {
  "detail": "Invalid start station: NonExistentStation"
  }

  ```


* **`500 Internal Server Error`**: Catches file read failures or unexpected pipeline exceptions cleanly without terminating the worker process.

 ---
````
