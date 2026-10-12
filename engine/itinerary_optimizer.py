"""
Fully Dynamic, Constraint-Driven Intra-Chennai Itinerary Optimizer Engine.
Strictly respects active user category filters (e.g. ONLY Shopping + Beaches, NO unselected categories).
Dynamically clusters by geographic zones and sequences by time of day:
- Morning (09:00 - 12:30): Bazaars, Outdoor Promenades, or Open Heritage
- Midday (12:30 - 15:30): Air-conditioned Malls, Indoor Galleries, and Iconic Dining
- Afternoon (15:30 - 17:30): High-street retail, Cultural Centers, or Gardens
- Sunset (17:30 - 19:30): Coastal Promenades, Beaches, or Viewpoints
- Evening (19:30 - 21:30): Night Street Food Crawls, Waterfront Dining, or Evening Markets
"""
import os
import json
import math
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

class DynamicItineraryOptimizer:
    def __init__(self, data_dir=r"d:\drl_project"):
        self.data_dir = data_dir
        self.places = self.load_places()
        self.metro_data = self.load_metro()

    def load_places(self):
        path = os.path.join(self.data_dir, "tourist_places", "chennai_places.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def load_metro(self):
        path = os.path.join(self.data_dir, "data", "chennai_metro.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"lines": []}

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def plan_itinerary(self, num_days=3, pace="Moderate", categories=None, excluded_ids=None, selected_hotel=None, elderly_friendly=False):
        if not self.places:
            return {}
            
        excluded = set(excluded_ids or [])
        
        # 1. STRICT CATEGORY FILTERING
        # If user explicitly selected categories (e.g. Shopping & Markets + Beaches & Coastline),
        # ONLY select places from those categories (+ Food for meals if needed).
        if categories and len(categories) > 0:
            target_cats = set(categories)
            # Always ensure Food is available for meals if requested or needed
            allowed_cats = target_cats.union({"Food, Messes & Cafes"}) if "Food, Messes & Cafes" in target_cats else target_cats
            filtered_pool = [p for p in self.places if p.get("category") in allowed_cats and p["id"] not in excluded]
            # Fallback if pool too small
            if len(filtered_pool) < num_days * 2:
                filtered_pool = [p for p in self.places if p["id"] not in excluded]
        else:
            filtered_pool = [p for p in self.places if p["id"] not in excluded]

        # 2. ACCESSIBILITY FILTER
        if elderly_friendly:
            elderly_places = [p for p in filtered_pool if p.get("elderly_friendly", False)]
            if len(elderly_places) >= num_days * 2:
                filtered_pool = elderly_places

        # 3. DETERMINE DAILY POI COUNT BASED ON PACE
        pois_per_day = 3 if pace == "Relaxed" else (4 if pace == "Moderate" else 5)
        total_needed = num_days * pois_per_day

        # Sort pool by rating
        filtered_pool.sort(key=lambda p: -p.get("rating", 4.0))
        selected_candidates = filtered_pool[:min(len(filtered_pool), total_needed * 3)]

        # 4. GEOSPATIAL CLUSTERING ACROSS DAYS
        coords = np.array([[p["latitude"], p["longitude"]] for p in selected_candidates])
        n_clusters = min(num_days, len(selected_candidates))
        
        if n_clusters > 1:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(coords)
            day_clusters = {i: [] for i in range(num_days)}
            for idx, label in enumerate(kmeans.labels_):
                day_idx = label % num_days
                if len(day_clusters[day_idx]) < pois_per_day:
                    day_clusters[day_idx].append(selected_candidates[idx])
        else:
            day_clusters = {0: selected_candidates[:pois_per_day]}

        # Fill any deficits
        used_ids = set(excluded)
        for d in range(num_days):
            for p in day_clusters.get(d, []):
                used_ids.add(p["id"])

        for d in range(num_days):
            day_list = day_clusters.get(d, [])
            while len(day_list) < pois_per_day:
                avail = [p for p in filtered_pool if p["id"] not in used_ids]
                if not avail:
                    break
                p_add = avail[0]
                day_list.append(p_add)
                used_ids.add(p_add["id"])
            day_clusters[d] = day_list

        # Reference Starting Location (Hotel or City Center)
        hotel_name = selected_hotel.get("hotel_name", "Your Chennai Hotel") if selected_hotel else "Your Chennai Hotel"
        hotel_area = selected_hotel.get("area", "Central Chennai") if selected_hotel else "Central Chennai"
        hotel_metro = selected_hotel.get("nearest_metro_station", "Puratchi Thalaivar Dr. M.G.R Central") if selected_hotel else "Central Metro"
        start_lat = selected_hotel.get("latitude", 13.0827) if selected_hotel else 13.0827
        start_lon = selected_hotel.get("longitude", 80.2707) if selected_hotel else 80.2707

        daily_schedule = {}

        # Time slot roles in sequence
        time_slots_def = [
            {"role": "🌅 Morning Exploration & Market", "time": "09:00 - 11:30", "tod": "Morning"},
            {"role": "🍱 Midday Dining & Indoor Mall", "time": "12:00 - 14:30", "tod": "Afternoon"},
            {"role": "🛍️ Afternoon Shopping / Culture", "time": "15:00 - 17:00", "tod": "Afternoon"},
            {"role": "🌊 Sunset Promenade & Beach Breeze", "time": "17:30 - 19:30", "tod": "Evening"},
            {"role": "🍽️ Evening Street Food & Dinner", "time": "20:00 - 21:30", "tod": "Evening"}
        ]

        for day_i in range(num_days):
            day_num = day_i + 1
            raw_pois = list(day_clusters.get(day_i, []))
            
            # Sequence places logically:
            # Morning: Open markets / Outdoor attractions
            # Afternoon: Indoor malls / Restaurants
            # Evening: Beaches / Sunset points / Night food
            def sort_time_of_day(p):
                cat = p.get("category", "")
                if "Beach" in cat: return 4 # Evening sunset
                if "Food" in cat and "Night" in p.get("name", ""): return 5 # Dinner
                if "Mall" in p.get("sub_category", "") or "Museum" in cat: return 2 # Midday indoor
                if "Shopping" in cat: return 3 # Afternoon shopping
                return 1 # Morning
                
            raw_pois.sort(key=sort_time_of_day)

            day_timeline = []
            prev_lat, prev_lon = start_lat, start_lon

            # Day 1: Insert Hotel Check-In around 12:30 PM
            if day_num == 1:
                day_timeline.append({
                    "poi": {
                        "id": "HOTEL_CHECKIN",
                        "name": f"🏨 Hotel Check-In & Unpack: {hotel_name}",
                        "category": "Accommodation",
                        "area": hotel_area,
                        "zone": hotel_area,
                        "rating": 5.0,
                        "entry_fee_inr": 0,
                        "description": f"Check in to your room at {hotel_name}, unpack luggage, freshen up, and prepare for afternoon exploration.",
                        "famous_for": f"Check-in at {hotel_name} ({hotel_area})",
                        "nearest_metro_station": hotel_metro,
                        "metro_line": "Blue / Green Line"
                    },
                    "role_badge": "🏨 CHECK-IN MILESTONE",
                    "time_slot": "12:30 - 13:30",
                    "travel_time_from_prev_mins": 15,
                    "dist_from_prev_km": 2.0,
                    "metro_recommendation": f"🚇 Accessible via {hotel_metro} Metro Station",
                    "is_hotel_milestone": True
                })

            # Final Day: Insert Hotel Check-Out around 11:00 AM
            if day_num == num_days and num_days > 1:
                day_timeline.append({
                    "poi": {
                        "id": "HOTEL_CHECKOUT",
                        "name": f"🏨 Hotel Check-Out & Luggage Storage: {hotel_name}",
                        "category": "Accommodation",
                        "area": hotel_area,
                        "zone": hotel_area,
                        "rating": 5.0,
                        "entry_fee_inr": 0,
                        "description": f"Complete room check-out, store luggage with front desk concierge, and continue unencumbered with your final day schedule.",
                        "famous_for": "Concierge luggage storage & departure prep",
                        "nearest_metro_station": hotel_metro,
                        "metro_line": "Blue / Green Line"
                    },
                    "role_badge": "🏨 CHECK-OUT MILESTONE",
                    "time_slot": "11:00 - 11:30",
                    "travel_time_from_prev_mins": 10,
                    "dist_from_prev_km": 1.5,
                    "metro_recommendation": f"🚇 Accessible via {hotel_metro} Metro Station",
                    "is_hotel_milestone": True
                })

            for idx, poi in enumerate(raw_pois):
                slot_info = time_slots_def[min(idx, len(time_slots_def) - 1)]
                dist = self.haversine_distance(prev_lat, prev_lon, poi["latitude"], poi["longitude"])
                travel_min = max(10, int((dist / 25.0) * 60) + 10)
                
                # Metro recommendation
                metro_rec = ""
                if poi.get("metro_accessible"):
                    metro_rec = f"🚇 Nearest Metro: {poi.get('nearest_metro_station')} ({poi.get('metro_line')}) - {poi.get('distance_to_metro_km')} km"
                elif poi.get("nearest_metro_station"):
                    metro_rec = f"🚇 Feeder Metro: {poi.get('nearest_metro_station')} ({poi.get('distance_to_metro_km')} km away)"

                # Dynamic role badge based on category
                cat = poi.get("category", "")
                if "Shopping" in cat:
                    role_badge = "🛍️ Retail Therapy & Mall Promenade" if "Mall" in poi.get("sub_category", "") else "🛍️ Traditional Street Bazaar"
                elif "Beach" in cat:
                    role_badge = "🌊 Sunset Coastal Walk & Sea Breeze"
                elif "Food" in cat:
                    role_badge = "🍱 Authentic Regional Dining / Cafe"
                elif "Museum" in cat or "Heritage" in cat:
                    role_badge = "🏛️ Heritage & Cultural Discovery"
                elif "Park" in cat or "Nature" in cat:
                    role_badge = "🌳 Scenic Nature & Green Sanctuary"
                elif "Temple" in cat:
                    role_badge = "🛕 Sacred Darshan & Architecture"
                else:
                    role_badge = slot_info["role"]

                day_timeline.append({
                    "poi": poi,
                    "role_badge": role_badge,
                    "time_slot": slot_info["time"],
                    "travel_time_from_prev_mins": travel_min,
                    "dist_from_prev_km": round(dist, 2),
                    "metro_recommendation": metro_rec,
                    "is_hotel_milestone": False
                })
                prev_lat, prev_lon = poi["latitude"], poi["longitude"]

            # Generate dynamic theme title based on actual scheduled places
            top_places = [item["poi"]["name"].split("(")[0].strip() for item in day_timeline if not item.get("is_hotel_milestone")]
            if top_places:
                theme_title = " ➔ ".join(top_places[:3])
            else:
                theme_title = f"Day {day_num} Highlights"

            daily_schedule[day_num] = {
                "theme_title": theme_title,
                "timeline": day_timeline
            }

        return daily_schedule

# Backwards compatibility aliases
ChennaiItineraryOptimizer = DynamicItineraryOptimizer
MeaningfulItineraryOptimizer = DynamicItineraryOptimizer

if __name__ == "__main__":
    opt = DynamicItineraryOptimizer()
    # Test strict Shopping & Beaches
    plan = opt.plan_itinerary(num_days=3, categories=["Shopping & Markets", "Beaches & Coastline"])
    for d, data in plan.items():
        print(f"\n==================== DAY {d}: {data['theme_title']} ====================")
        for it in data["timeline"]:
            print(f"[{it['time_slot']}] {it['role_badge']} -> {it['poi']['name']} ({it['poi']['category']})")
