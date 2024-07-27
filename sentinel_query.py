import pystac_client  #  pystac_client for accessing STAC APIs
import planetary_computer  #  planetary_computer for authentication and access to Planetary Computer
import rasterio  #  rasterio for handling raster data
import numpy as np  #  numpy for numerical operations
from rasterio.mask import mask  #  mask from rasterio for masking raster data
from shapely.geometry import shape, mapping  #  shape and mapping from shapely.geometry for handling GeoJSON and geometrical operations
from shapely.ops import transform  #  transform from shapely.ops for transforming geometries
import pyproj  #  pyproj for coordinate reference system (CRS) transformations
import logging  #  logging for logging messages
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any

class GeoJSONValidator(BaseModel):
    type: str
    coordinates: Any
    
# Function to query Sentinel-2 data URLs
def query_sentinel_data(aoi_geojson, timestamp):
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )
    
    # Parse timestamp to get start and end dates
    try:
        start_date, end_date = timestamp.split('/')
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid timestamp format. Use YYYY-MM-DD/YYYY-MM-DD.")

    try:
        # Validate AOI GeoJSON
        GeoJSONValidator(**aoi_geojson)
        logging.info("AOI GeoJSON is valid.")
    except ValidationError as e:
        logging.error("Invalid AOI GeoJSON: %s", str(e))
        raise ValueError("Invalid AOI GeoJSON format.")

    logging.info("AOI GeoJSON: %s", aoi_geojson)


    search = catalog.search(
        collections=["sentinel-2-l2a"],  # Search within the Sentinel-2 Level 2A collection
        intersects=aoi_geojson,  # Search for data intersecting the given AOI
        datetime=timestamp,  # Search within the given timestamp
        query={"eo:cloud_cover": {"lt": 10}},  # Filter by cloud cover less than 10%
    )
    
    items = search.item_collection()
    if len(items) == 0:
        return None
    
#     # Select the item with the least cloud cover
#     least_cloudy_item = min(items, key=lambda item: item.properties["eo:cloud_cover"])
#     # Extract URLs for red and NIR bands
#     asset_href_red = least_cloudy_item.assets["B04"].href
#     asset_href_nir = least_cloudy_item.assets["B08"].href

    
    # Find the closest available date to the requested range
    closest_item = min(
        items,
        key=lambda item: abs(datetime.strptime(item.properties["datetime"], "%Y-%m-%dT%H:%M:%S.%fZ") - start_date)
    )
    
    # Extract URLs for red and NIR bands
    asset_href_red = closest_item.assets["B04"].href
    asset_href_nir = closest_item.assets["B08"].href

    return asset_href_red, asset_href_nir

# Function to calculate NDVI
def calculate_ndvi(asset_href_red: str, asset_href_nir: str, aoi_geojson: dict):
    logging.info(f"Calculating NDVI using assets: {asset_href_red} and {asset_href_nir}")
    
    # Open the red and NIR band assets using rasterio
    with rasterio.open(asset_href_red) as red_src, rasterio.open(asset_href_nir) as nir_src:
        # Ensure CRS alignment between the red and NIR bands
        if red_src.crs != nir_src.crs:
            raise ValueError("CRS mismatch between red and NIR bands")
        
        # Convert AOI to the CRS of the raster data
        aoi_geom = shape(aoi_geojson)
        aoi_geom = transform(
            lambda x, y: pyproj.Transformer.from_crs("EPSG:4326", red_src.crs.to_string(), always_xy=True).transform(x, y),
            aoi_geom
        )
        
        # Mask the rasters using the AOI geometry
        red, _ = mask(red_src, [mapping(aoi_geom)], crop=True)
        nir, _ = mask(nir_src, [mapping(aoi_geom)], crop=True)

    # Check if the bands are non-empty
    if red.size == 0 or nir.size == 0:
        logging.error("One or both bands are empty")
        raise ValueError("One or both bands are empty")

    # Calculate NDVI
    with np.errstate(divide='ignore', invalid='ignore'):
        ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)
    
    # Handle any NaN or inf values in the NDVI array
    ndvi = np.nan_to_num(ndvi, nan=np.nan, posinf=np.nan, neginf=np.nan)

    # Flatten the NDVI array and remove NaN values for statistics
    ndvi_flat = ndvi.flatten()
    ndvi_flat = ndvi_flat[~np.isnan(ndvi_flat)]

    if ndvi_flat.size == 0:
        logging.error("NDVI calculation resulted in an empty array")
        raise ValueError("NDVI calculation resulted in an empty array")

    # Compute statistics for NDVI values
    mean_ndvi = np.mean(ndvi_flat)
    std_ndvi = np.std(ndvi_flat)
    
    logging.info(f"NDVI statistics - mean: {mean_ndvi}, std: {std_ndvi}")

    return {
        "mean_ndvi": float(mean_ndvi),
        "std_ndvi": float(std_ndvi)
    }
