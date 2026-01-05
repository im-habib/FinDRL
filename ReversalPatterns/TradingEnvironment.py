# 4. TradingEnvironment (Gym-like)

import gym
import numpy as np
from gym import spaces

class TradingEnvironment(gym.Env):
    def __init__(self, data, initial_balance=10000, max_position=1):
        """
        data: pd.DataFrame from MultiTimeframeDataset
        initial_balance: Starting cash
        max_position: Max position size (1 = full position, 0.5 = half)
        """
        super(TradingEnvironment, self).__init__()

        self.data = data.values
        self.n_steps = len(data)
        self.initial_balance = initial_balance
        self.max_position = max_position

        # Action space: 0 = Hold, 1 = Buy, 2 = Sell
        self.action_space = spaces.Discrete(3)

        # Observation space: MultiTimeframe features
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(data.shape[1],), dtype=np.float32)

        self.reset()

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0  # -1 = short, 0 = flat, +1 = long
        self.entry_price = 0
        self.total_profit = 0
        return self.data[self.current_step]

    def step(self, action):
        """
        action: 0=Hold, 1=Buy, 2=Sell
        """
        reward = 0
        done = False
        price = self._get_current_price()

        # Execute action
        if action == 1 and self.position == 0:  # Buy
            self.position = 1
            self.entry_price = price
        elif action == 2 and self.position == 0:  # Sell (short)
            self.position = -1
            self.entry_price = price
        elif action == 1 and self.position == -1:  # Cover short
            reward = (self.entry_price - price) * self.max_position
            self.balance += reward
            self.total_profit += reward
            self.position = 0
        elif action == 2 and self.position == 1:  # Close long
            reward = (price - self.entry_price) * self.max_position
            self.balance += reward
            self.total_profit += reward
            self.position = 0

        # Move to next step
        self.current_step += 1
        if self.current_step >= self.n_steps - 1:
            done = True

        # Observation
        obs = self.data[self.current_step]

        # Optional: Penalize holding losing positions
        if self.position == 1:
            reward += (price - self.entry_price) * 0.01
        elif self.position == -1:
            reward += (self.entry_price - price) * 0.01

        return obs, reward, done, {}

    def _get_current_price(self):
        # Assume close price is at column index 3 (adjust as needed)
        return self.data[self.current_step, 3]