import requests

url = "http://127.0.0.1:8000/query_ndvi"
payload = {
    "timestamp": "2024-06-01/2024-07-01",
    "aoi_geojson": {
        "type": "Polygon",
        "coordinates": [
            [
                [-149.56536865234375, 60.80072385643073],
                [-148.44338989257812, 60.80072385643073],
                [-148.44338989257812, 61.18363894915102],
                [-149.56536865234375, 61.18363894915102],
                [-149.56536865234375, 60.80072385643073]
            ]
        ]
    }
}

response = requests.post(url, json=payload)
print(response.json())
