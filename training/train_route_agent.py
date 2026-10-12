"""
Training Pipeline for Multi-Modal Route Planning DQN Agent using Stable-Baselines3.
Trains Double-DQN agent to find optimal transport paths to Chennai.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import BaseCallback

# Add project root to sys path
sys.path.append(r"d:\drl_project")
from environments.multi_modal_route_env import MultiModalRouteEnv

class RewardLoggingCallback(BaseCallback):
    def __init__(self, check_freq=1000, verbose=1):
        super(RewardLoggingCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.episode_rewards = []
        self.episode_lengths = []
        self.current_reward = 0.0
        self.current_len = 0

    def _on_step(self) -> bool:
        reward = self.locals["rewards"][0]
        done = self.locals["dones"][0]
        
        self.current_reward += reward
        self.current_len += 1
        
        if done:
            self.episode_rewards.append(self.current_reward)
            self.episode_lengths.append(self.current_len)
            self.current_reward = 0.0
            self.current_len = 0
            
        return True

def train_route_dqn(total_timesteps=40000):
    print("=== Starting Multi-Modal Route Planning DQN Training ===")
    env = MultiModalRouteEnv()
    
    callback = RewardLoggingCallback()
    
    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=1e-3,
        buffer_size=50000,
        learning_starts=1000,
        batch_size=64,
        tau=1.0,
        gamma=0.99,
        train_freq=4,
        gradient_steps=1,
        target_update_interval=500,
        exploration_fraction=0.3,
        exploration_initial_eps=1.0,
        exploration_final_eps=0.05,
        verbose=0
    )
    
    model.learn(total_timesteps=total_timesteps, callback=callback)
    
    # Save Model
    save_dir = r"d:\drl_project\agents\models"
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, "route_dqn_best.zip")
    model.save(model_path)
    print(f"Model saved successfully to {model_path}")
    
    # Plot Training Curve
    plots_dir = r"d:\drl_project\training\plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    if len(callback.episode_rewards) > 10:
        plt.figure(figsize=(10, 5))
        # Compute moving average
        window = 20
        rewards = callback.episode_rewards
        smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
        
        plt.plot(rewards, alpha=0.3, color='blue', label='Episode Reward')
        plt.plot(range(window-1, len(rewards)), smoothed, color='darkblue', linewidth=2, label=f'Moving Avg ({window} eps)')
        plt.title('Multi-Modal Route Planning DQN Training Reward Curve')
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        
        plot_path = os.path.join(plots_dir, "route_training_curve.png")
        plt.savefig(plot_path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"Training plot saved to {plot_path}")

    return model

if __name__ == "__main__":
    train_route_dqn(total_timesteps=30000)
