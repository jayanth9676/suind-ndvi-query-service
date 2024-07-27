"""
MAIN CODE IS IN THE
main.py and sentinel_query.py




# This is just an example code

# CODE:

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from sentinel_query import query_sentinel_data, calculate_ndvi
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)

class QueryData(BaseModel):
    timestamp: str = Field(..., example="2023-07-01/2023-07-31")
    aoi_geojson: Dict[str, Any]

@app.post("/query_ndvi")
async def get_ndvi(data: QueryData):
    logging.info("Received request with timestamp: %s and AOI: %s", data.timestamp, data.aoi_geojson)
    
    asset_href = query_sentinel_data(data.aoi_geojson, data.timestamp)
    if not asset_href:
        logging.error("No suitable Sentinel-2 data found for timestamp: %s and AOI: %s", data.timestamp, data.aoi_geojson)
        raise HTTPException(status_code=404, detail="No suitable Sentinel-2 data found for the given parameters.")
    
    try:
        ndvi_stats = calculate_ndvi(asset_href, data.aoi_geojson)
    except ValueError as e:
        logging.error("Error in calculating NDVI: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
    return ndvi_stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import pystac_client
import planetary_computer
import rasterio
import numpy as np
from rasterio.windows import from_bounds
from shapely.geometry import shape
from shapely import wkt

def query_sentinel_data(aoi_geojson, timestamp):
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        intersects=aoi_geojson,
        datetime=timestamp,
        query={"eo:cloud_cover": {"lt": 10}},
    )
    
    items = search.item_collection()
    if len(items) == 0:
        return None
    
    least_cloudy_item = min(items, key=lambda item: item.properties["eo:cloud_cover"])
    asset_href = least_cloudy_item.assets["visual"].href

    return asset_href

def load_band_data(asset_href, aoi_geojson):
    # Example placeholder function
    return np.random.rand(8, 100, 100)  # Example data with 8 bands

def calculate_ndvi(asset_href, aoi_geojson):
    band_data = load_band_data(asset_href, aoi_geojson)
    
    # Check if enough bands are present
    if band_data.shape[0] < 8:
        raise ValueError("Not enough bands in the data to calculate NDVI")
    
    nir = band_data[7].astype(float)
    red = band_data[3].astype(float)
    
    ndvi = (nir - red) / (nir + red)
    
    return calculate_statistics(ndvi, asset_href, aoi_geojson)

def calculate_statistics(ndvi, asset_href, aoi_geojson):
    # Example placeholder function for statistics
    return {
        'mean': np.mean(ndvi),
        'std': np.std(ndvi)
    }
"""