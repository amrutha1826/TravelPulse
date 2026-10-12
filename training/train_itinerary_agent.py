"""
Training Pipeline for Intra-Chennai Local Trip Optimizer using PPO (Proximal Policy Optimization).
Trains PPO agent to sequence multi-day Chennai visits optimizing time, diversity, and satisfaction.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback

# Add project root
sys.path.append(r"d:\drl_project")
from environments.chennai_itinerary_env import ChennaiItineraryEnv

class ItineraryLoggingCallback(BaseCallback):
    def __init__(self, verbose=1):
        super(ItineraryLoggingCallback, self).__init__(verbose)
        self.episode_rewards = []
        self.episode_visited_counts = []
        self.current_reward = 0.0

    def _on_step(self) -> bool:
        reward = self.locals["rewards"][0]
        done = self.locals["dones"][0]
        info = self.locals["infos"][0]
        
        self.current_reward += reward
        
        if done:
            self.episode_rewards.append(self.current_reward)
            self.episode_visited_counts.append(info.get("visited_count", 0))
            self.current_reward = 0.0
            
        return True

def train_itinerary_ppo(total_timesteps=40000):
    print("=== Starting Intra-Chennai Itinerary PPO Training ===")
    env = ChennaiItineraryEnv(num_days=3)
    
    callback = ItineraryLoggingCallback()
    
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        verbose=0
    )
    
    model.learn(total_timesteps=total_timesteps, callback=callback)
    
    # Save Model
    save_dir = r"d:\drl_project\agents\models"
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, "itinerary_ppo_best.zip")
    model.save(model_path)
    print(f"Itinerary model saved to {model_path}")
    
    # Plot Training Curve
    plots_dir = r"d:\drl_project\training\plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    if len(callback.episode_rewards) > 10:
        plt.figure(figsize=(10, 5))
        window = 20
        rewards = callback.episode_rewards
        smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
        
        plt.plot(rewards, alpha=0.3, color='forestgreen', label='Episode Reward')
        plt.plot(range(window-1, len(rewards)), smoothed, color='darkgreen', linewidth=2, label=f'Moving Avg ({window} eps)')
        plt.title('Intra-Chennai Itinerary PPO Policy Training Reward')
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        
        plot_path = os.path.join(plots_dir, "itinerary_training_curve.png")
        plt.savefig(plot_path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"Training plot saved to {plot_path}")

    return model

if __name__ == "__main__":
    train_itinerary_ppo(total_timesteps=30000)
