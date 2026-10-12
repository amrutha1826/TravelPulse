import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app

def test_full_platform_api():
    client = TestClient(app)

    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200
    print("[PASS] Health check:", res.json()["status"])

    # 2. Geo States
    res = client.get("/api/geo/states")
    assert res.status_code == 200
    states = res.json()
    assert len(states) > 0
    print(f"[PASS] States count: {len(states)}")

    # 3. Geo Cities for Tamil Nadu
    res = client.get("/api/geo/cities?state=Tamil Nadu")
    assert res.status_code == 200
    cities = res.json()
    assert len(cities) > 0
    print(f"[PASS] Tamil Nadu cities count: {len(cities)}")

    # 4. Operators
    res = client.get("/api/transport/operators")
    assert res.status_code == 200
    ops = res.json()
    assert len(ops) > 0
    print(f"[PASS] Transport operators count: {len(ops)}")

    # 5. Search Transport (Chennai to Bengaluru)
    chennai = next((c for c in cities if "chennai" in c["name"].lower()), cities[0])
    res_ka = client.get("/api/geo/cities?state=Karnataka")
    blr = next((c for c in res_ka.json() if "bengaluru" in c["name"].lower() or "bangalore" in c["name"].lower()), res_ka.json()[0])

    transport_req = {
        "origin_city_id": chennai["id"],
        "dest_city_id": blr["id"],
        "selected_modes": ["flight", "train", "bus"],
        "sort_by": "recommended",
        "limit": 5
    }
    res_t = client.post("/api/transport/search", json=transport_req)
    assert res_t.status_code == 200
    t_data = res_t.json()
    print(f"[PASS] Transport search returned {len(t_data.get('results', []))} routes")
    if t_data.get("results"):
        top_r = t_data["results"][0]
        rev = top_r.get("review_summary")
        print(f"       Top route: {top_r.get('carrier_name') or top_r.get('operator_name')} | Grounded reviews attached: {rev is not None}")

    # 6. Itinerary Generate (2 days in Chennai)
    itin_req = {
        "destination_city_id": chennai["id"],
        "num_days": 2,
        "pace": "medium",
        "categories": ["Temples & Spiritual", "Heritage & History"]
    }
    res_itin = client.post("/api/itinerary/generate", json=itin_req)
    assert res_itin.status_code == 200
    itin_data = res_itin.json()
    day_plans = itin_data.get("day_plans", {})
    print(f"[PASS] DRL Itinerary generated {len(day_plans)} days")
    day1 = day_plans.get("1") or day_plans.get(1)
    if day1 and day1.get("activities"):
        act0 = day1["activities"][0]
        p_name = act0.get("place_name") or act0.get("poi", {}).get("name")
        act_rev = act0.get("review_summary")
        print(f"       Day 1 Activity 1: {p_name} | Grounded review: {act_rev is not None}")

    # 7. Hotels search
    res_h = client.get(f"/api/hotels/search?city_id={chennai['id']}&limit=3")
    assert res_h.status_code == 200
    hotels = res_h.json()
    print(f"[PASS] Hotels returned: {len(hotels)}")
    if hotels:
        h0 = hotels[0]
        h_rev = h0.get("review_summary")
        print(f"       Hotel: {h0['name']} | Grounded TripAdvisor reviews: {h_rev is not None}")

    # 8. Booking creation
    book_req = {
        "user_name": "Test Traveler",
        "user_email": "test@travelpulse.ai",
        "user_phone": "+91 99999 88888",
        "booking_type": "transport",
        "item_details": {"route": "Chennai to Bengaluru"},
        "total_amount": 1500
    }
    res_b = client.post("/api/bookings/create", json=book_req)
    assert res_b.status_code == 200
    pnr = res_b.json().get("pnr")
    print(f"[PASS] Booking confirmed with PNR: {pnr}")

if __name__ == "__main__":
    test_full_platform_api()
    print("\nALL 8 API INTEGRATION TESTS PASSED PERFECTLY!")
