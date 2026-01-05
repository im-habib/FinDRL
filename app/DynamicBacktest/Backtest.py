import numpy as np
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt


class Backtest:
    """
    A class to backtest trading strategies based on different indicators from pandas_ta.
    """
    def __init__(self, data):
        """
        Initializes the backtesting class with historical price data.
        
        Parameters:
        - data: A pandas DataFrame containing historical stock data with 'Close' prices.
        """
        # Standardize column names to lowercase
        self.data = data.copy()
        self.data.columns = self.data.columns.str.lower()
        self.results = None  # To store backtest results

    def add_indicator(self, indicator_name, **kwargs):
        """
        Adds the chosen indicator to the data with the specified parameters.
        
        Parameters:
        - indicator_name: Name of the indicator (e.g., 'rsi', 'macd', 'bbands').
        - kwargs: Additional arguments specific to each indicator.
        """
        if hasattr(ta, indicator_name):
            # Ensure the close column is accessed in lowercase
            indicator = getattr(ta, indicator_name)(self.data['close'], **kwargs)
            
            # If the indicator returns multiple columns (e.g., MACD, Bollinger Bands)
            if isinstance(indicator, pd.DataFrame):
                for col in indicator.columns:
                    self.data[col.lower()] = indicator[col]  # Convert indicator columns to lowercase
            else:
                self.data[indicator_name.lower()] = indicator  # Store in lowercase
        else:
            raise ValueError(f"Indicator '{indicator_name}' not found in pandas_ta.")

    def generate_signals(self, indicator_name, buy_condition, sell_condition):
        """
        Generates buy/sell signals based on custom conditions.
        
        Parameters:
        - indicator_name: Column name of the indicator in the DataFrame.
        - buy_condition: A lambda function to define buy condition (e.g., lambda x: x < 30).
        - sell_condition: A lambda function to define sell condition (e.g., lambda x: x > 70).
        """
        # Ensure the indicator name is lowercase
        indicator_name = indicator_name.lower()
        
        self.data['Signal'] = np.where(buy_condition(self.data[indicator_name]), 1,
                                       np.where(sell_condition(self.data[indicator_name]), -1, 0))

    def backtest(self):
        """
        Backtests the strategy based on generated signals and calculates cumulative returns.
        """
        self.data['Strategy Returns'] = self.data['Signal'].shift(1) * self.data['close'].pct_change()
        self.data['Cumulative Returns'] = (1 + self.data['Strategy Returns']).cumprod()
        self.results = self.data[['Cumulative Returns']].dropna()
        return self.results

    def plot_results(self):
        """Plots the cumulative returns of the strategy."""
        if self.results is not None:
            self.results.plot(title='Cumulative Returns')
            plt.xlabel('Date')
            plt.ylabel('Cumulative Returns')
            plt.show()
        else:
            print("No results to plot. Run the backtest first.")

    # """
    # A class to backtest trading strategies based on different indicators from pandas_ta.
    # """
    # def __init__(self, data):
    #     """
    #     Initializes the backtesting class with historical price data.
    #     Parameters:
    #     - data: A pandas DataFrame containing historical stock data with 'Close' prices.
    #     """
    #     # Standardize column names to lowercase
    #     self.data = data.copy()
    #     self.data.columns = self.data.columns.str.lower()
    #     self.results = None  # To store backtest results

    # def add_indicator(self, indicator_name, **kwargs):
    #     """
    #     Adds the chosen indicator to the data with the specified parameters.
        
    #     Parameters:
    #     - indicator_name: Name of the indicator (e.g., 'rsi', 'macd', 'bbands').
    #     - kwargs: Additional arguments specific to each indicator.
    #     """
    #     if hasattr(ta, indicator_name):
    #         # Use 'close' in lowercase to match standardized columns
    #         indicator = getattr(ta, indicator_name)(self.data['close'], **kwargs)
            
    #         # If the indicator returns multiple columns (e.g., MACD, Bollinger Bands)
    #         if isinstance(indicator, pd.DataFrame):
    #             for col in indicator.columns:
    #                 self.data[col] = indicator[col]
    #         else:
    #             self.data[indicator_name.upper()] = indicator
    #     else:
    #         raise ValueError(f"Indicator '{indicator_name}' not found in pandas_ta.")

    # def generate_signals(self, indicator_name, buy_condition, sell_condition):
    #     """
    #     Generates buy/sell signals based on custom conditions.
        
    #     Parameters:
    #     - indicator_name: Column name of the indicator in the DataFrame.
    #     - buy_condition: A lambda function to define buy condition (e.g., lambda x: x < 30).
    #     - sell_condition: A lambda function to define sell condition (e.g., lambda x: x > 70).
    #     """
    #     self.data['Signal'] = np.where(buy_condition(self.data[indicator_name]), 1,
    #                                    np.where(sell_condition(self.data[indicator_name]), -1, 0))

    # def backtest(self):
    #     """
    #     Backtests the strategy based on generated signals and calculates cumulative returns.
    #     """
    #     self.data['Strategy Returns'] = self.data['Signal'].shift(1) * self.data['close'].pct_change()
    #     self.data['Cumulative Returns'] = (1 + self.data['Strategy Returns']).cumprod()
    #     self.results = self.data[['Cumulative Returns']].dropna()
    #     return self.results

    # def plot_results(self):
    #     """Plots the cumulative returns of the strategy."""
    #     if self.results is not None:
    #         self.results.plot(title='Cumulative Returns')
    #         plt.xlabel('Date')
    #         plt.ylabel('Cumulative Returns')
    #         plt.show()
    #     else:
    #         print("No results to plot. Run the backtest first.")
