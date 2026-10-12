"""
Custom Gymnasium Environment for Multi-Modal Route Planning (India to Chennai).
DRL agent learns to navigate the multi-modal transport graph (flights, trains, buses)
to reach Chennai while balancing travel time, total fare, and transfer fatigue.
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import math
import os
import sys

# Add project root to path
sys.path.append(r"d:\drl_project")
from engine.graph_builder import MultiModalGraphBuilder

class MultiModalRouteEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, data_dir=r"d:\drl_project", target_city="Chennai", max_steps=5):
        super(MultiModalRouteEnv, self).__init__()
        self.data_dir = data_dir
        self.target_city = target_city
        self.max_steps = max_steps
        
        self.builder = MultiModalGraphBuilder(data_dir=data_dir)
        self.cities = list(self.builder.graph.nodes())
        self.city_to_idx = {city: i for i, city in enumerate(self.cities)}
        self.idx_to_city = {i: city for i, city in enumerate(self.cities)}
        self.target_idx = self.city_to_idx.get(target_city, 0)
        
        # Modes: 0: start/none, 1: flight, 2: train, 3: bus
        self.mode_map = {"none": 0, "flight": 1, "train": 2, "bus": 3}
        self.idx_to_mode = {v: k for k, v in self.mode_map.items()}
        
        # Max candidate connections per step
        self.max_actions = 15
        
        # Action space: Discrete choice among available outbound edges at current city
        self.action_space = spaces.Discrete(self.max_actions)
        
        # Observation space:
        # [current_city_idx/N, mode_idx/3, elapsed_hours/48.0, cost/25000.0, transfers/5.0, dist_to_target/3000.0, step_num/max_steps]
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(7,), dtype=np.float32
        )
        
        self.reset()

    def _get_haversine_dist(self, city1, city2):
        n1 = self.builder.graph.nodes.get(city1, {})
        n2 = self.builder.graph.nodes.get(city2, {})
        lat1, lon1 = n1.get("lat", 13.08), n1.get("lon", 80.27)
        lat2, lon2 = n2.get("lat", 13.08), n2.get("lon", 80.27)
        
        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _get_available_edges(self, city):
        """Returns sorted list of candidate outgoing edges."""
        if not self.builder.graph.has_node(city):
            return []
        
        edges = []
        out_edges = self.builder.graph.out_edges(city, keys=True, data=True)
        for u, v, k, d in out_edges:
            edges.append({
                "to_city": v,
                "mode": d.get("mode", "train"),
                "duration_hours": d.get("duration_hours", 5.0),
                "fare_inr": d.get("fare_inr", 1000.0),
                "operator": d.get("operator", ""),
                "number": d.get("number", "")
            })
            
        # Sort so that target city or major hubs come first
        def sort_key(e):
            is_dest = 0 if e["to_city"] == self.target_city else 1
            dist = self._get_haversine_dist(e["to_city"], self.target_city)
            return (is_dest, dist, e["fare_inr"])
            
        edges.sort(key=sort_key)
        return edges[:self.max_actions]

    def _get_obs(self):
        city_norm = float(self.current_city_idx) / max(1, len(self.cities) - 1)
        mode_norm = float(self.current_mode_idx) / 3.0
        time_norm = min(1.0, self.elapsed_hours / 48.0)
        cost_norm = min(1.0, self.total_cost / 25000.0)
        trans_norm = min(1.0, self.num_transfers / 5.0)
        
        curr_city = self.idx_to_city[self.current_city_idx]
        dist = self._get_haversine_dist(curr_city, self.target_city)
        dist_norm = min(1.0, dist / 3000.0)
        step_norm = float(self.current_step) / self.max_steps
        
        return np.array([city_norm, mode_norm, time_norm, cost_norm, trans_norm, dist_norm, step_norm], dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Pick random origin city other than Chennai
        non_target = [c for c in self.cities if c != self.target_city]
        if non_target:
            self.origin_city = np.random.choice(non_target)
        else:
            self.origin_city = "Bangalore"
            
        self.current_city = self.origin_city
        self.current_city_idx = self.city_to_idx[self.current_city]
        self.current_mode_idx = 0
        self.elapsed_hours = 0.0
        self.total_cost = 0.0
        self.num_transfers = 0
        self.current_step = 0
        self.journey_path = [self.current_city]
        self.journey_legs = []
        
        return self._get_obs(), {}

    def step(self, action):
        self.current_step += 1
        available = self._get_available_edges(self.current_city)
        
        # Penalty for invalid action index
        if action >= len(available):
            reward = -20.0
            terminated = (self.current_step >= self.max_steps)
            truncated = False
            return self._get_obs(), reward, terminated, truncated, {"error": "invalid_action"}

        edge = available[action]
        next_city = edge["to_city"]
        mode = edge["mode"]
        dur = edge["duration_hours"]
        fare = edge["fare_inr"]
        
        # Layover time if transfer
        layover = 1.5 if self.num_transfers > 0 else 0.0
        
        old_dist = self._get_haversine_dist(self.current_city, self.target_city)
        new_dist = self._get_haversine_dist(next_city, self.target_city)
        
        # Update State
        self.current_city = next_city
        self.current_city_idx = self.city_to_idx[next_city]
        self.current_mode_idx = self.mode_map.get(mode, 1)
        self.elapsed_hours += (dur + layover)
        self.total_cost += fare
        if self.current_step > 1:
            self.num_transfers += 1
            
        self.journey_path.append(next_city)
        self.journey_legs.append(edge)
        
        # Reward Engineering:
        # Distance reduction bonus + time cost + fare cost + transfer penalty
        dist_progress = (old_dist - new_dist) / 100.0 # positive if moved closer
        time_penalty = dur * 0.5
        cost_penalty = (fare / 1000.0) * 0.8
        transfer_penalty = 2.0 if self.num_transfers > 1 else 0.0
        
        reward = dist_progress - time_penalty - cost_penalty - transfer_penalty
        
        terminated = False
        if self.current_city == self.target_city:
            # Huge terminal success bonus scaled by efficiency
            efficiency_bonus = max(0, 100.0 - (self.elapsed_hours * 1.5) - (self.total_cost / 500.0))
            reward += 150.0 + efficiency_bonus
            terminated = True
        elif self.current_step >= self.max_steps:
            # Failed to reach target in max steps
            reward -= 50.0
            terminated = True
            
        truncated = False
        return self._get_obs(), float(reward), terminated, truncated, {
            "current_city": self.current_city,
            "elapsed_hours": self.elapsed_hours,
            "total_cost": self.total_cost,
            "path": self.journey_path
        }

if __name__ == "__main__":
    env = MultiModalRouteEnv()
    obs, _ = env.reset()
    print("Initial obs:", obs, "Origin:", env.origin_city)
    for _ in range(3):
        a = env.action_space.sample()
        obs, r, term, trunc, info = env.step(a)
        print(f"Action: {a} -> Reward: {r:.2f}, Terminated: {term}, City: {info.get('current_city')}")
        if term:
            break
