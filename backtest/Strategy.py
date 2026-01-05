import pandas as pd
from itertools import product

class Backtester:
    def __init__(self, dataframe, initial_balance=10000, transaction_fee=0.001):
        """
        Initialize the backtester with the provided DataFrame and parameters.
        
        Args:
            dataframe (pd.DataFrame): The input DataFrame containing raw data and indicators.
            initial_balance (float): The starting balance for the backtest.
            transaction_fee (float): Transaction fee as a percentage (default: 0.1% or 0.001).
        """
        self.trade_log = []  # To store details of each trade
        self.balance = initial_balance
        self.dataframe = dataframe.copy()
        self.initial_balance = initial_balance
        self.transaction_fee = transaction_fee
        self.dataframe["datetime"] = self.dataframe.index
        self.excluded_columns = ['datetime', 'open', 'high', 'low', 'close', 'adj close', 'volume', 'ticker']

    def prepare_data(self):
        """
        Prepare the data by calculating returns and binary labels.
        """
        self.dataframe["return"] = (self.dataframe["close"] - self.dataframe["open"]) / self.dataframe["open"]
        self.dataframe["label"] = (self.dataframe["return"] > 0).astype(int)  # 1 for profit, 0 for loss

    def generate_threshold_combinations(self, low_range, high_range, step=1):
        """
        Generate all combinations of lower and upper thresholds within the range.

        Args:
            low_range (int): Start of the lower threshold range.
            high_range (int): End of the upper threshold range.
            step (int): Step size for thresholds.

        Returns:
            list of tuple: All valid (low, high) combinations.
        """
        values = range(low_range, high_range, step)
        params = [(low, high) for low, high in product(values, repeat=2)]
        return params

    def execute_trade(self, entry_price, exit_price, signal):
        """
        Execute a trade, update the balance, and log trade details.

        Args:
            entry_price (float): Price at which the trade is entered.
            exit_price (float): Price at which the trade is exited.
            signal (int): Trade signal (1 for buy, -1 for sell).

        Returns:
            float: Profit or loss from the trade.
        """
        # Calculate trade amount (fixed percentage of balance, e.g., 10%)
        trade_amount = self.balance * 0.1
        position_size = trade_amount / entry_price  # Number of shares/contracts

        # Calculate fees
        entry_fee = trade_amount * self.transaction_fee
        exit_fee = (position_size * exit_price) * self.transaction_fee
        total_fee = entry_fee + exit_fee

        # Calculate profit/loss
        profit = (position_size * (exit_price - entry_price) * signal) - total_fee

        # Update balance
        self.balance += profit

        # Log trade details
        self.trade_log.append({
            "entry_price": entry_price,
            "exit_price": exit_price,
            "signal": signal,
            "trade_amount": trade_amount,
            "position_size": position_size,
            "profit": profit,
            "balance": self.balance,
            "fees": total_fee
        })

        return profit

    def backtest_single_indicator(self, indicator_name, low_range, high_range, step=1):
        """
        Backtest a single indicator with all possible threshold combinations.

        Args:
            indicator_name (str): The name of the indicator column to test.
            low_range (int): Start of the lower threshold range.
            high_range (int): End of the upper threshold range.
            step (int): Step size for thresholds.

        Returns:
            pd.DataFrame: Backtest results with metrics.
        """
        threshold_combinations = self.generate_threshold_combinations(low_range, high_range, step) #1 - 100, 1
        results = []

        for low, high in threshold_combinations:
            self.balance = self.initial_balance  # Reset balance for each threshold test
            self.trade_log = []  # Clear trade log

            indicator_df = self.dataframe.copy()
            indicator_df["signal"] = 0
            indicator_df.loc[indicator_df[indicator_name] < low, "signal"] = 1  # Buy
            indicator_df.loc[indicator_df[indicator_name] > high, "signal"] = -1  # Sell

            # Simulate trades
            for i, row in indicator_df.iterrows():
                if row["signal"] != 0:
                    next_row = indicator_df.iloc[i + 1] if i + 1 < len(indicator_df) else None
                    if next_row is not None:
                        self.execute_trade(row["close"], next_row["close"], row["signal"])

            # Metrics
            total_profit = self.balance - self.initial_balance
            accuracy = sum(1 for trade in self.trade_log if trade["profit"] > 0) / len(self.trade_log) if self.trade_log else 0
            sharpe_ratio = pd.Series([trade["profit"] for trade in self.trade_log]).mean() / (
                    pd.Series([trade["profit"] for trade in self.trade_log]).std() + 1e-8)

            results.append({
                "indicator": indicator_name,
                "low_threshold": low,
                "high_threshold": high,
                "total_profit": total_profit,
                "accuracy": accuracy,
                "sharpe_ratio": sharpe_ratio,
                "final_balance": self.balance
            })

        return pd.DataFrame(results), pd.DataFrame(self.trade_log)

    def backtest_all_indicators(self, low_range=1, high_range=100, step=1):
        """
        Backtest all indicators with threshold combinations.

        Args:
            low_range (int): Start of the lower threshold range.
            high_range (int): End of the upper threshold range.
            step (int): Step size for thresholds.
        Returns:
            pd.DataFrame: Aggregated results for all indicators.
            dict: Dictionary containing the new DataFrame for each indicator.
        """
        aggregated_results = []
        indicator_dataframes = {}

        for column in self.dataframe.columns:
            if column in self.excluded_columns:
                continue  # Skip excluded columns

            print(f"Backtesting indicator: {column}")
            result, indicator_df = self.backtest_single_indicator(column, low_range, high_range, step)
            aggregated_results.append(result)
            indicator_dataframes[column] = indicator_df

        return pd.concat(aggregated_results, ignore_index=True), indicator_dataframes

    def get_top_parameters(self, results_df, metric="total_profit", top_n=5):
        """
        Extract the top N parameter configurations for each indicator group based on a specified metric.

        Args:
            results_df (pd.DataFrame): The aggregated backtesting results for all indicators.
            metric (str): The metric to sort by (default: "total_profit").
            top_n (int): The number of top parameter sets to return for each indicator group (default: 5).

        Returns:
            dict: A dictionary where keys are indicator groups and values are DataFrames of the top N configurations.
        """
        if metric not in results_df.columns:
            raise ValueError(f"Metric '{metric}' is not found in the results DataFrame.")

        # Group the results by indicator group
        grouped_results = {}
        for group, indicators in self.group_indicators(results_df["indicator"]):
            # Filter results for this group
            group_results = results_df[results_df["indicator"].isin(indicators)]

            # Get the top N rows based on the metric
            top_results = group_results.nlargest(top_n, metric)
            grouped_results[group] = top_results

        return grouped_results

    def group_indicators(self, indicators):
        """
        Group indicators based on their root names.

        Args:
            indicators (pd.Series or list of str): The list of indicator names.

        Returns:
            dict: A dictionary where keys are indicator groups and values are lists of indicators.
        """
        from collections import defaultdict

        indicator_groups = defaultdict(list)

        for indicator in indicators:
            if "_" in indicator:  # Ensure the column has a recognizable parameter pattern
                root_name = indicator.split("_")[0]  # Extract the prefix (indicator type)
                indicator_groups[root_name].append(indicator)

        return dict(indicator_groups)


# def backtest_single_indicator(self, indicator_name, low_range, high_range, step=1):
#     """
#     Backtest a single indicator with all possible threshold combinations.

#     Args:
#         indicator_name (str): The name of the indicator column to test.
#         low_range (int): Start of the lower threshold range.
#         high_range (int): End of the upper threshold range.
#         step (int): Step size for thresholds.

#     Returns:
#         pd.DataFrame: Backtest results with signals, entry/exit times, and metrics.
#     """
#     # Create a new DataFrame for the indicator
#     indicator_df = self.dataframe[["datetime", indicator_name]].copy()
#     indicator_df["return"] = self.dataframe["return"]
#     indicator_df["label"] = self.dataframe["label"]

#     threshold_combinations = self.generate_threshold_combinations(low_range, high_range, step)
#     results = []

#     for low, high in threshold_combinations:
#         indicator_df["signal"] = 0
#         indicator_df.loc[indicator_df[indicator_name] < low, "signal"] = 1  # Buy
#         indicator_df.loc[indicator_df[indicator_name] > high, "signal"] = -1  # Sell

#         # Add entry and exit times
#         indicator_df["entry_time"] = indicator_df.loc[indicator_df["signal"] != 0, "datetime"]
#         indicator_df["exit_time"] = indicator_df["entry_time"].shift(-1)

#         # Calculate profit and metrics
#         indicator_df["profit"] = indicator_df["return"] * indicator_df["signal"]
#         total_profit = indicator_df["profit"].sum()
#         accuracy = (indicator_df["signal"] == indicator_df["label"]).mean()
#         sharpe_ratio = indicator_df["profit"].mean() / (indicator_df["profit"].std() + 1e-8)
#         cumulative_return = indicator_df["profit"].cumsum().iloc[-1]

#         results.append({
#             "indicator": indicator_name,
#             "low_threshold": low,
#             "high_threshold": high,
#             "total_profit": total_profit,
#             "accuracy": accuracy,
#             "sharpe_ratio": sharpe_ratio,
#             "cumulative_return": cumulative_return
#         })
#     return pd.DataFrame(results), indicator_df

# import pandas as pd
# from itertools import product

# class Backtester:
#     def __init__(self, dataframe):
#         """
#         Initialize the backtester.
#         Args:
#             dataframe (pd.DataFrame): The input DataFrame containing indicators and raw data.
#         """
#         self.dataframe = dataframe.copy()
#         self.dataframe["datetime"] = self.dataframe.index
#         self.excluded_columns = ['datetime', 'open', 'high', 'low', 'close', 'adj close', 'volume', 'ticker']

#     def prepare_data(self):
#         """
#         Prepare the data by calculating returns and binary labels.
#         """
#         self.dataframe["return"] = (self.dataframe["close"] - self.dataframe["open"]) / self.dataframe["open"]
#         self.dataframe["label"] = (self.dataframe["return"] > 0).astype(int)  # 1 for profit, 0 for loss

#     def generate_threshold_combinations(self, low_range, high_range, step=1):
#         """
#         Generate all combinations of lower and upper thresholds within the range.

#         Args:
#             low_range (int): Start of the lower threshold range.
#             high_range (int): End of the upper threshold range.
#             step (int): Step size for thresholds.

#         Returns:
#             list of tuple: All valid (low, high) combinations.
#         """
#         low_values = range(low_range, high_range, step)
#         high_values = range(low_range, high_range, step)
#         return [(low, high) for low, high in product(low_values, high_values) if low < high]

#     def backtest_indicator_with_thresholds(self, indicator_name, low_range, high_range, step=1):
#         """
#         Backtest a single indicator with all possible threshold combinations.

#         Args:
#             indicator_name (str): The name of the indicator column to test.
#             low_range (int): Start of the lower threshold range.
#             high_range (int): End of the upper threshold range.
#             step (int): Step size for thresholds.

#         Returns:
#             pd.DataFrame: Results for each combination of thresholds.
#         """
#         threshold_combinations = self.generate_threshold_combinations(low_range, high_range, step)
#         results = []

#         for low, high in threshold_combinations:
#             self.dataframe["signal"] = 0
#             self.dataframe.loc[self.dataframe[indicator_name] < low, "signal"] = 1  # Buy
#             self.dataframe.loc[self.dataframe[indicator_name] > high, "signal"] = -1  # Sell

#             # Add entry and exit time
#             self.dataframe["entry_time"] = self.dataframe.loc[self.dataframe["signal"] != 0, "datetime"]
#             self.dataframe["exit_time"] = self.dataframe["entry_time"].shift(-1)

#             self.dataframe["profit"] = self.dataframe["return"] * self.dataframe["signal"]
#             total_profit = self.dataframe["profit"].sum()
#             accuracy = (self.dataframe["signal"] == self.dataframe["label"]).mean()
#             sharpe_ratio = self.dataframe["profit"].mean() / (self.dataframe["profit"].std() + 1e-8)

#             for _, row in self.dataframe.loc[self.dataframe["signal"] != 0].iterrows():
#                 results.append({
#                     "close": row["close"],
#                     "entry_time": row["entry_time"],
#                     "exit_time": row["exit_time"],
#                     "indicator": indicator_name,
#                     "low_threshold": low,
#                     "high_threshold": high,
#                     "total_profit": total_profit,
#                     "accuracy": accuracy,
#                     "sharpe_ratio": sharpe_ratio,
#                 })

#         return pd.DataFrame(results)

#     def backtest_all_indicators_with_thresholds(self, low_range=1, high_range=100, step=1):
#         """
#         Backtest all calculated indicators with threshold combinations.

#         Args:
#             low_range (int): Start of the lower threshold range.
#             high_range (int): End of the upper threshold range.
#             step (int): Step size for thresholds.
#         Returns:
#             pd.DataFrame: Aggregated results for all indicators.
#         """
#         aggregated_results = []
#         for column in self.dataframe.columns:
#             if column in self.excluded_columns:
#                 continue  # Skip excluded columns
#             print(f"Backtesting indicator: {column}")
#             result = self.backtest_indicator_with_thresholds(column, low_range, high_range, step)
#             aggregated_results.append(result)

#         return pd.concat(aggregated_results, ignore_index=True), self.dataframe


# import pandas as pd
# from itertools import product

# class Backtester:
#     def __init__(self, dataframe, excluded_columns=None):
#         """
#         Initialize the backtester.
#         Args:
#             dataframe (pd.DataFrame): The input DataFrame containing indicators and raw data.
#             excluded_columns (list): Columns to exclude from indicator backtesting.
#         """
#         self.dataframe = dataframe.copy()
#         self.excluded_columns = excluded_columns if excluded_columns else []

#     def prepare_data(self):
#         """
#         Prepare the data by calculating returns and binary labels.
#         """
#         self.dataframe["return"] = (self.dataframe["close"] - self.dataframe["open"]) / self.dataframe["open"]
#         self.dataframe["label"] = (self.dataframe["return"] > 0).astype(int)  # 1 for profit, 0 for loss
#         # self.dataframe = self.dataframe.dropna()

#     def generate_threshold_combinations(self, low_range, high_range, step=1):
#         """
#         Generate all combinations of lower and upper thresholds within the range.

#         Args:
#             low_range (int): Start of the lower threshold range.
#             high_range (int): End of the upper threshold range.
#             step (int): Step size for thresholds.

#         Returns:
#             list of tuple: All valid (low, high) combinations.
#         """
#         low_values = range(low_range, high_range, step)
#         high_values = range(low_range, high_range, step)
#         return [(low, high) for low, high in product(low_values, high_values) if low < high]

#     def backtest_indicator_with_thresholds(self, indicator_name, low_range, high_range, step=1):
#         """
#         Backtest a single indicator with all possible threshold combinations.

#         Args:
#             indicator_name (str): The name of the indicator column to test.
#             low_range (int): Start of the lower threshold range.
#             high_range (int): End of the upper threshold range.
#             step (int): Step size for thresholds.

#         Returns:
#             pd.DataFrame: Results for each combination of thresholds.
#         """
#         threshold_combinations = self.generate_threshold_combinations(low_range, high_range, step)
#         results = []

#         for low, high in threshold_combinations:
#             self.dataframe["signal"] = 0
#             self.dataframe.loc[self.dataframe[indicator_name] < low, "signal"] = 1  # Buy
#             self.dataframe.loc[self.dataframe[indicator_name] > high, "signal"] = -1  # Sell

#             self.dataframe["profit"] = self.dataframe["return"] * self.dataframe["signal"]
#             total_profit = self.dataframe["profit"].sum()
#             accuracy = (self.dataframe["signal"] == self.dataframe["label"]).mean()
#             sharpe_ratio = self.dataframe["profit"].mean() / (self.dataframe["profit"].std() + 1e-8)

#             results.append({
#                 "indicator": indicator_name,
#                 "low_threshold": low,
#                 "high_threshold": high,
#                 "total_profit": total_profit,
#                 "accuracy": accuracy,
#                 "sharpe_ratio": sharpe_ratio,
#             })

#         return pd.DataFrame(results)

#     def backtest_all_indicators_with_thresholds(self, low_range=1, high_range=100, step=1):
#         """
#         Backtest all calculated indicators with threshold combinations.

#         Args:
#             low_range (int): Start of the lower threshold range.
#             high_range (int): End of the upper threshold range.
#             step (int): Step size for thresholds.
#         Returns:
#             pd.DataFrame: Aggregated results for all indicators.
#         """
#         aggregated_results = []
#         for column in self.dataframe.columns:
#             if column in self.excluded_columns:
#                 continue  # Skip excluded columns
#             print(f"Backtesting indicator: {column}")
#             result = self.backtest_indicator_with_thresholds(column, low_range, high_range, step)
#             aggregated_results.append(result)

#         return pd.concat(aggregated_results, ignore_index=True)


# import numpy as np
# import pandas as pd
# from strategies.Strategies import StrategyBuilder

# class Backtester:
#     def __init__(self, initial_balance=10000, transaction_cost=0.001):
#         """
#         Initialize the BackTester.

#         Parameters:
#         - initial_balance: The starting capital for backtesting.
#         - transaction_cost: Transaction cost as a fraction of trade value.
#         """
#         self.initial_balance = initial_balance
#         self.transaction_cost = transaction_cost

#     def backtest_strategy(self, data, strategy):
#         """
#         Perform backtesting for a single strategy.

#         Parameters:
#         - data: DataFrame containing the dataset.
#         - strategy: Dictionary with 'buy_expression' and 'sell_expression'.

#         Returns:
#         - Dictionary with strategy and performance metrics.
#         """
#         backtest_data = data.copy()

#         # Evaluate buy and sell signals
#         try:
#             backtest_data['buy_signal'] = backtest_data.eval(strategy['buy_expression'])
#             backtest_data['sell_signal'] = backtest_data.eval(strategy['sell_expression'])
#         except Exception as e:
#             print(f"Error evaluating strategy: {strategy}, Error: {e}")
#             return {'strategy': strategy, 'metrics': None}

#         # Initialize portfolio state
#         backtest_data['position'] = 0
#         position = 0

#         # Apply buy/sell logic
#         for i in range(len(backtest_data)):
#             if backtest_data.at[i, 'buy_signal'] and position == 0:  # Buy signal
#                 position = 1
#             elif backtest_data.at[i, 'sell_signal'] and position == 1:  # Sell signal
#                 position = 0
#             backtest_data.at[i, 'position'] = position

#         # Calculate daily returns and portfolio value
#         backtest_data['daily_return'] = (
#             backtest_data['position'] * backtest_data['close'].pct_change()
#         )
#         backtest_data['portfolio_value'] = (1 + backtest_data['daily_return'].fillna(0)).cumprod() * self.initial_balance
#         backtest_data['cumulative_return'] = (1 + backtest_data['daily_return']).cumprod()
#         sharpe_ratio = self.calculate_sharpe_ratio(backtest_data['daily_return'])
#         max_drawdown = self.calculate_max_drawdown(backtest_data['cumulative_return'])

#         # Adjust for transaction costs
#         trades = backtest_data['position'].diff().abs().sum()
#         total_cost = trades * self.transaction_cost * self.initial_balance
#         final_value = backtest_data['portfolio_value'].iloc[-1] - total_cost

#         # Performance metrics
#         total_return = (final_value - self.initial_balance) / self.initial_balance
#         metrics = {
#             'total_return': total_return,
#             'final_value': final_value,
#             'total_trades': trades,
#             'total_cost': total_cost,
#             'sharpe_ratio': sharpe_ratio,
#             'max_drawdown': max_drawdown,
#         }

#         # trades, total_cost, total_return, sharpe_ratio, max_drawdown,

#         return {'strategy': strategy, 'metrics': metrics}

#     def calculate_sharpe_ratio(self, daily_returns):
#         """
#         Calculate the Sharpe ratio given daily returns.

#         Parameters:
#         - daily_returns: Series of daily returns.

#         Returns:
#         - Sharpe ratio (float).
#         """
#         mean_return = daily_returns.mean()
#         std_return = daily_returns.std()
#         sharpe_ratio = (mean_return / std_return) * (252 ** 0.5) if std_return != 0 else 0
#         return sharpe_ratio


#     def calculate_max_drawdown(self, cumulative_returns):
#         """
#         Calculate the maximum drawdown.

#         Parameters:
#         - cumulative_returns: Series of cumulative returns.

#         Returns:
#         - Maximum drawdown (float).
#         """
#         running_max = cumulative_returns.cummax()
#         drawdown = (cumulative_returns - running_max) / running_max
#         max_drawdown = drawdown.min()
#         return max_drawdown

#     def evaluate_strategies(self, data, strategies):
#         """
#         Evaluate multiple strategies on the given data.

#         Parameters:
#         - data: DataFrame containing the dataset.
#         - strategies: List of strategy dictionaries.

#         Returns:
#         - DataFrame containing strategy expressions and their performance metrics.
#         """
#         results = []

#         for strategy in strategies:
#             result = self.backtest_strategy(data.copy(), strategy)
#             if result['metrics'] is not None and result["performance"] is not None:
#                 results.append({
#                     'buy_expression': result['strategy']['buy_expression'],
#                     'sell_expression': result['strategy']['sell_expression'],
#                     **result['metrics'],
#                     **result["performance"]

#                 })

#         # Convert results to a DataFrame
#         results_df = pd.DataFrame(results)
#         results_df = results_df.sort_values(by='total_return', ascending=False)
#         total_return_sum = results_df['total_return'].sum()
#         results_df['return_percentage'] = (results_df['total_return'] / total_return_sum) * 100

#         return results_df


# if __name__ == "main":
#     # Sample data
#     n_samples = 5000

#     data = pd.DataFrame({
#         'close': np.random.uniform(100, 200, n_samples),
#         'open': np.random.uniform(100, 200, n_samples),
#         'high': np.random.uniform(100, 200, n_samples),
#         'low': np.random.uniform(100, 200, n_samples),
#         'volume': np.random.uniform(1000, 5000, n_samples),
#     })

#     df = pd.DataFrame(data)
#     strategy_builder = StrategyBuilder()
#     strategies = strategy_builder.build(df, num_indicators=3)

#     # Initialize the backtester
#     backtester = Backtester()
#     results_df = backtester.evaluate_strategies(df, strategies)
# import random as rd
# from backtesting import Backtest
# from backtest.BacktestStrategy import BStrategy


# class Backtesting:
#     def __init__(self, data, cash=10000, commission=0.001):
#         """
#         Initialize the backtesting framework.

#         Parameters:
#         - data: The historical data as a DataFrame.
#         - cash: Initial cash balance for backtesting.
#         - commission: Commission rate per trade.
#         """
#         self.data = data
#         self.cash = cash
#         self.commission = commission
    
#     def generate_random_conditions(self, parameter):
#         """
#         Generate random buy threshold around a parameter for the indicator.

#         Parameters:
#         - parameter: The central parameter value to determine thresholds.

#         Returns:
#         - threshold: A randomly chosen threshold for buy condition.
#         """
#         # Define range around the parameter for thresholds
#         threshold = rd.randint(parameter - 5, parameter + 5)
#         return threshold

#     def run_backtest(self, indicator_series, parameter):
#         """
#         Run the backtest with a single indicator and random buy/sell conditions around a parameter.

#         Parameters:
#         - indicator_func: A pandas-ta function like ta.rsi or ta.sma.
#         - indicator_params: Parameters for the indicator function (e.g., {'length': 14}).
#         - parameter: Central value for threshold randomization.
#         - check_field: The column in `data` on which the indicator operates (e.g., 'Close').
#         - indicator_name: Name of the indicator for labeling (optional).

#         Returns:
#         - stats: Performance statistics of the backtest.
#         """
#         # Generate random buy threshold
#         threshold = self.generate_random_conditions(parameter)

        
        
#         # Initialize the Backtest instance with parameters for DynamicStrategy
#         bt = Backtest(self.data, BStrategy, cash=self.cash, commission=self.commission)        
#         # Run the backtest and pass parameters
#         stats = bt.run(
#             indicator_series=indicator_series,
#             threshold=threshold
#         )

#         return stats


# class Backtesting:
#     def __init__(self, data, cash=10000, commission=0.001):
#         """
#         Initialize the backtesting framework.

#         Parameters:
#         - data: The historical data as a DataFrame.
#         - cash: Initial cash balance for backtesting.
#         - commission: Commission rate per trade.
#         """
#         self.data = data
#         self.cash = cash
#         self.commission = commission
    
#     def generate_random_conditions(self, parameter):
#         """
#         Generate random buy threshold around a parameter.
#         """
#         return rd.randint(int(parameter) - 5, int(parameter) + 5)

#     def run_backtest(self, indicator_series, parameter):
#         """
#         Run the backtest with a single indicator and random buy/sell conditions around a parameter.

#         Parameters:
#         - indicator_func: A pandas-ta function like ta.rsi or ta.sma.
#         - indicator_params: Parameters for the indicator function (e.g., {'length': 14}).
#         - parameter: Central value for threshold randomization.
#         - check_field: The column in `data` on which the indicator operates (e.g., 'Close').
#         - indicator_name: Name of the indicator for labeling (optional).

#         Returns:
#         - stats: Performance statistics of the backtest.
#         """
#         # Generate random buy threshold
#         threshold = self.generate_random_conditions(parameter)
        
#         # Initialize the Backtest instance with parameters for DynamicStrategy
#         bt = Backtest(self.data, BStrategy, cash=self.cash, commission=self.commission)        
#         # Run the backtest and pass parameters
#         stats = bt.run(
#             threshold=threshold,
#             indicator_series=indicator_series,
#         )
#         return stats