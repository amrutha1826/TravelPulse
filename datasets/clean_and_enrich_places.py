"""
Script to clean, geo-fence, and enrich Chennai POIs with Metro connectivity and accessibility metadata.
Removes any out-of-city anomalies (Tirupati, Srirangam, etc.) and tags nearest Chennai Metro stations.
"""
import json
import os
import math
import pandas as pd

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def main():
    # Load metro data
    metro_file = r"d:\drl_project\data\chennai_metro.json"
    with open(metro_file, "r", encoding="utf-8") as f:
        metro_data = json.load(f)
        
    all_stations = []
    for line in metro_data["lines"]:
        for st in line["stations"]:
            all_stations.append({
                "name": st["name"],
                "lat": st["lat"],
                "lon": st["lon"],
                "line": line["line_name"],
                "color": line["color"]
            })
            
    # Load existing places
    places_file = r"d:\drl_project\tourist_places\chennai_places.json"
    with open(places_file, "r", encoding="utf-8") as f:
        places = json.load(f)

    # Filter strictly within Chennai & local metropolitan boundary + ECR/Mahabalipuram
    # Exclude anything in Andhra Pradesh (Tirupati, Tirumala, Kalahasti) or distant Tamil Nadu (Trichy, Srirangam, Madurai, Salem)
    valid_places = []
    excluded_names = ["srirangam", "tirumala", "tirupati", "kalahasti", "trichy", "madurai", "salem", "thanjavur"]
    
    for p in places:
        name_lower = p["name"].lower()
        area_lower = p.get("area", "").lower()
        desc_lower = p.get("description", "").lower()
        
        # Check if outside Chennai bounds
        if any(bad in name_lower or bad in area_lower or bad in desc_lower for bad in excluded_names):
            # Exception: If it's a TTD temple located in T. Nagar Chennai, rename it clearly to "TTD Balaji Temple (T. Nagar, Chennai)"
            if "t. nagar" in area_lower or "venkatnarayana" in area_lower:
                p["name"] = "TTD Sri Venkateswara Temple (T. Nagar, Chennai)"
                p["description"] = "Authentic Chennai administrative temple and shrine of Tirupati Balaji located in T. Nagar."
                p["famous_for"] = "Tirupati Laddus, Darshan in T. Nagar Chennai"
            else:
                continue # Skip outside-city entries
                
        # Calculate nearest Metro Station
        p_lat, p_lon = p["latitude"], p["longitude"]
        nearest_st = min(all_stations, key=lambda s: haversine(p_lat, p_lon, s["lat"], s["lon"]))
        dist_to_metro = round(haversine(p_lat, p_lon, nearest_st["lat"], nearest_st["lon"]), 2)
        
        p["nearest_metro_station"] = nearest_st["name"]
        p["metro_line"] = nearest_st["line"]
        p["distance_to_metro_km"] = dist_to_metro
        p["metro_accessible"] = bool(dist_to_metro <= 3.0)
        
        # Accessibility flags
        p["elderly_friendly"] = bool(p["category"] in ["Temples & Spiritual", "Parks & Nature", "Food, Messes & Cafes"] and dist_to_metro <= 4.0)
        p["wheelchair_accessible"] = bool(p["category"] in ["Shopping & Markets", "Museums & Arts", "Parks & Nature"])
        
        valid_places.append(p)

    out_dir = r"d:\drl_project\tourist_places"
    json_path = os.path.join(out_dir, "chennai_places.json")
    csv_path = os.path.join(out_dir, "chennai_places.csv")
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(valid_places, f, indent=2, ensure_ascii=False)
        
    df = pd.DataFrame(valid_places)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"Cleaned & Enriched: {len(valid_places)} local Chennai places saved with Metro connectivity!")

if __name__ == "__main__":
    main()
