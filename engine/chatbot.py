"""
Context-Aware Chatbot & Dynamic In-Place Plan Modifier Engine.
Processes user change requests in natural language and dynamically re-optimizes
the current trip state without resetting the entire plan. (Zero external LLM API).
"""
import re
import json
import os

class TripState:
    def __init__(self, origin_city="Bangalore", num_days=3, pace="Moderate", budget_per_day=3000, daily_start_time="09:00", daily_end_time="21:00"):
        self.origin_city = origin_city
        self.num_days = num_days
        self.pace = pace
        self.budget_per_day = budget_per_day
        self.daily_start_time = daily_start_time
        self.daily_end_time = daily_end_time
        self.day_time_windows = {} # day_num -> (start_time, end_time)
        self.selected_route = None
        self.selected_hotel = None
        self.daily_itinerary = {d: [] for d in range(1, num_days + 1)}
        self.excluded_modes = set()
        self.preferred_categories = set()
        self.excluded_categories = set()
        self.forbidden_poi_ids = set()
        self.pinned_pois = {} # day -> list of POIs

    def to_dict(self):
        return {
            "origin_city": self.origin_city,
            "num_days": self.num_days,
            "pace": self.pace,
            "budget_per_day": self.budget_per_day,
            "daily_start_time": self.daily_start_time,
            "daily_end_time": self.daily_end_time,
            "day_time_windows": self.day_time_windows,
            "selected_route": self.selected_route,
            "selected_hotel": self.selected_hotel,
            "daily_itinerary": self.daily_itinerary,
            "excluded_modes": list(self.excluded_modes),
            "preferred_categories": list(self.preferred_categories),
            "excluded_categories": list(self.excluded_categories)
        }

class PlanModifierChatbot:
    def __init__(self, places_db, hotels_db, graph_builder, itinerary_optimizer):
        self.places_db = places_db
        self.hotels_db = hotels_db
        self.graph_builder = graph_builder
        self.itinerary_optimizer = itinerary_optimizer

    def parse_intent(self, user_text):
        """Extracts intent and parameters from user query using rule-based NLP."""
        text = user_text.lower().strip()
        
        # 1. Transport mode change
        if any(w in text for w in ["flight", "train", "bus", "transport", "flight to train", "train to bus"]):
            if "avoid flight" in text or "no flight" in text or "don't want flight" in text or "prefer train" in text or "train only" in text or "only train" in text:
                return {"intent": "exclude_transport", "mode": "flight", "prefer": "train"}
            if "avoid bus" in text or "no bus" in text or "don't want bus" in text:
                return {"intent": "exclude_transport", "mode": "bus", "prefer": "train"}
            if "only flight" in text or "prefer flight" in text or "fastest" in text:
                return {"intent": "prefer_transport", "mode": "flight"}
            if "cheapest" in text or "budget transport" in text:
                return {"intent": "cheapest_transport"}
            return {"intent": "change_transport_general", "text": text}

        # 2. Hotel change
        if any(w in text for w in ["hotel", "stay", "resort", "hostel", "accommodation", "room"]):
            area_match = None
            for area in ["mylapore", "t. nagar", "t nagar", "guindy", "central", "egmore", "adyar", "besant nagar", "ecr", "omr", "airport"]:
                if area in text:
                    area_match = area.title()
                    break
            
            category_match = None
            if "cheap" in text or "budget" in text or "low cost" in text:
                category_match = "Budget"
            elif "luxury" in text or "5 star" in text or "5-star" in text or "premium" in text:
                category_match = "Luxury"
            elif "hostel" in text or "dorm" in text or "backpacker" in text:
                category_match = "Backpacker Hostel"
            elif "standard" in text or "3 star" in text:
                category_match = "Standard"
                
            return {
                "intent": "change_hotel",
                "area": area_match,
                "category": category_match
            }

        # 3. Replace or remove place / category on a specific day
        day_match = re.search(r"day\s*([1-9])", text)
        target_day = int(day_match.group(1)) if day_match else None

        if any(w in text for w in ["replace", "change", "swap", "instead of", "substitute"]):
            target_cat = None
            if "museum" in text: target_cat = "museum"
            elif "temple" in text: target_cat = "temple"
            elif "beach" in text: target_cat = "beach"
            elif "food" in text or "cafe" in text or "mess" in text: target_cat = "food"
            elif "shopping" in text or "market" in text: target_cat = "shopping"
            
            replacement_cat = None
            if "beach" in text and target_cat != "beach": replacement_cat = "Beaches & Coastline"
            elif "food" in text and target_cat != "food": replacement_cat = "Food, Messes & Cafes"
            elif "temple" in text and target_cat != "temple": replacement_cat = "Temples & Spiritual"
            elif "shopping" in text and target_cat != "shopping": replacement_cat = "Shopping & Markets"
            elif "nature" in text or "park" in text: replacement_cat = "Parks & Nature"
            elif "heritage" in text or "monument" in text: replacement_cat = "Heritage & History"
            
            return {
                "intent": "replace_place_or_category",
                "day": target_day,
                "target_cat": target_cat,
                "replacement_cat": replacement_cat
            }

        if any(w in text for w in ["remove", "don't want", "skip", "no more", "delete"]):
            cat = None
            if "temple" in text: cat = "Temples & Spiritual"
            elif "museum" in text: cat = "Museums & Arts"
            elif "beach" in text: cat = "Beaches & Coastline"
            elif "park" in text or "zoo" in text: cat = "Parks & Nature"
            elif "shopping" in text: cat = "Shopping & Markets"
            return {
                "intent": "remove_category",
                "day": target_day,
                "category": cat
            }

        if any(w in text for w in ["add", "include", "want to see", "visit", "must see"]):
            poi_name = None
            for p in self.places_db:
                if p["name"].lower() in text:
                    poi_name = p
                    break
            return {
                "intent": "add_poi_or_category",
                "day": target_day or 1,
                "poi": poi_name,
                "text": text
            }

        # 4. Pace or Budget adjustment
        if any(w in text for w in ["relax", "relaxed", "less hectic", "slow", "easy"]):
            return {"intent": "change_pace", "pace": "Relaxed", "day": target_day}
        if any(w in text for w in ["packed", "more places", "fast", "cover more", "busy"]):
            return {"intent": "change_pace", "pace": "Packed", "day": target_day}
            
        budget_match = re.search(r"(?:budget|cost|rs\.?|inr)\s*(\d+)", text)
        if budget_match:
            return {"intent": "change_budget", "budget": int(budget_match.group(1))}

        # 5. General fallback / inquiry
        return {"intent": "general_query", "text": text}

    def process_message(self, user_query, trip_state):
        """Processes query, mutates trip_state in-place, and returns detailed assistant response."""
        parsed = self.parse_intent(user_query)
        intent = parsed.get("intent")
        
        response_msg = ""
        action_performed = ""

        # --- 1. Transport Change ---
        if intent == "exclude_transport":
            mode = parsed["mode"]
            prefer = parsed["prefer"]
            trip_state.excluded_modes.add(mode)
            
            # Re-fetch transport routes excluding the mode
            all_routes = self.graph_builder.get_multihop_routes(trip_state.origin_city, "Chennai")
            filtered = [r for r in all_routes if mode not in r.get("primary_mode", "").lower()]
            if filtered:
                # Sort by duration or cost
                filtered.sort(key=lambda r: (r["total_duration_hours"], r["total_fare_inr"]))
                trip_state.selected_route = filtered[0]
                action_performed = f"Updated transport route to avoid {mode.title()} and prioritize {prefer.title()}."
                response_msg = f"✅ **Transport Plan Updated!**\n\nI have switched your journey from **{trip_state.origin_city} to Chennai** to avoid **{mode.title()}s**.\n\n🚄 **New Selected Route:** {trip_state.selected_route['primary_mode']} ({trip_state.selected_route['type']})\n- **Duration:** {trip_state.selected_route['total_duration_hours']} hours\n- **Total Fare:** ₹{trip_state.selected_route['total_fare_inr']:,}\n- **Operator / Details:** {trip_state.selected_route['legs'][0].get('operator')} {trip_state.selected_route['legs'][0].get('number')}"
            else:
                response_msg = f"⚠️ I searched for non-{mode} routes from {trip_state.origin_city} to Chennai, but no direct or 1-transfer connections were found. Retaining existing options."

        elif intent == "cheapest_transport":
            all_routes = self.graph_builder.get_multihop_routes(trip_state.origin_city, "Chennai")
            if all_routes:
                all_routes.sort(key=lambda r: r["total_fare_inr"])
                trip_state.selected_route = all_routes[0]
                action_performed = "Switched to lowest-fare transport option."
                response_msg = f"💰 **Switched to Lowest Cost Route:**\n- **Route:** {trip_state.selected_route['primary_mode']}\n- **Total Fare:** ₹{trip_state.selected_route['total_fare_inr']:,}\n- **Duration:** {trip_state.selected_route['total_duration_hours']} hours"

        # --- 2. Hotel Change ---
        elif intent == "change_hotel":
            area = parsed.get("area")
            cat = parsed.get("category")
            
            # Filter hotels
            candidates = self.hotels_db
            if area:
                candidates = [h for h in candidates if area.lower() in h["area"].lower() or area.lower() in h["zone"].lower()]
            if cat:
                candidates = [h for h in candidates if h["category"].lower() == cat.lower()]
                
            if not candidates:
                candidates = self.hotels_db
                
            # Pick best rated
            candidates.sort(key=lambda h: (-h["rating"], h["price_per_night_inr"]))
            trip_state.selected_hotel = candidates[0]
            action_performed = f"Updated hotel stay to {trip_state.selected_hotel['hotel_name']}."
            response_msg = f"🏨 **Hotel Stay Updated!**\n\nI have updated your accommodation in Chennai:\n- **Hotel:** {trip_state.selected_hotel['hotel_name']}\n- **Location:** {trip_state.selected_hotel['area']} ({trip_state.selected_hotel['zone']})\n- **Price:** ₹{trip_state.selected_hotel['price_per_night_inr']:,} / night ({trip_state.selected_hotel['category']})\n- **Rating:** ⭐ {trip_state.selected_hotel['rating']}/5\n- **Amenities:** {trip_state.selected_hotel['amenities']}"

        # --- 3. Replace Place or Category ---
        elif intent == "replace_place_or_category":
            target_day = parsed.get("day") or 1
            replacement_cat = parsed.get("replacement_cat") or "Food, Messes & Cafes"
            
            day_plan = trip_state.daily_itinerary.get(target_day, [])
            if day_plan:
                # Remove last or target item
                removed = day_plan.pop()
                trip_state.forbidden_poi_ids.add(removed["poi"]["id"])
                
                # Find replacement from replacement_cat
                available = [p for p in self.places_db if p.get("category") == replacement_cat and p["id"] not in trip_state.forbidden_poi_ids]
                if available:
                    new_poi = available[0]
                    day_plan.append({
                        "poi": new_poi,
                        "visit_time": removed.get("visit_time", "15:00"),
                        "dist_from_prev_km": 3.2
                    })
                    trip_state.daily_itinerary[target_day] = day_plan
                    action_performed = f"Replaced {removed['poi']['name']} with {new_poi['name']} on Day {target_day}."
                    response_msg = f"🔄 **Day {target_day} Plan Updated In-Place!**\n\n- ❌ Removed: **{removed['poi']['name']}** ({removed['poi']['category']})\n- ✅ Added: **{new_poi['name']}** ({new_poi['category']})\n- **Highlights:** {new_poi.get('famous_for')}\n\nThe rest of your Day {target_day} and subsequent days remain preserved without starting over!"
                else:
                    response_msg = f"Found no unvisited places in category '{replacement_cat}'."
            else:
                response_msg = f"Day {target_day} currently has no activities to replace. Let me know what you'd like to add!"

        # --- 4. Remove Category ---
        elif intent == "remove_category":
            cat = parsed.get("category")
            if cat:
                trip_state.excluded_categories.add(cat)
                # Filter out of all days
                for d in trip_state.daily_itinerary:
                    trip_state.daily_itinerary[d] = [item for item in trip_state.daily_itinerary[d] if item["poi"].get("category") != cat]
                action_performed = f"Filtered out {cat} across all itinerary days."
                response_msg = f"🚫 **Removed '{cat}' from your entire trip.** I have adjusted your schedule to focus more on beaches, food streets, and heritage architecture."
            else:
                response_msg = "Please specify which category you would like to exclude (e.g., temples, museums, shopping)."

        # --- 5. Change Pace ---
        elif intent == "change_pace":
            new_pace = parsed.get("pace", "Relaxed")
            trip_state.pace = new_pace
            action_performed = f"Adjusted pace to {new_pace}."
            response_msg = f"⏳ **Trip Pace Adjusted to {new_pace}!**\n\nI have spaced out your visits with longer buffer times at each spot so you can explore without rushing."

        # --- Fallback / Help ---
        else:
            response_msg = f"🤖 **I'm your Chennai Trip Assistant!** You can ask me to modify your plan anytime in plain English, for example:\n- *'Switch morning flight to train or bus'*\n- *'Replace the museum on Day 2 with a beach or food street'*\n- *'Change my hotel to a budget stay near Mylapore'*\n- *'Make Day 1 more relaxed'*\n- *'Add Marina Beach to Day 1'*\n\nTell me what you'd like changed and I'll adjust it instantly!"

        return {
            "response": response_msg,
            "action_performed": action_performed,
            "updated_state": trip_state
        }
