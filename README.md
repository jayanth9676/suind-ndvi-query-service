# FastAPI NDVI Query Service

This FastAPI application allows users to query the NDVI (Normalized Difference Vegetation Index) for a given area and time period using Sentinel-2 satellite data from the Microsoft Planetary Computer.

## Features

- Query Sentinel-2 data for a specific time range and geographical area.
- Calculate NDVI using the red and near-infrared (NIR) bands.
- Return NDVI statistics (mean and standard deviation) for the specified area.

## Requirements

- Docker
- Python

## Setup

### Clone the Repository

```bash
git clone https://github.com/your-repo/ndvi-query-service.git
cd suind-ndvi-query-service
```

### Build and Run with Docker

Ensure Docker is installed on your machine. Then, build and run the Docker container:

```bash
docker-compose up --build
```

The service will be available at `http://localhost:8000`.

### Running Locally

If you prefer to run the application without Docker, follow these steps:

1. **Create a virtual environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application**:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

## Usage

### Endpoint

- **POST** `/query_ndvi`

### Request Body

```json
{
    "timestamp": "2024-06-01/2024-07-01",
    "aoi_geojson": {
        "type": "Polygon",
        "coordinates": [[[-105.0214433670044, 39.57805759162015], [-105.0214433670044, 39.58115417669956], [-105.0173282623291, 39.58115417669956], [-105.0173282623291, 39.57805759162015], [-105.0214433670044, 39.57805759162015]]]
    }
}
```

### Response

```json
{
    "mean_ndvi": 0.33,
    "std_ndvi": 0.13
}
```

## Files

### `main.py`

The main FastAPI application. Defines the API endpoints and handles incoming requests.

### `sentinel_query.py`

Contains functions for querying Sentinel-2 data from the Microsoft Planetary Computer and calculating NDVI.

## Example

### Request

```bash
curl -X POST "http://localhost:8000/query_ndvi" -H "Content-Type: application/json" -d '{"timestamp": "2024-06-01/2024-07-01", "aoi_geojson": {"type": "Polygon", "coordinates": [[[-105.0214433670044, 39.57805759162015], [-105.0214433670044, 39.58115417669956], [-105.0173282623291, 39.58115417669956], [-105.0173282623291, 39.57805759162015], [-105.0214433670044, 39.57805759162015]]]} }'
```

### Response

```json
{
    "mean_ndvi": 0.33,
    "std_ndvi": 0.13
}
```

### Author
[@jayanth9676](https://github.com/jayanth9676)
