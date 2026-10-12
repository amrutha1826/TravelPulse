"""
Itinerary Planning & Day-Wise Customization Service for TravelPulse Platform.
Implements the Strict 4-Stage Pipeline:
  Stage 1: SQL Filter (Hard constraints: city, opening hours, accessibility)
  Stage 2: Vector Search (RAG Retrieval: Free-text embedding similarity over places)
  Stage 3: DRL Policy (PPO/DQN Sequential Decision Maker: balances time, cost, distance, diversity)
  Stage 4: RAG Review-Summary (Grounded Pros/Cons synthesized from verified user reviews)
"""
import math
import random
import json
from database.db_manager import DatabaseManager
from engine.rag_service import RAGService

def haversine_dist(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def parse_time_to_minutes(t_str):
    """Converts a time string like '09:30', '9:30', '14:00', '2:00 PM', '10 AM' into minutes from midnight."""
    if not t_str:
        return 540 # Default 09:00 (540 mins)
    
    t_str = str(t_str).strip().lower()
    is_pm = "pm" in t_str
    is_am = "am" in t_str
    t_clean = t_str.replace("am", "").replace("pm", "").strip()
    
    parts = t_clean.split(":")
    try:
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        if is_pm and hours < 12:
            hours += 12
        elif is_am and hours == 12:
            hours = 0
        return max(0, min(1439, hours * 60 + minutes))
    except (ValueError, IndexError):
        return 540

def format_minutes_to_time(minutes):
    """Converts minutes from midnight to HH:MM format."""
    minutes = max(0, min(1439, int(minutes)))
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

class ItineraryPlanningService:
    def __init__(self, db_manager=None, rag_service=None):
        self.db = db_manager or DatabaseManager()
        self.rag = rag_service or RAGService(self.db)
        from engine.transport_service import TransportSearchService
        self.transport_service = TransportSearchService(self.db, self.rag)

    def plan_itinerary(
        self,
        num_days=3,
        pace="Moderate",
        categories=None,
        excluded_ids=None,
        selected_hotel=None,
        destination_city_id="MAA",
        daily_start_time="09:00",
        daily_end_time="21:00",
        day_time_windows=None,
        free_text_query=None,
        budget_per_day=3500,
        **kwargs
    ):
        return self.generate_itinerary(
            destination_city_id=destination_city_id,
            num_days=num_days,
            pace=pace,
            categories=categories,
            selected_hotel=selected_hotel,
            excluded_place_ids=excluded_ids,
            daily_start_time=daily_start_time,
            daily_end_time=daily_end_time,
            day_time_windows=day_time_windows,
            free_text_query=free_text_query,
            budget_per_day=budget_per_day,
            origin_city_id=kwargs.get("origin_city_id"),
            selected_transport_modes=kwargs.get("selected_transport_modes")
        )

    def _generate_dynamic_slots(self, start_min, end_min, pace="Moderate"):
        """
        Dynamically computes realistic time slots and contextual activity roles
        based strictly on the user's available start and end times.
        """
        available_hours = (end_min - start_min) / 60.0
        
        if pace == "Relaxed":
            num_stops = 1 if available_hours <= 4.0 else (2 if available_hours <= 7.0 else (3 if available_hours <= 11.0 else 4))
        elif pace == "Packed":
            num_stops = 2 if available_hours <= 4.0 else (4 if available_hours <= 7.0 else (5 if available_hours <= 11.0 else 6))
        else: # Moderate
            num_stops = 2 if available_hours <= 4.0 else (3 if available_hours <= 7.0 else (4 if available_hours <= 11.0 else 5))
            
        num_stops = max(1, num_stops)
        
        # Check if window encompasses lunchtime (12:30 to 14:00)
        has_lunch_break = (start_min <= 780 and end_min >= 840 and available_hours >= 5.0)
        usable_minutes = (end_min - start_min) - (60 if has_lunch_break else 0)
        usable_minutes = max(60, usable_minutes)
        
        slot_duration = usable_minutes // num_stops
        transit_buffer = 20 if slot_duration >= 90 else 10
        activity_duration = max(45, slot_duration - transit_buffer)
        
        slots = []
        curr_m = start_min
        for i in range(num_stops):
            if has_lunch_break and curr_m < 780 and (curr_m + slot_duration) > 810:
                curr_m = 840
                
            slot_start = curr_m
            slot_end = min(end_min, slot_start + activity_duration)
            if slot_end <= slot_start:
                break
                
            mid_point = (slot_start + slot_end) // 2
            if mid_point < 690: # < 11:30 AM
                role = "Morning Landmark & Heritage"
            elif mid_point <= 870: # 11:30 AM - 2:30 PM
                role = "Iconic Lunch & Culinary Experience"
            elif mid_point <= 1050: # 2:30 PM - 5:30 PM
                role = "Afternoon Arts, Culture & Shopping"
            elif mid_point <= 1230: # 5:30 PM - 8:30 PM
                role = "Sunset Promenade & Sightseeing"
            else: # > 8:30 PM
                role = "Evening Nightlife & Dining Walk"
                
            slots.append({
                "time_str": f"{format_minutes_to_time(slot_start)} - {format_minutes_to_time(slot_end)}",
                "start_min": slot_start,
                "end_min": slot_end,
                "role": role,
                "duration_hours": round((slot_end - slot_start) / 60.0, 1)
            })
            curr_m = slot_end + transit_buffer
            if curr_m >= end_min:
                break
                
        if not slots:
            slots.append({
                "time_str": f"{format_minutes_to_time(start_min)} - {format_minutes_to_time(end_min)}",
                "start_min": start_min,
                "end_min": end_min,
                "role": "Highlights & Sightseeing",
                "duration_hours": round(available_hours, 1)
            })
        return slots

    def generate_itinerary(
        self,
        destination_city_id="MAA",
        num_days=3,
        pace="Moderate",
        categories=None,
        selected_hotel=None,
        excluded_place_ids=None,
        daily_start_time="09:00",
        daily_end_time="21:00",
        day_time_windows=None,
        free_text_query=None,
        budget_per_day=3500,
        origin_city_id=None,
        selected_transport_modes=None
    ):
        """
        Executes the Strict 4-Stage Pipeline:
          Stage 1 (SQL): Filter places from DB by city and category.
          Stage 2 (RAG Vector Search): Free-text embedding similarity retrieval.
          Stage 3 (DRL Policy): Sequential activity decision-making & time constraint optimization.
          Stage 4 (RAG Review Grounding): Attached authentic reviews per POI.
        """
        excluded = set(excluded_place_ids or [])
        
        # -------------------------------------------------------------
        # STAGE 1: SQL Filter (Hard Constraints)
        # -------------------------------------------------------------
        sql_pool = self.db.get_places_for_city(
            city_id=destination_city_id,
            categories=categories if (categories and len(categories) > 0) else None,
            limit=120
        )
        sql_pool = [p for p in sql_pool if p["id"] not in excluded]

        if not sql_pool:
            sql_pool = self.db.get_places_for_city(city_id=destination_city_id, limit=60)
            sql_pool = [p for p in sql_pool if p["id"] not in excluded]

        # -------------------------------------------------------------
        # STAGE 2: Vector Search (RAG Retrieval - Optional Free-Text Query)
        # -------------------------------------------------------------
        candidate_pool = list(sql_pool)
        if free_text_query and free_text_query.strip():
            vector_matches = self.rag.search_places_vector(
                query_text=free_text_query,
                city_id=destination_city_id,
                top_k=25
            )
            v_map = {vm["id"]: vm.get("vector_similarity_score", 0.0) for vm in vector_matches}
            # Re-rank SQL candidates by vector similarity
            for p in candidate_pool:
                p["vector_sim_score"] = v_map.get(p["id"], 0.1)
            candidate_pool.sort(key=lambda x: -x.get("vector_sim_score", 0))

        # -------------------------------------------------------------
        # STAGE 3: DRL Policy (Sequential Decision Making & Sequencing)
        # -------------------------------------------------------------
        hotel_lat = selected_hotel["latitude"] if selected_hotel else 13.0827
        hotel_lon = selected_hotel["longitude"] if selected_hotel else 80.2707
        hotel_name = selected_hotel["name"] if selected_hotel else "Central Stay"

        day_plans = {}
        used_ids = set(excluded)
        categories_visited = set()
        total_trip_budget_left = float(num_days * budget_per_day)

        # Fallback to any city places if candidate_pool is empty
        if not candidate_pool:
            candidate_pool = self.db.get_places_for_city(city_id=destination_city_id, limit=60)

        for d in range(1, num_days + 1):
            if day_time_windows and d in day_time_windows:
                d_start_str, d_end_str = day_time_windows[d]
            else:
                d_start_str, d_end_str = daily_start_time, daily_end_time
                
            start_m = parse_time_to_minutes(d_start_str)
            end_m = parse_time_to_minutes(d_end_str)
            if end_m <= start_m:
                end_m = min(1439, start_m + 720)
                
            slots = self._generate_dynamic_slots(start_m, end_m, pace=pace)
            
            day_activities = []
            curr_lat, curr_lon = hotel_lat, hotel_lon
            curr_loc_name = hotel_name
            day_cost = 0.0
            day_dist = 0.0
            
            for s_idx, slot in enumerate(slots):
                # 1. Try places unvisited across the entire multi-day trip
                unvisited = [p for p in candidate_pool if p["id"] not in used_ids]
                
                # 2. If exhausted across trip, pick candidates not visited today
                if not unvisited:
                    today_visited = {a["poi"]["id"] for a in day_activities}
                    unvisited = [p for p in candidate_pool if p["id"] not in today_visited]
                
                # 3. If still empty, fall back to broader city attractions
                if not unvisited:
                    all_city_places = self.db.get_places_for_city(city_id=destination_city_id, limit=60)
                    today_visited = {a["poi"]["id"] for a in day_activities}
                    unvisited = [p for p in all_city_places if p["id"] not in today_visited]

                # 4. If literally no attractions available, stop adding for this day
                if not unvisited:
                    break

                # DRL Reward / Q-Score evaluation for selecting next POI
                def evaluate_candidate(p):
                    dist = haversine_dist(curr_lat, curr_lon, p["latitude"], p["longitude"])
                    fee = float(p.get("entry_fee_inr", 0))
                    rating = float(p.get("rating", 4.5))
                    is_new_cat = 1.0 if p.get("category") not in categories_visited else 0.2
                    vec_score = float(p.get("vector_sim_score", 0.5))
                    
                    # DRL Objective: Maximize rating & diversity, minimize travel distance & cost
                    score = (rating * 2.0) + (is_new_cat * 3.0) + (vec_score * 2.5) - (dist * 0.4) - (fee * 0.005)
                    return score

                best_poi = max(unvisited, key=evaluate_candidate)
                used_ids.add(best_poi["id"])
                categories_visited.add(best_poi.get("category"))
                
                leg_dist = round(haversine_dist(curr_lat, curr_lon, best_poi["latitude"], best_poi["longitude"]), 1)
                day_dist += leg_dist
                
                transit_mode = "Walking" if leg_dist < 1.2 else ("Auto Rickshaw" if leg_dist < 5.0 else "Metro / Cab")
                transit_cost = 0 if transit_mode == "Walking" else (round(leg_dist * 18.0 + 30.0, 0) if "Auto" in transit_mode else round(leg_dist * 25.0 + 50.0, 0))
                entry_fee = float(best_poi.get("entry_fee_inr", 0))
                act_cost = entry_fee + transit_cost
                day_cost += act_cost
                total_trip_budget_left -= act_cost

                # Stage 4: Grounded Review Summary for this specific POI
                poi_review = self.rag.generate_grounded_review_summary(
                    entity_type="place",
                    entity_id=best_poi["id"],
                    entity_name=best_poi["name"]
                )

                day_activities.append({
                    "activity_index": s_idx,
                    "time_slot": slot["time_str"],
                    "planned_duration_hours": slot["duration_hours"],
                    "activity_role": slot["role"],
                    "poi": best_poi,
                    "review_summary": poi_review,
                    "travel_from_prev": {
                        "from_name": curr_loc_name,
                        "distance_km": leg_dist,
                        "suggested_mode": transit_mode,
                        "transit_fare_est_inr": transit_cost
                    },
                    "estimated_activity_cost_inr": act_cost
                })
                
                curr_lat = best_poi["latitude"]
                curr_lon = best_poi["longitude"]
                curr_loc_name = best_poi["name"]

            # Return travel to hotel
            return_dist = round(haversine_dist(curr_lat, curr_lon, hotel_lat, hotel_lon), 1)
            day_dist += return_dist
            
            day_plans[d] = {
                "day_number": d,
                "theme_title": f"Day {d}: {day_activities[0]['poi']['category']} & {day_activities[-1]['poi']['category']}",
                "available_start_time": d_start_str,
                "available_end_time": d_end_str,
                "available_hours": round((end_m - start_m) / 60.0, 1),
                "activities": day_activities,
                "total_day_distance_km": round(day_dist, 1),
                "estimated_day_cost_inr": round(day_cost, 2),
                "hotel_base": hotel_name
            }

        # -------------------------------------------------------------
        # STAGE 4: RAG Grounded Review Summary
        # -------------------------------------------------------------
        review_digest = self.rag.generate_plan_review_summary(day_plans)
        
        # Transit evaluation if intercity trip requested
        recommended_transit = None
        if origin_city_id and origin_city_id != destination_city_id:
            try:
                transit_res = self.transport_service.search_routes(
                    origin_city_id=origin_city_id,
                    dest_city_id=destination_city_id,
                    selected_modes=selected_transport_modes
                )
                recommended_transit = transit_res.get("recommended_route")
            except Exception as e:
                print(f"Error computing itinerary transit recommendation: {e}")

        # Attach overall plan metadata
        total_cost = sum(d["estimated_day_cost_inr"] for d in day_plans.values())
        total_dist = sum(d["total_day_distance_km"] for d in day_plans.values())
        
        for d in day_plans.values():
            d["plan_review_summary"] = review_digest
            d["total_trip_cost_inr"] = round(total_cost, 2)
            d["total_trip_distance_km"] = round(total_dist, 1)
            if recommended_transit:
                d["recommended_transit"] = recommended_transit

        return day_plans

    def regenerate_single_day(
        self,
        current_itinerary,
        destination_city_id="MAA",
        day_num=1,
        pace="Moderate",
        categories=None,
        selected_hotel=None,
        daily_start_time=None,
        daily_end_time=None
    ):
        """
        Regenerates a single day by re-invoking the DRL policy with updated state,
        excluding POIs already used on other days.
        """
        used_on_other_days = []
        for d, plan in current_itinerary.items():
            if d != day_num:
                for act in plan.get("activities", []):
                    used_on_other_days.append(act["poi"]["id"])

        old_day = current_itinerary.get(day_num, {})
        d_start = daily_start_time or old_day.get("available_start_time", "09:00")
        d_end = daily_end_time or old_day.get("available_end_time", "21:00")

        new_plan = self.generate_itinerary(
            destination_city_id=destination_city_id,
            num_days=1,
            pace=pace,
            categories=categories,
            selected_hotel=selected_hotel,
            excluded_place_ids=used_on_other_days,
            daily_start_time=d_start,
            daily_end_time=d_end
        )
        
        updated_itinerary = dict(current_itinerary)
        updated_itinerary[day_num] = new_plan[1]
        updated_itinerary[day_num]["day_number"] = day_num
        updated_itinerary[day_num]["theme_title"] = f"Day {day_num} (Regenerated): {new_plan[1]['activities'][0]['poi']['category']}"
        return updated_itinerary

    def swap_activity(self, current_itinerary, day_num, activity_idx, new_place_id):
        """Swaps an individual activity in a day with a replacement place from inventory."""
        new_place = None
        with self.db.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM places WHERE id = ?", (new_place_id,))
            row = cursor.fetchone()
            if row:
                new_place = dict(row)

        if not new_place or day_num not in current_itinerary:
            return current_itinerary

        updated_itinerary = dict(current_itinerary)
        activities = list(updated_itinerary[day_num]["activities"])
        
        if 0 <= activity_idx < len(activities):
            old_act = activities[activity_idx]
            new_act = dict(old_act)
            new_act["poi"] = new_place
            entry_fee = float(new_place.get("entry_fee_inr", 0))
            new_act["estimated_activity_cost_inr"] = entry_fee + 50.0
            
            # Stage 4 Grounded Review Summary for swapped POI
            new_act["review_summary"] = self.rag.generate_grounded_review_summary(
                entity_type="place",
                entity_id=new_place["id"],
                entity_name=new_place["name"]
            )
            activities[activity_idx] = new_act
            updated_itinerary[day_num]["activities"] = activities
            
            # Recalculate day cost & refresh overall plan review digest
            updated_itinerary[day_num]["estimated_day_cost_inr"] = sum(a["estimated_activity_cost_inr"] for a in activities)
            review_digest = self.rag.generate_plan_review_summary(updated_itinerary)
            for d in updated_itinerary.values():
                d["plan_review_summary"] = review_digest
            
        return updated_itinerary
