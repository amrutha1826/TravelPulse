"""
Enhanced Custom NLU Chatbot & Conversational Replanner Engine.
Handles Day changes, Category focus, Pace adjustments, POI removals, Hotel updates, and Transport switches.
(Zero external LLM API dependency - 100% offline).
"""
import os
import re
import json
import random
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
import joblib

def levenshtein_similarity(s1, s2):
    s1, s2 = s1.lower().strip(), s2.lower().strip()
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
        
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
            
    return 1.0 - (dp[m][n] / max(m, n))

def generate_robust_nlu_data():
    """Generates 3,000+ diverse training queries covering all trip modification intents."""
    data = []
    
    # 1. change_days intent (both absolute and relative)
    days_templates = [
        "plan it for {d} days", "make it a {d} day trip", "change trip to {d} days",
        "i want a {d} days plan", "extend plan to {d} days", "reduce trip to {d} days",
        "make it {d} days", "plan for {d} days please", "can we do {d} days in chennai",
        "set days to {d}", "change duration to {d} days", "{d} days itinerary please",
        "can you add 1 more day for the trip", "add 1 more day", "add {d} days",
        "extend by 1 day", "increase by 1 day", "make it 1 day longer",
        "remove 1 day", "reduce by 1 day", "shorten trip by 1 day"
    ]
    for _ in range(400):
        d = random.randint(1, 7)
        data.append({"text": random.choice(days_templates).format(d=d), "intent": "change_days"})

    # 2. change_categories intent
    cat_templates = [
        "show only shopping and beaches", "i want only {c1} and {c2}", "focus on {c1}",
        "give me {c1} only", "only {c1} and {c2} please", "prefer {c1} and {c2}",
        "no temples only malls and beaches", "change interests to {c1}", "focus on malls and street food"
    ]
    sample_cats = ["shopping", "beaches", "malls", "food", "nature", "heritage", "temples"]
    for _ in range(350):
        c1, c2 = random.sample(sample_cats, 2)
        data.append({"text": random.choice(cat_templates).format(c1=c1, c2=c2), "intent": "change_categories"})

    # 3. remove_poi intent
    remove_templates = [
        "i dont want to visit {p}", "bro i dont want to visit {p} chane the itenirary",
        "remove {p} from plan", "skip {p}", "delete {p} from day {d}",
        "dont take me to {p}", "no {p} please", "exclude {p}", "take out {p}"
    ]
    sample_places = ["tirumala temple", "kapaleeshwarar", "marina beach", "egmore museum", "san thome", "fort st george", "rayars mess", "express avenue", "phoenix mall"]
    for _ in range(350):
        p = random.choice(sample_places)
        d = random.randint(1, 5)
        data.append({"text": random.choice(remove_templates).format(p=p, d=d), "intent": "remove_poi"})

    # 4. change_pace intent
    pace_templates = [
        "make day {d} more relaxed", "make it relaxed", "relaxed pace please",
        "slow down schedule", "make day {d} packed", "packed pace cover more",
        "too hectic make it easier", "less places per day"
    ]
    for _ in range(300):
        d = random.randint(1, 5)
        data.append({"text": random.choice(pace_templates).format(d=d), "intent": "change_pace"})

    # 5. change_transport intent (including exclusions and preferences)
    transport_templates = [
        "switch to train", "train only", "avoid flight", "no flights please", "no flights",
        "exclude flights", "hey remove flights", "remove flights", "dont want flights", "without flights",
        "exclude trains", "no train", "switch to flight", "bus only", "prefer flight", "cheapest bus",
        "fastest transport", "switch morning flight to train", "take train instead of flight", "remove plane"
    ]
    for _ in range(450):
        data.append({"text": random.choice(transport_templates), "intent": "change_transport"})

    # 6. change_hotel intent
    hotel_templates = [
        "change hotel to budget near {a}", "find cheaper stay in {a}", "switch to 5 star hotel in {a}",
        "backpacker hostel in {a}", "luxury stay near ecr", "change hotel to {a}"
    ]
    areas = ["mylapore", "t nagar", "guindy", "central", "adyar", "besant nagar", "ecr", "omr"]
    for _ in range(300):
        a = random.choice(areas)
        data.append({"text": random.choice(hotel_templates).format(a=a), "intent": "change_hotel"})

    # 7. change_time_window intent
    time_templates = [
        "i am only available from {t1} to {t2}", "plan from {t1} to {t2}",
        "available between {t1} and {t2}", "set daily timing to {t1} to {t2}",
        "start at {t1} and finish by {t2}", "my available hours are {t1} to {t2}",
        "change trip hours to {t1} to {t2}", "start day {d} at {t1}",
        "on day {d} start after {t1}", "end day {d} by {t2}",
        "plan day {d} from {t1} to {t2}", "only available after {t1} on day {d}"
    ]
    sample_t1 = ["9am", "10am", "10:30 am", "11am", "2pm", "09:00", "10:00", "14:00"]
    sample_t2 = ["5pm", "6pm", "7pm", "8pm", "9pm", "10pm", "18:00", "20:00", "22:00"]
    for _ in range(400):
        t1 = random.choice(sample_t1)
        t2 = random.choice(sample_t2)
        d = random.randint(1, 5)
        data.append({"text": random.choice(time_templates).format(t1=t1, t2=t2, d=d), "intent": "change_time_window"})

    # 8. add_poi / replace_poi / general
    for _ in range(250):
        data.append({"text": f"add {random.choice(sample_places)} to day {random.randint(1,5)}", "intent": "add_poi"})
    for _ in range(200):
        data.append({"text": f"replace {random.choice(sample_places)} with a beach", "intent": "replace_poi"})
    for _ in range(150):
        data.append({"text": "hello trip planner what can you do", "intent": "general_query"})

    return pd.DataFrame(data)

def normalize_time_str(t_str):
    """Normalizes natural language time strings (e.g., '10am', '2:30 pm', '16:00') into standard 'HH:MM'."""
    if not t_str:
        return None
    t_clean = str(t_str).strip().lower()
    is_pm = "pm" in t_clean
    is_am = "am" in t_clean
    t_clean = t_clean.replace("am", "").replace("pm", "").strip()
    
    parts = t_clean.split(":")
    try:
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        if is_pm and hours < 12:
            hours += 12
        elif is_am and hours == 12:
            hours = 0
        return f"{max(0, min(23, hours)):02d}:{max(0, min(59, minutes)):02d}"
    except (ValueError, IndexError):
        return None

class CustomNLUReplanner:
    def __init__(self, data_dir=r"d:\drl_project"):
        self.data_dir = data_dir
        self.model = None
        self.vectorizer = None
        self.places = self.load_places()
        self.hotels = self.load_hotels()
        self.model_path = os.path.join(data_dir, "agents", "models", "nlu_intent_classifier.joblib")
        self.train_or_load_model()

    def load_places(self):
        p_path = os.path.join(self.data_dir, "tourist_places", "chennai_places.json")
        if os.path.exists(p_path):
            with open(p_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def load_hotels(self):
        h_path = os.path.join(self.data_dir, "hotels", "chennai_hotels.csv")
        if os.path.exists(h_path):
            return pd.read_csv(h_path).to_dict(orient="records")
        return []

    def train_or_load_model(self):
        # Re-train to guarantee high precision across all intents
        df = generate_robust_nlu_data()
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        X = self.vectorizer.fit_transform(df["text"])
        y = df["intent"]
        
        self.model = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=350, random_state=42)
        self.model.fit(X, y)
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({"vectorizer": self.vectorizer, "model": self.model}, self.model_path)

    def extract_entities(self, text):
        text_clean = text.lower().strip()
        entities = {}
        
        # 0. Available Time Window Extraction (e.g., "from 10am to 6pm", "between 09:00 and 18:00", "start day 1 at 2pm")
        time_range_match = re.search(r"(?:from|between|available\s+at|timing\s+is|timing\s+from|hours\s+are)?\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*(?:to|and|-|until|till)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", text_clean)
        if time_range_match and any(w in text_clean for w in ["from", "to", "between", "available", "timing", "hours", "start", "end", "pm", "am", ":"]):
            st_norm = normalize_time_str(time_range_match.group(1))
            et_norm = normalize_time_str(time_range_match.group(2))
            if st_norm and et_norm:
                entities["start_time"] = st_norm
                entities["end_time"] = et_norm

        if "start_time" not in entities:
            st_match = re.search(r"(?:start\s+(?:at|after|from)|only\s+available\s+after)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", text_clean)
            if st_match:
                st_norm = normalize_time_str(st_match.group(1))
                if st_norm:
                    entities["start_time"] = st_norm

        if "end_time" not in entities:
            et_match = re.search(r"(?:end\s+(?:by|at|before)|finish\s+(?:by|at|before)|wrap\s+up\s+by|until)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", text_clean)
            if et_match:
                et_norm = normalize_time_str(et_match.group(1))
                if et_norm:
                    entities["end_time"] = et_norm

        # 1. Relative Day delta extraction (e.g. "add 1 more day", "add 2 days", "extend by 1 day", "reduce by 1 day")
        add_match = re.search(r"(?:add|extend\s+by|increase\s+by|plus|\+)\s*([1-7])\s*(?:more\s+)?days?", text_clean)
        if not add_match:
            if re.search(r"(?:add|extend)\s+(?:a|another|one)\s+day", text_clean):
                entities["day_delta"] = 1
        else:
            entities["day_delta"] = int(add_match.group(1))

        sub_match = re.search(r"(?:reduce\s+by|shorten\s+by|decrease\s+by|minus|\-)\s*([1-7])\s*(?:more\s+)?days?", text_clean)
        if not sub_match:
            sub_match = re.search(r"(?:remove|cut)\s+([1-7])\s*(?:more\s+)?days?", text_clean)
        if sub_match:
            entities["day_delta"] = -int(sub_match.group(1))

        # 2. Absolute Day Count extraction (e.g. "change to 4 days", "plan it for 4 days", "make it 4 days")
        if "day_delta" not in entities:
            day_count_match = re.search(r"(?:to|for|make\s+it|plan\s+for|set\s+to|a)\s*([1-7])\s*(?:day|days)", text_clean)
            if not day_count_match:
                day_count_match = re.search(r"\b([1-7])\s*days?\b", text_clean)
            if day_count_match:
                entities["num_days"] = int(day_count_match.group(1))

        # 3. Specific Target Day (e.g. "on day 2", "make day 4")
        target_day_match = re.search(r"day\s*([1-7])", text_clean)
        if target_day_match:
            entities["target_day"] = int(target_day_match.group(1))

        # 4. Category extraction
        detected_cats = []
        if "shopping" in text_clean or "mall" in text_clean or "malls" in text_clean or "bazaar" in text_clean:
            detected_cats.append("Shopping & Markets")
        if "beach" in text_clean or "beaches" in text_clean or "coast" in text_clean or "sea" in text_clean:
            detected_cats.append("Beaches & Coastline")
        if "food" in text_clean or "mess" in text_clean or "cafe" in text_clean or "restaurant" in text_clean or "dining" in text_clean:
            detected_cats.append("Food, Messes & Cafes")
        if "heritage" in text_clean or "museum" in text_clean or "history" in text_clean or "fort" in text_clean:
            detected_cats.append("Heritage & History")
        if "temple" in text_clean or "temples" in text_clean or "kovil" in text_clean or "spiritual" in text_clean:
            detected_cats.append("Temples & Spiritual")
        if "park" in text_clean or "nature" in text_clean or "zoo" in text_clean or "lake" in text_clean:
            detected_cats.append("Parks & Nature")
            
        if detected_cats:
            entities["categories"] = detected_cats

        # 5. Pace extraction
        if "relax" in text_clean or "relaxed" in text_clean or "slow" in text_clean or "less hectic" in text_clean:
            entities["pace"] = "Relaxed"
        elif "packed" in text_clean or "fast" in text_clean or "more places" in text_clean or "busy" in text_clean:
            entities["pace"] = "Packed"

        # 6. Transport Mode & Action extraction
        mode_map = {
            "flight": "flight", "flights": "flight", "plane": "flight", "air": "flight", "fly": "flight", "spicejet": "flight", "indigo": "flight",
            "train": "train", "trains": "train", "rail": "train", "railway": "train", "irctc": "train", "vande bharat": "train",
            "bus": "bus", "buses": "bus", "coach": "bus", "volvo": "bus"
        }

        # Check explicit "switch X to Y" or "prefer Y" or "to Y"
        target_to_match = re.search(r"(?:to|prefer|into|use|take|want|only)\s+([a-z\s]+)", text_clean)
        target_mode = None
        if target_to_match:
            cand = target_to_match.group(1).strip()
            for k, v in mode_map.items():
                if re.search(rf"\b{re.escape(k)}\b", cand):
                    target_mode = v
                    break

        # Check explicit "exclude X", "remove X", "avoid X", "no X"
        exclude_match = re.search(r"(?:exclude|remove|avoid|no\s+|without|skip|dont want|don't want|cancel)\s+([a-z\s]+)", text_clean)
        exclude_mode = None
        if exclude_match:
            cand = exclude_match.group(1).strip()
            for k, v in mode_map.items():
                if re.search(rf"\b{re.escape(k)}\b", cand):
                    exclude_mode = v
                    break

        if exclude_mode:
            entities["transport_mode"] = exclude_mode
            entities["transport_action"] = "exclude"
        elif target_mode:
            entities["transport_mode"] = target_mode
            entities["transport_action"] = "prefer"
        else:
            # Fallback scan across all keywords
            for k, v in mode_map.items():
                if re.search(rf"\b{re.escape(k)}\b", text_clean):
                    entities["transport_mode"] = v
                    if any(neg in text_clean for neg in ["exclude", "remove", "avoid", "no ", "without", "skip", "dont want", "don't want", "cancel"]):
                        entities["transport_action"] = "exclude"
                    else:
                        entities["transport_action"] = "prefer"
                    break

        # 7. POI Match (Only if NOT a purely transport or general category command)
        is_transport_cmd = bool(entities.get("transport_mode") and entities.get("transport_action"))
        if not is_transport_cmd:
            best_poi = None
            best_score = 0.0
            
            # Specific known aliases
            if "tirumala" in text_clean or "tirupati" in text_clean:
                for p in self.places:
                    if "ttd" in p["name"].lower() or "venkateswara" in p["name"].lower():
                        best_poi = p
                        best_score = 1.0
                        break

            if not best_poi:
                # Exact full name match
                for p in self.places:
                    p_name = p["name"].lower()
                    if p_name in text_clean:
                        best_poi = p
                        best_score = 1.0
                        break
                        
            if not best_poi:
                stop_poi_words = {
                    "flight", "flights", "train", "trains", "buses", "bus", "hotel", "hotels",
                    "beach", "beaches", "temple", "temples", "museum", "museums", "park", "parks",
                    "mall", "malls", "market", "markets", "bazaar", "street", "road", "chennai",
                    "place", "places", "visit", "trip", "plan", "days", "food", "cafe", "mess",
                    "morning", "evening", "timing", "hours", "available"
                }
                
                for p in self.places:
                    p_name = p["name"].lower()
                    p_tokens = [w for w in re.findall(r'\b[a-z]{4,}\b', p_name) if w not in stop_poi_words]
                    
                    if len(p_tokens) >= 2:
                        phrase = " ".join(p_tokens[:2])
                        if phrase in text_clean:
                            best_poi = p
                            best_score = 0.95
                            break
                            
                    for tok in p_tokens:
                        if len(tok) >= 5 and re.search(rf"\b{re.escape(tok)}\b", text_clean):
                            if tok not in ["south", "north", "central", "nagar", "royal", "grand", "plaza", "lights"]:
                                best_poi = p
                                best_score = 0.85
                                break
                    if best_score >= 0.85:
                        break

            if best_poi:
                entities["matched_poi"] = best_poi

        # 8. Hotel Area & Tier
        for a in ["mylapore", "t nagar", "t. nagar", "guindy", "central", "egmore", "adyar", "besant nagar", "ecr", "omr"]:
            if a in text_clean:
                entities["hotel_area"] = a.title()
                break
        if "budget" in text_clean or "cheap" in text_clean: entities["hotel_tier"] = "Budget"
        elif "luxury" in text_clean or "5 star" in text_clean or "5-star" in text_clean: entities["hotel_tier"] = "Luxury"
        elif "hostel" in text_clean: entities["hotel_tier"] = "Backpacker Hostel"

        return entities

    def process_query(self, user_text, trip_state, graph_builder, itinerary_optimizer, hotel_recommender):
        text_lower = user_text.lower().strip()
        entities = self.extract_entities(user_text)
        
        # 1. Available Time Window commands (e.g. "available from 10am to 6pm", "start day 1 at 2pm")
        if (entities.get("start_time") or entities.get("end_time")) and any(w in text_lower for w in ["available", "timing", "hours", "from", "to", "start", "end", "finish", "pm", "am", "clock", "between"]):
            intent = "change_time_window"

        # 2. Transport commands (Highest priority if transport mode/action detected)
        elif entities.get("transport_mode") and (
            entities.get("transport_action") == "exclude" or
            any(kw in text_lower for kw in ["flight", "flights", "train", "trains", "bus", "buses", "plane"]) and
            any(act in text_lower for act in ["exclude", "remove", "avoid", "no ", "without", "skip", "switch", "change", "only", "prefer", "take", "cheapest", "fastest", "dont want", "don't want"])
        ):
            intent = "change_transport"
            
        # 3. Day modifications (Relative or absolute)
        elif entities.get("day_delta") is not None or (entities.get("num_days") and any(w in text_lower for w in ["plan", "make", "day", "trip", "set", "change", "add", "extend", "reduce", "shorten", "to", "for"])):
            intent = "change_days"
            
        # 4. Pace adjustments
        elif entities.get("pace") and any(w in text_lower for w in ["pace", "make", "day", "schedule", "trip", "slow", "fast", "packed", "relaxed"]):
            intent = "change_pace"
            
        # 5. Strict category changes
        elif ("only" in text_lower or "focus on" in text_lower or "show me" in text_lower or "filter" in text_lower) and entities.get("categories"):
            intent = "change_categories"
            
        # 6. POI Removal
        elif ("dont want" in text_lower or "remove" in text_lower or "skip" in text_lower or "delete" in text_lower or "no " in text_lower) and (entities.get("matched_poi") or entities.get("categories")):
            intent = "remove_poi"
            
        # 7. Hotel updates
        elif any(w in text_lower for w in ["hotel", "stay", "hostel", "resort", "lodge", "room"]) and (entities.get("hotel_area") or entities.get("hotel_tier") or "cheap" in text_lower or "budget" in text_lower or "luxury" in text_lower):
            intent = "change_hotel"
            
        else:
            # Model prediction
            X = self.vectorizer.transform([user_text])
            intent = self.model.predict(X)[0]

        reply = ""
        action_done = ""

        # --- 0. CHANGE TIME WINDOW ---
        if intent == "change_time_window" or entities.get("start_time") or entities.get("end_time"):
            target_day = entities.get("target_day")
            new_st = entities.get("start_time", trip_state.daily_start_time if hasattr(trip_state, "daily_start_time") else "09:00")
            new_et = entities.get("end_time", trip_state.daily_end_time if hasattr(trip_state, "daily_end_time") else "21:00")

            if target_day:
                if not hasattr(trip_state, "day_time_windows"):
                    trip_state.day_time_windows = {}
                trip_state.day_time_windows[target_day] = (new_st, new_et)
                window_desc = f"Day {target_day} available hours updated to **{new_st} ➔ {new_et}**"
            else:
                trip_state.daily_start_time = new_st
                trip_state.daily_end_time = new_et
                window_desc = f"Daily available time window set to **{new_st} ➔ {new_et}** across all days"

            trip_state.daily_itinerary = itinerary_optimizer.plan_itinerary(
                num_days=trip_state.num_days,
                pace=trip_state.pace,
                categories=list(trip_state.preferred_categories) if trip_state.preferred_categories else None,
                excluded_ids=trip_state.forbidden_poi_ids,
                selected_hotel=trip_state.selected_hotel,
                daily_start_time=getattr(trip_state, "daily_start_time", "09:00"),
                daily_end_time=getattr(trip_state, "daily_end_time", "21:00"),
                day_time_windows=getattr(trip_state, "day_time_windows", None)
            )
            action_done = f"Updated available time window: {new_st} - {new_et}"
            reply = f"⏰ **Available Timing Updated!**\n\n{window_desc}.\n\nYour itinerary activities, durations, and transit schedules have been dynamically recalculated strictly within these hours. Head over to the **Day-Wise Itinerary Planner** to review your revised time slots!"

        # --- 1. CHANGE DAYS ---
        elif intent == "change_days" or entities.get("num_days") or entities.get("day_delta") is not None:
            if entities.get("day_delta") is not None:
                new_days = max(1, min(7, trip_state.num_days + entities["day_delta"]))
            else:
                new_days = max(1, min(7, entities.get("num_days", trip_state.num_days)))
                
            trip_state.num_days = new_days
            # Re-plan itinerary dynamically
            trip_state.daily_itinerary = itinerary_optimizer.plan_itinerary(
                num_days=new_days,
                pace=trip_state.pace,
                categories=list(trip_state.preferred_categories) if trip_state.preferred_categories else None,
                excluded_ids=trip_state.forbidden_poi_ids,
                selected_hotel=trip_state.selected_hotel
            )
            action_done = f"Updated trip duration to {new_days} days."
            reply = f"🗓️ **Itinerary Updated to {new_days} Days!**\n\nI have recalculated your entire Chennai sightseeing schedule for **{new_days} days** at a **{trip_state.pace} pace**.\n\nAll days are balanced with hotel check-in/out and CMRL Metro recommendations. Check the **Local Sightseeing Itinerary** tab to see your new schedule!"

        # --- 2. CHANGE CATEGORIES / FOCUS ---
        elif intent == "change_categories" or ("only" in text_lower and entities.get("categories")):
            new_cats = entities.get("categories", ["Shopping & Markets", "Beaches & Coastline"])
            trip_state.preferred_categories = set(new_cats)
            trip_state.daily_itinerary = itinerary_optimizer.plan_itinerary(
                num_days=trip_state.num_days,
                pace=trip_state.pace,
                categories=new_cats,
                excluded_ids=trip_state.forbidden_poi_ids,
                selected_hotel=trip_state.selected_hotel
            )
            cat_names = ", ".join(new_cats)
            action_done = f"Filtered itinerary strictly to: {cat_names}."
            reply = f"🎯 **Category Focus Updated!**\n\nI have regenerated your itinerary strictly focusing on **{cat_names}**.\n\nUnselected categories (like temples or heritage) have been completely removed, replacing them with major shopping malls (Phoenix, Express Avenue, VR Chennai), traditional bazaars (Pondy Bazaar, Sowcarpet), and sunset beaches (Marina, Besant Nagar)!"

        # --- 3. REMOVE POI / CATEGORY ---
        elif intent == "remove_poi":
            target_poi = entities.get("matched_poi")
            cats = entities.get("categories")
            
            if target_poi:
                poi_id = target_poi["id"]
                poi_name = target_poi["name"]
                trip_state.forbidden_poi_ids.add(poi_id)
                
                # Regenerate itinerary without forbidden POIs
                trip_state.daily_itinerary = itinerary_optimizer.plan_itinerary(
                    num_days=trip_state.num_days,
                    pace=trip_state.pace,
                    categories=list(trip_state.preferred_categories) if trip_state.preferred_categories else None,
                    excluded_ids=trip_state.forbidden_poi_ids,
                    selected_hotel=trip_state.selected_hotel
                )
                action_done = f"Removed {poi_name} from trip."
                reply = f"✅ **Removed {poi_name}!**\n\nI have taken **{poi_name}** out of your schedule and re-balanced your daily route with an alternate spot. The rest of your itinerary and hotel stays remain preserved!"
            elif cats:
                cat_to_remove = cats[0]
                trip_state.excluded_categories.add(cat_to_remove)
                trip_state.daily_itinerary = itinerary_optimizer.plan_itinerary(
                    num_days=trip_state.num_days,
                    pace=trip_state.pace,
                    categories=[c for c in (trip_state.preferred_categories or []) if c != cat_to_remove] or None,
                    excluded_ids=trip_state.forbidden_poi_ids,
                    selected_hotel=trip_state.selected_hotel
                )
                action_done = f"Excluded {cat_to_remove} from itinerary."
                reply = f"🚫 **Excluded '{cat_to_remove}' across all days.** I've refreshed your schedule to focus on your remaining preferred spots."
            else:
                reply = "I noticed you'd like to remove a place or category. Could you specify which place or type of attraction you'd like to exclude?"

        # --- 3.5. REPLACE POI / SWAP CATEGORY ---
        elif intent == "replace_poi" or "replace" in text_lower or "swap" in text_lower:
            target_day = entities.get("target_day")
            cats = entities.get("categories", [])
            matched = entities.get("matched_poi")
            
            target_cat = None
            if cats:
                # Find target category (usually the last mentioned, e.g. "with a beach")
                target_cat = cats[0] if len(cats) == 1 else cats[-1]
            
            # Rebalance itinerary with focus
            if target_cat:
                if trip_state.preferred_categories:
                    trip_state.preferred_categories.add(target_cat)
                else:
                    trip_state.preferred_categories = {target_cat}
                    
            trip_state.daily_itinerary = itinerary_optimizer.plan_itinerary(
                num_days=trip_state.num_days,
                pace=trip_state.pace,
                categories=list(trip_state.preferred_categories) if trip_state.preferred_categories else None,
                excluded_ids=trip_state.forbidden_poi_ids,
                selected_hotel=trip_state.selected_hotel
            )
            
            cat_label = target_cat if target_cat else (matched["name"] if matched else "new attraction")
            day_label = f" on Day {target_day}" if target_day else ""
            action_done = f"Replaced activity{day_label} with {cat_label}."
            reply = f"🔄 **Activity Replaced{day_label}!**\n\nI have updated your schedule to swap in **{cat_label}** and optimized the geographic travel times accordingly. Check the **Local Sightseeing Itinerary** tab to view your updated route!"

        # --- 4. CHANGE PACE ---
        elif intent == "change_pace":
            new_pace = entities.get("pace", "Relaxed")
            target_day = entities.get("target_day")
            trip_state.pace = new_pace
            trip_state.daily_itinerary = itinerary_optimizer.plan_itinerary(
                num_days=trip_state.num_days,
                pace=new_pace,
                categories=list(trip_state.preferred_categories) if trip_state.preferred_categories else None,
                excluded_ids=trip_state.forbidden_poi_ids,
                selected_hotel=trip_state.selected_hotel
            )
            action_done = f"Adjusted pace to {new_pace}."
            reply = f"⏳ **Trip Pace Adjusted to {new_pace}!**\n\n{'For Day ' + str(target_day) + ' and all other days, ' if target_day else ''}I have relaxed your daily schedule with fewer stops and extended time windows at each attraction."

        # --- 5. CHANGE TRANSPORT ---
        elif intent == "change_transport":
            mode = entities.get("transport_mode", "train")
            action_type = entities.get("transport_action", "prefer")
            routes = graph_builder.get_multihop_routes(trip_state.origin_city, "Chennai")
            
            # Check exclude / avoid / remove
            if action_type == "exclude" or any(neg in text_lower for neg in ["exclude", "remove", "avoid", "no ", "without", "skip", "dont want", "don't want"]):
                routes = [r for r in routes if mode not in r["primary_mode"].lower()]
                action_text = f"Excluded {mode}s from journey"
            else:
                routes = [r for r in routes if mode in r["primary_mode"].lower()]
                action_text = f"Switched transport to {mode}"
                
            if routes:
                routes.sort(key=lambda r: (r["total_duration_hours"], r["total_fare_inr"]))
                trip_state.selected_route = routes[0]
                action_done = f"{action_text} (Selected: {trip_state.selected_route['primary_mode']})."
                reply = f"🚆 **Updated Journey Plan:** {trip_state.selected_route['primary_mode']} ({trip_state.selected_route['type']})\n- **Duration:** {trip_state.selected_route['total_duration_hours']} hrs | **Fare:** ₹{trip_state.selected_route['total_fare_inr']:,}\n- **Operator:** {trip_state.selected_route['legs'][0].get('operator')} {trip_state.selected_route['legs'][0].get('number')}\n- **Connecting via:** {trip_state.selected_route['legs'][0].get('to_city') if trip_state.selected_route['type'] == 'Connecting' else 'Direct'}"
            else:
                reply = f"No alternative routes found when filtering for {mode} from {trip_state.origin_city} to Chennai."

        # --- 6. CHANGE HOTEL ---
        elif intent == "change_hotel":
            area = entities.get("hotel_area")
            tier = entities.get("hotel_tier")
            recs = hotel_recommender.get_recommendations(max_price=trip_state.budget_per_day, preferred_zone=area, category=tier)
            if recs:
                trip_state.selected_hotel = recs[0]
                trip_state.daily_itinerary = itinerary_optimizer.plan_itinerary(
                    num_days=trip_state.num_days,
                    pace=trip_state.pace,
                    selected_hotel=trip_state.selected_hotel
                )
                action_done = f"Changed hotel to {trip_state.selected_hotel['hotel_name']}."
                reply = f"🏨 **Hotel Updated!**\n- **Property:** {trip_state.selected_hotel['hotel_name']}\n- **Location:** {trip_state.selected_hotel['area']} ({trip_state.selected_hotel['zone']})\n- **Price:** ₹{trip_state.selected_hotel['price_per_night_inr']:,}/night\n- **Check-In/Out:** 🕒 {trip_state.selected_hotel.get('check_in_time', '12:00')} / {trip_state.selected_hotel.get('check_out_time', '11:00')}\n\nHotel check-in and check-out milestones have been updated in your daily itinerary!"
            else:
                reply = "No matching hotels found for those criteria in our database."

        # --- 7. GENERAL / FALLBACK ---
        else:
            reply = "🤖 **I'm your Chennai Trip Assistant!** You can modify any part of your plan dynamically. Try saying:\n- *'Plan it for 4 days'*\n- *'Show only shopping and beaches'*\n- *'Make Day 4 more relaxed'*\n- *'I dont want to visit tirumala temple'*\n- *'Switch to train only'*\n- *'Find a budget hotel near Mylapore'*"

        return {
            "intent": intent,
            "entities": entities,
            "reply": reply,
            "action_done": action_done,
            "trip_state": trip_state
        }
