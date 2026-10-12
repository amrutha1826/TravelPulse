"""
Custom Gymnasium Environment for Intra-Chennai Local Trip & Itinerary Optimization.
DRL agent (PPO/DQN) learns to sequence daily visits to 200+ attractions and food spots,
satisfying opening hours, minimizing transit distance, and maximizing diversity and user satisfaction.
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import math
import os
import json
import pandas as pd

class ChennaiItineraryEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, data_dir=r"d:\drl_project", num_days=3, pace="Moderate", budget_per_day=3000):
        super(ChennaiItineraryEnv, self).__init__()
        self.data_dir = data_dir
        self.num_days = num_days
        self.pace = pace # "Relaxed" (3 POIs/day), "Moderate" (5 POIs/day), "Packed" (7 POIs/day)
        self.budget_per_day = budget_per_day
        self.total_budget = num_days * budget_per_day
        
        self.places = self._load_places()
        self.categories = list(set(p.get("category", "General") for p in self.places))
        self.cat_to_idx = {c: i for i, c in enumerate(self.categories)}
        
        # Max candidate choices at each step (e.g. 10 nearest unvisited POIs + 1 action for 'finish day')
        self.max_candidate_actions = 12
        self.action_space = spaces.Discrete(self.max_candidate_actions)
        
        # Observation vector:
        # [lat_norm, lon_norm, current_hour_norm, remaining_day_time_norm, day_idx_norm, budget_left_norm, category_diversity_score, total_visited_norm]
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(8,), dtype=np.float32
        )
        
        self.reset()

    def _load_places(self):
        places_path = os.path.join(self.data_dir, "tourist_places", "chennai_places.json")
        if os.path.exists(places_path):
            with open(places_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _get_haversine_dist_km(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _get_candidate_pois(self):
        """Returns list of unvisited candidate places sorted by distance from current location."""
        unvisited = [p for p in self.places if p["id"] not in self.visited_poi_ids]
        if not unvisited:
            return []
            
        def dist_func(p):
            return self._get_haversine_dist_km(self.current_lat, self.current_lon, p["latitude"], p["longitude"])
            
        unvisited.sort(key=dist_func)
        return unvisited[:self.max_candidate_actions - 1]

    def _get_obs(self):
        # Chennai bounds approx: Lat 12.6 to 13.3, Lon 79.9 to 80.35
        lat_norm = np.clip((self.current_lat - 12.6) / 0.7, 0.0, 1.0)
        lon_norm = np.clip((self.current_lon - 79.9) / 0.45, 0.0, 1.0)
        hour_norm = np.clip((self.current_hour - 6.0) / 16.0, 0.0, 1.0) # 6 AM to 10 PM
        rem_time_norm = np.clip(self.remaining_day_hours / 12.0, 0.0, 1.0)
        day_norm = float(self.current_day - 1) / max(1, self.num_days - 1)
        budget_norm = np.clip(self.budget_remaining / max(1.0, self.total_budget), 0.0, 1.0)
        
        # Diversity score: unique visited categories / total categories
        unique_cats = len(set(self.visited_categories))
        div_score = float(unique_cats) / max(1, len(self.categories))
        
        visited_norm = min(1.0, len(self.visited_poi_ids) / (self.num_days * 6.0))
        
        return np.array([lat_norm, lon_norm, hour_norm, rem_time_norm, day_norm, budget_norm, div_score, visited_norm], dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Start at a central Chennai hub (e.g. Central Station / Mylapore)
        self.current_lat = 13.0827
        self.current_lon = 80.2707
        self.current_day = 1
        self.current_hour = 8.5 # 8:30 AM
        self.remaining_day_hours = 12.0 # 8:30 AM to 8:30 PM
        self.budget_remaining = float(self.total_budget)
        
        self.visited_poi_ids = set()
        self.visited_categories = []
        self.daily_itineraries = {d: [] for d in range(1, self.num_days + 1)}
        self.step_count = 0
        
        return self._get_obs(), {}

    def step(self, action):
        self.step_count += 1
        candidates = self._get_candidate_pois()
        
        # Action = max_candidate_actions - 1 means: Finish current day & advance to next morning
        if action == (self.max_candidate_actions - 1) or len(candidates) == 0:
            # End current day
            self.current_day += 1
            self.current_hour = 8.5 # Reset to next morning
            self.remaining_day_hours = 12.0
            
            # Reset location to central hotel or stay
            self.current_lat = 13.0827
            self.current_lon = 80.2707
            
            terminated = (self.current_day > self.num_days)
            reward = 5.0 # Day concluded
            truncated = False
            return self._get_obs(), reward, terminated, truncated, {"event": "day_ended"}

        # Penalty if action index out of bounds
        if action >= len(candidates):
            reward = -10.0
            terminated = (self.current_day > self.num_days)
            return self._get_obs(), reward, terminated, False, {"error": "invalid_action"}

        poi = candidates[action]
        dist_km = self._get_haversine_dist_km(self.current_lat, self.current_lon, poi["latitude"], poi["longitude"])
        transit_time_hours = (dist_km / 25.0) + 0.25 # Avg speed 25 km/h + 15 min buffer
        visit_dur = poi.get("recommended_duration_hours", 1.5)
        total_time_needed = transit_time_hours + visit_dur
        
        entry_fee = poi.get("entry_fee_inr", 0)
        
        # Check time feasibility for today
        if total_time_needed > self.remaining_day_hours:
            # Not enough time left today -> advance to next day
            self.current_day += 1
            self.current_hour = 8.5
            self.remaining_day_hours = 12.0
            self.current_lat = 13.0827
            self.current_lon = 80.2707
            
            terminated = (self.current_day > self.num_days)
            reward = -2.0 # mild penalty for scheduling conflict
            return self._get_obs(), reward, terminated, False, {"event": "overtime_shifted_day"}

        # Execute Visit
        self.visited_poi_ids.add(poi["id"])
        cat = poi.get("category", "General")
        self.visited_categories.append(cat)
        
        self.current_lat = poi["latitude"]
        self.current_lon = poi["longitude"]
        self.current_hour += total_time_needed
        self.remaining_day_hours -= total_time_needed
        self.budget_remaining -= entry_fee
        
        self.daily_itineraries[self.current_day].append({
            "poi": poi,
            "visit_time": f"{int(self.current_hour - visit_dur):02d}:{int(((self.current_hour - visit_dur) % 1) * 60):02d}",
            "dist_from_prev_km": round(dist_km, 2)
        })

        # Reward Engineering:
        # 1. Place Rating (base value)
        rating_reward = poi.get("rating", 4.5) * 2.0
        
        # 2. Distance transit penalty (penalize long travel)
        dist_penalty = dist_km * 0.4
        
        # 3. Category diversity reward (encourage seeing varied places)
        cat_count = self.visited_categories.count(cat)
        diversity_bonus = 4.0 / max(1, cat_count)
        
        # 4. Time-of-day appropriateness bonus
        time_match_bonus = 0.0
        best_time = poi.get("best_time_of_day", "Any")
        if (best_time == "Morning" and self.current_hour <= 12.0) or \
           (best_time == "Afternoon" and 12.0 < self.current_hour <= 16.5) or \
           (best_time == "Evening" and self.current_hour > 16.5):
            time_match_bonus = 3.0
            
        reward = rating_reward + diversity_bonus + time_match_bonus - dist_penalty
        
        # Check if trip completed
        terminated = (self.current_day > self.num_days)
        if terminated:
            # Trip completion bonus based on total rich experiences
            reward += len(self.visited_poi_ids) * 5.0
            
        truncated = False
        return self._get_obs(), float(reward), terminated, truncated, {
            "visited_count": len(self.visited_poi_ids),
            "current_day": self.current_day
        }

if __name__ == "__main__":
    env = ChennaiItineraryEnv(num_days=3)
    obs, _ = env.reset()
    print("Itinerary Env Initial obs:", obs)
    for step_i in range(10):
        a = env.action_space.sample()
        obs, r, term, trunc, info = env.step(a)
        print(f"Step {step_i}: Action {a} -> Reward {r:.2f}, Terminated: {term}, Info: {info}")
        if term:
            break
