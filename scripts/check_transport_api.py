import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

res = client.post("/api/transport/search", json={
    "origin_city_id": "BLR",
    "dest_city_id": "MAA",
    "selected_modes": ["flight", "train", "bus"],
    "sort_by": "cheapest",
    "limit": 10
})

data = res.json()
print("Status:", res.status_code)
print("Keys in response:", list(data.keys()))
print("Total count in data:", data.get("total_count"))
print("Direct routes count:", len(data.get("direct_routes", [])))
print("Connecting routes count:", len(data.get("connecting_routes", [])))
print("All routes count:", len(data.get("all_routes", [])))

if data.get("direct_routes"):
    print("Sample direct route:", data["direct_routes"][0]["transport_mode"], data["direct_routes"][0]["operator_name"], data["direct_routes"][0]["total_fare_inr"])
