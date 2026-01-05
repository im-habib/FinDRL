import numpy as np
import pandas as pd
from random import sample


class StrategyBuilder:
    def __init__(self):
        """
        Initialize the Strategy Builder.
        """
        self.operators = ['>', '<', '>=', '<=', '==', '!=']  # Supported comparison operators
        self.excluded_columns = ['date', 'open', 'high', 'low', 'close', 'adj close', 'volume', 'ticker']

    def build(self, data, num_indicators=2):
        """
        Build strategies dynamically based on the number of indicators.
        Parameters:
        - data: DataFrame containing the dataset.
        - excluded_columns: List of columns to exclude.
        - num_indicators: Number of indicators to use in the strategy.
        Returns:
        - List of strategy dictionaries.
        """
        # Filter indicators by excluding specified columns
        indicators = [col for col in data.columns if col.lower() not in self.excluded_columns]
        # Ensure there are enough indicators
        if len(indicators) < num_indicators:
            raise ValueError(f"Not enough indicators for num_indicators={num_indicators}.")

        # Create a set to track unique strategies
        unique_strategies = set()

        # Generate strategies until all possible combinations are exhausted
        max_combinations = len(indicators[:10])
        while len(unique_strategies) < max_combinations:
            # Randomly choose a combination of indicators
            combination = tuple(sorted(sample(indicators, num_indicators)))

            # Generate buy and sell expressions dynamically
            buy_conditions = [f"{combination[i]} > {combination[i+1]}" for i in range(len(combination) - 1)]
            sell_conditions = [f"{combination[i]} < {combination[i+1]}" for i in range(len(combination) - 1)]

            # Combine conditions using logical operators
            buy_expression = " & ".join(buy_conditions)
            sell_expression = " | ".join(sell_conditions)

            # Create a strategy tuple to ensure uniqueness
            strategy_tuple = (buy_expression, sell_expression)
            if strategy_tuple not in unique_strategies:
                unique_strategies.add(strategy_tuple)

        # Convert the set of strategies to a list of dictionaries
        strategies = [{'buy_expression': buy, 'sell_expression': sell} for buy, sell in unique_strategies]
        return strategies

if __name__ == "main":
    # Sample data
    n_samples = 2000

    data = pd.DataFrame({
        'close': np.random.uniform(100, 200, n_samples),
        'open': np.random.uniform(100, 200, n_samples),
        'high': np.random.uniform(100, 200, n_samples),
        'low': np.random.uniform(100, 200, n_samples),
        'volume': np.random.uniform(1000, 5000, n_samples),
    })

    df = pd.DataFrame(data)
    strategy_builder = StrategyBuilder()
    strategies = strategy_builder.build(df, num_indicators=3)