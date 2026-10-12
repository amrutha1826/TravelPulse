"""
Enrich Chennai Hotels with check-in/out schedules, room capacities, and Metro station connections.
"""
import os
import json
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
                "line": line["line_name"]
            })
            
    hotels_file = r"d:\drl_project\hotels\chennai_hotels.csv"
    if not os.path.exists(hotels_file):
        print("Hotels file missing!")
        return
        
    df = pd.read_csv(hotels_file)
    
    check_in_times = []
    check_out_times = []
    room_capacities = []
    nearest_metros = []
    dist_metros = []
    
    for _, row in df.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        nearest_st = min(all_stations, key=lambda s: haversine(lat, lon, s["lat"], s["lon"]))
        dist = round(haversine(lat, lon, nearest_st["lat"], nearest_st["lon"]), 2)
        
        nearest_metros.append(nearest_st["name"])
        dist_metros.append(dist)
        
        # Standard hotel check-in/out policies
        cat = str(row.get("category", "Standard"))
        if cat == "Luxury":
            check_in_times.append("14:00")
            check_out_times.append("12:00")
            room_capacities.append(3)
        elif cat == "Backpacker Hostel":
            check_in_times.append("12:00")
            check_out_times.append("10:00")
            room_capacities.append(1)
        else:
            check_in_times.append("12:00")
            check_out_times.append("11:00")
            room_capacities.append(2)
            
    df["check_in_time"] = check_in_times
    df["check_out_time"] = check_out_times
    df["room_capacity"] = room_capacities
    df["nearest_metro_station"] = nearest_metros
    df["distance_to_metro_km"] = dist_metros
    
    df.to_csv(hotels_file, index=False, encoding="utf-8")
    print(f"Enriched {len(df)} hotels with check-in/out policies and Metro links!")

if __name__ == "__main__":
    main()
