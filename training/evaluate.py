"""
Evaluation and Baseline Benchmarking for DRL Models.
Compares DRL Route Agent & DRL Itinerary Agent against Greedy Heuristics and Random Baselines.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from stable_baselines3 import DQN, PPO

# Add root
sys.path.append(r"d:\drl_project")
from environments.multi_modal_route_env import MultiModalRouteEnv
from environments.chennai_itinerary_env import ChennaiItineraryEnv

def evaluate_route_planners(num_episodes=50):
    print("\n--- Evaluating Multi-Modal Route Planners ---")
    env = MultiModalRouteEnv()
    
    # Load trained DQN if exists
    model_path = r"d:\drl_project\agents\models\route_dqn_best.zip"
    dqn_model = DQN.load(model_path) if os.path.exists(model_path) else None
    
    results = {"DRL (DQN)": [], "Greedy (Fastest)": [], "Greedy (Cheapest)": [], "Random": []}
    
    for ep in range(num_episodes):
        # 1. DRL Agent
        obs, _ = env.reset(seed=ep)
        origin = env.origin_city
        tot_r, done = 0.0, False
        while not done:
            if dqn_model:
                action, _ = dqn_model.predict(obs, deterministic=True)
            else:
                action = 0
            obs, r, term, trunc, info = env.step(int(action))
            tot_r += r
            done = term or trunc
        results["DRL (DQN)"].append({
            "reached": env.current_city == "Chennai",
            "reward": tot_r,
            "duration": env.elapsed_hours,
            "cost": env.total_cost,
            "transfers": env.num_transfers
        })
        
        # 2. Greedy Fastest
        env.reset(seed=ep)
        env.origin_city = origin
        env.current_city = origin
        env.current_city_idx = env.city_to_idx[origin]
        tot_r, done = 0.0, False
        while not done:
            avail = env._get_available_edges(env.current_city)
            if not avail:
                break
            # Pick min duration
            best_a = min(range(len(avail)), key=lambda i: avail[i]["duration_hours"])
            obs, r, term, trunc, info = env.step(best_a)
            tot_r += r
            done = term or trunc
        results["Greedy (Fastest)"].append({
            "reached": env.current_city == "Chennai",
            "reward": tot_r,
            "duration": env.elapsed_hours,
            "cost": env.total_cost,
            "transfers": env.num_transfers
        })
        
        # 3. Greedy Cheapest
        env.reset(seed=ep)
        env.origin_city = origin
        env.current_city = origin
        env.current_city_idx = env.city_to_idx[origin]
        tot_r, done = 0.0, False
        while not done:
            avail = env._get_available_edges(env.current_city)
            if not avail:
                break
            best_a = min(range(len(avail)), key=lambda i: avail[i]["fare_inr"])
            obs, r, term, trunc, info = env.step(best_a)
            tot_r += r
            done = term or trunc
        results["Greedy (Cheapest)"].append({
            "reached": env.current_city == "Chennai",
            "reward": tot_r,
            "duration": env.elapsed_hours,
            "cost": env.total_cost,
            "transfers": env.num_transfers
        })
        
        # 4. Random
        env.reset(seed=ep)
        env.origin_city = origin
        env.current_city = origin
        env.current_city_idx = env.city_to_idx[origin]
        tot_r, done = 0.0, False
        while not done:
            a = env.action_space.sample()
            obs, r, term, trunc, info = env.step(a)
            tot_r += r
            done = term or trunc
        results["Random"].append({
            "reached": env.current_city == "Chennai",
            "reward": tot_r,
            "duration": env.elapsed_hours,
            "cost": env.total_cost,
            "transfers": env.num_transfers
        })

    summary = []
    for model_name, ep_list in results.items():
        succ_rate = np.mean([1.0 if x["reached"] else 0.0 for x in ep_list]) * 100.0
        avg_rew = np.mean([x["reward"] for x in ep_list])
        avg_dur = np.mean([x["duration"] for x in ep_list if x["reached"]] or [0])
        avg_cost = np.mean([x["cost"] for x in ep_list if x["reached"]] or [0])
        summary.append({
            "Algorithm": model_name,
            "Success Rate (%)": round(succ_rate, 1),
            "Avg Reward": round(avg_rew, 2),
            "Avg Travel Hours": round(avg_dur, 2),
            "Avg Fare (INR)": round(avg_cost, 2)
        })
        
    df_summary = pd.DataFrame(summary)
    print(df_summary.to_string(index=False))
    return df_summary

def evaluate_itinerary_optimizers(num_episodes=30):
    print("\n--- Evaluating Intra-Chennai Itinerary Optimizers ---")
    env = ChennaiItineraryEnv(num_days=3)
    
    model_path = r"d:\drl_project\agents\models\itinerary_ppo_best.zip"
    ppo_model = PPO.load(model_path) if os.path.exists(model_path) else None
    
    results = {"DRL (PPO)": [], "Greedy (Nearest-Neighbor)": [], "Random": []}
    
    for ep in range(num_episodes):
        # 1. DRL (PPO)
        obs, _ = env.reset(seed=ep)
        tot_r, done = 0.0, False
        while not done:
            if ppo_model:
                action, _ = ppo_model.predict(obs, deterministic=True)
            else:
                action = 0
            obs, r, term, trunc, info = env.step(int(action))
            tot_r += r
            done = term or trunc
        results["DRL (PPO)"].append({
            "reward": tot_r,
            "places_visited": len(env.visited_poi_ids),
            "unique_cats": len(set(env.visited_categories))
        })
        
        # 2. Greedy Nearest Neighbor
        obs, _ = env.reset(seed=ep)
        tot_r, done = 0.0, False
        while not done:
            action = 0 # Nearest candidate
            obs, r, term, trunc, info = env.step(action)
            tot_r += r
            done = term or trunc
        results["Greedy (Nearest-Neighbor)"].append({
            "reward": tot_r,
            "places_visited": len(env.visited_poi_ids),
            "unique_cats": len(set(env.visited_categories))
        })
        
        # 3. Random
        obs, _ = env.reset(seed=ep)
        tot_r, done = 0.0, False
        while not done:
            action = env.action_space.sample()
            obs, r, term, trunc, info = env.step(action)
            tot_r += r
            done = term or trunc
        results["Random"].append({
            "reward": tot_r,
            "places_visited": len(env.visited_poi_ids),
            "unique_cats": len(set(env.visited_categories))
        })
        
    summary = []
    for model_name, ep_list in results.items():
        avg_rew = np.mean([x["reward"] for x in ep_list])
        avg_vis = np.mean([x["places_visited"] for x in ep_list])
        avg_cat = np.mean([x["unique_cats"] for x in ep_list])
        summary.append({
            "Algorithm": model_name,
            "Avg Reward Score": round(avg_rew, 2),
            "Avg Places Visited": round(avg_vis, 1),
            "Unique Categories Visited": round(avg_cat, 1)
        })
        
    df_summary = pd.DataFrame(summary)
    print(df_summary.to_string(index=False))
    return df_summary

def plot_comparison(route_df, itin_df):
    plots_dir = r"d:\drl_project\training\plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Route comparison
    colors1 = ['#2b5c8f', '#4682b4', '#87ceeb', '#d3d3d3']
    ax1.bar(route_df["Algorithm"], route_df["Avg Reward"], color=colors1, edgecolor='black', alpha=0.85)
    ax1.set_title("Multi-Modal Route Planner - Avg Reward Comparison")
    ax1.set_ylabel("Composite Reward Score")
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate(route_df["Avg Reward"]):
        ax1.text(i, v + 2, f"{v}", ha='center', fontweight='bold')
        
    # Itinerary comparison
    colors2 = ['#2e8b57', '#3cb371', '#d3d3d3']
    ax2.bar(itin_df["Algorithm"], itin_df["Avg Reward Score"], color=colors2, edgecolor='black', alpha=0.85)
    ax2.set_title("Intra-Chennai Itinerary Optimizer - Avg Reward Comparison")
    ax2.set_ylabel("Total Satisfaction Reward")
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate(itin_df["Avg Reward Score"]):
        ax2.text(i, v + 2, f"{v}", ha='center', fontweight='bold')
        
    plt.tight_layout()
    plot_path = os.path.join(plots_dir, "baseline_comparison.png")
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"Comparison chart saved to {plot_path}")

if __name__ == "__main__":
    route_res = evaluate_route_planners(num_episodes=30)
    itin_res = evaluate_itinerary_optimizers(num_episodes=30)
    plot_comparison(route_res, itin_res)
