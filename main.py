from fastapi import FastAPI, HTTPException  #  FastAPI and HTTPException for creating API and handling errors
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field  #  Pydantic for data validation and schema definition
from typing import Dict, Any  #  types for type hints
from sentinel_query import query_sentinel_data, calculate_ndvi  #  functions from sentinel_query.py
import logging  #  logging for logging messages

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Serve the static frontend files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Define the schema for incoming request data using Pydantic
class QueryData(BaseModel):
    timestamp: str = Field(..., example="2024-06-01/2024-07-01")
    aoi_geojson: Dict[str, Any]

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("frontend/home.html") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Define the POST endpoint /query_ndvi
@app.post("/query_ndvi")
async def get_ndvi(data: QueryData):
    logging.info("Received request with timestamp: %s and AOI: %s", data.timestamp, data.aoi_geojson)
    
    # Query Sentinel-2 data URLs
    asset_hrefs = query_sentinel_data(data.aoi_geojson, data.timestamp)
    if not asset_hrefs:
        logging.error("No suitable Sentinel-2 data found for timestamp: %s and AOI: %s", data.timestamp, data.aoi_geojson)
        raise HTTPException(status_code=404, detail="No suitable Sentinel-2 data found for the given parameters.")
    
    try:
        # Calculate NDVI statistics
        ndvi_stats = calculate_ndvi(asset_hrefs[0], asset_hrefs[1], data.aoi_geojson)
    except ValueError as e:
        logging.error("Error in calculating NDVI: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
    # Return NDVI statistics
    return ndvi_stats

# Run the FastAPI app using Uvicorn if the script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
