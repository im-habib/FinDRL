# 5. RLTradingAgent (DQN or PPO)

from stable_baselines3 import PPO, DQN
from stable_baselines3.common.vec_env import DummyVecEnv


class RLTradingAgent:
    def __init__(self, env, algorithm="PPO", policy="MlpPolicy", verbose=1):
        """
        env: TradingEnvironment instance
        algorithm: "PPO" or "DQN"
        policy: Policy network architecture
        verbose: Verbosity level
        """
        self.env = DummyVecEnv([lambda: env])  # Wrap environment for SB3
        self.algorithm = algorithm.upper()
        self.policy = policy
        self.verbose = verbose

        if self.algorithm == "PPO":
            self.model = PPO(self.policy, self.env, verbose=self.verbose)
        elif self.algorithm == "DQN":
            self.model = DQN(self.policy, self.env, verbose=self.verbose)
        else:
            raise ValueError("Unsupported algorithm: Choose PPO or DQN")

    def train(self, timesteps=100_000):
        """
        Train the agent for a number of timesteps
        """
        print(f"Training {self.algorithm} agent for {timesteps} timesteps...")
        self.model.learn(total_timesteps=timesteps)
        print("Training complete!")

    def predict(self, state, deterministic=True):
        """
        Predict action for given state
        """
        action, _ = self.model.predict(state, deterministic=deterministic)
        return action

    def save(self, path="rl_trading_agent.zip"):
        """
        Save model to disk
        """
        self.model.save(path)
        print(f"Model saved to {path}")

    def load(self, path="rl_trading_agent.zip"):
        """
        Load model from disk
        """
        if self.algorithm == "PPO":
            self.model = PPO.load(path, env=self.env)
        elif self.algorithm == "DQN":
            self.model = DQN.load(path, env=self.env)
        print(f"Model loaded from {path}")