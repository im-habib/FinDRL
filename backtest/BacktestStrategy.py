from backtesting import Strategy

class BStrategy(Strategy):
    # Define class attributes to be set dynamically

    # indicator_params = None
    # check_field = None
    threshold = None
    indicator_series = None
    
    def init(self):
        """
        Initialize the indicator dynamically using the provided pandas-ta function.
        """
        # Ensure that indicator_func, indicator_params, and check_field are set
        # assert self.indicator_func is not None, "indicator_func is not set"
        # assert self.indicator_params is not None, "indicator_params is not set"
        # assert self.check_field is not None, "check_field is not set"

        # Access the underlying DataFrame from self.data
        # data_series = self.data.df[self.check_field]

        # Debug: Print the first few values of the input data
        # print("Input data for indicator computation:")
        # print(data_series.head())

        # Compute the indicator
        # indicator_series = self.indicator_func(data_series, **self.indicator_params)
        
        # Debug: Check the output of the indicator
        # print("Computed indicator values (first 5 rows):")
        # print(indicator_series.head() if indicator_series is not None else "Indicator computation returned None")

        # Check if indicator_series is valid
        if self.indicator_series is not None and len(self.indicator_series) == len(self.data.df):
            # Convert to numpy array and assign to self.indicator
            self.indicator = self.I(lambda: self.indicator_series.to_numpy())
        else:
            # If the length doesn't match or computation failed, raise an error with details
            raise ValueError("Indicator computation failed or resulted in incorrect length.")
        
        print(f"threshold: {self.threshold}")
    
    def next(self):
        """
        Execute buy/sell signals based on provided conditions.
        """
        # Check buy condition
        if self.indicator[-1] > self.threshold:
            self.buy()
                
        if self.indicator[-1] < self.threshold:
            self.sell()



# Initialize and run the dynamic backtest with random conditions around a parameter
# dynamic_backtest = DynamicBacktest(df)
# stats = dynamic_backtest.run_backtest(indicator_series, parameter)

# # Print the performance statistics
# print(stats)



# import random as rd
# import pandas as pd
# import pandas_ta as ta
# from backtesting import Backtest, Strategy
# # from backtesting.test import GOOG


# class DynamicStrategy(Strategy):
#     # Define class attributes to be set dynamically
#     indicator_func = None
#     indicator_params = None
#     check_field = None
#     threshold = None

#     def init(self):
#         """
#         Initialize the indicator dynamically using the provided pandas-ta function.
#         """
#         # Ensure that indicator_func, indicator_params, and check_field are set
#         assert self.indicator_func is not None, "indicator_func is not set"
#         assert self.indicator_params is not None, "indicator_params is not set"
#         assert self.check_field is not None, "check_field is not set"

#         # Access the underlying DataFrame from self.data
#         data_series = self.data.df[self.check_field]

#         # Debug: Print the first few values of the input data
#         # print("Input data for indicator computation:")
#         # print(data_series.head())

#         # Compute the indicator
#         indicator_series = self.indicator_func(data_series, **self.indicator_params)
        
#         # Debug: Check the output of the indicator
#         # print("Computed indicator values (first 5 rows):")
#         # print(indicator_series.head() if indicator_series is not None else "Indicator computation returned None")

#         # Check if indicator_series is valid
#         if indicator_series is not None and len(indicator_series) == len(self.data.df):
#             # Convert to numpy array and assign to self.indicator
#             self.indicator = self.I(lambda: indicator_series.to_numpy())
#         else:
#             # If the length doesn't match or computation failed, raise an error with details
#             raise ValueError("Indicator computation failed or resulted in incorrect length.")
        
#         print(f"threshold: {self.threshold}")
    
#     def next(self):
#         """
#         Execute buy/sell signals based on provided conditions.
#         """
#         # Check buy condition
#         if self.indicator[-1] > self.threshold:
#             self.buy()
                
#         if self.indicator[-1] < self.threshold:
#             self.sell()


# class DynamicBacktest:
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

#     def run_backtest(self, indicator_func, indicator_params, parameter, check_field):
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
#         bt = Backtest(self.data, DynamicStrategy, cash=self.cash, commission=self.commission)        
#         # Run the backtest and pass parameters
#         stats = bt.run(
#             indicator_func=indicator_func,
#             indicator_params=indicator_params,
#             check_field=check_field,
#             threshold=threshold
#         )

#         return stats


# def standardize_columns(df):
#     """
#     Ensures that the DataFrame has columns named 'Open', 'High', 'Low', 'Close', and 'Volume'.
#     If the columns are lowercase or differently named, they will be renamed accordingly.
#     """
#     # Define expected column mappings for both lowercase and uppercase
#     expected_columns = {
#         'open': 'Open',
#         'high': 'High',
#         'low': 'Low',
#         'close': 'Close',
#         'volume': 'Volume'
#     }
    
#     # Create a mapping for renaming based on the existing columns in df
#     rename_columns = {col: expected_columns[col.lower()] for col in df.columns if col.lower() in expected_columns}
    
#     # Rename the columns to match the expected format
#     df = df.rename(columns=rename_columns)
    
#     # Verify if required columns are present after renaming
#     missing_columns = [col for col in ['Open', 'High', 'Low', 'Close'] if col not in df.columns]
#     if missing_columns:
#         raise ValueError(f"Data is missing required columns: {missing_columns}")

#     return df

# # Load data
# data = pd.read_csv("./data/usa/processed.csv")
# df = standardize_columns(data)

# parameter = 14  # Central parameter for generating thresholds
# # Indicator parameters, e.g., length for RSI
# indicator_params = {'length': 14}

# # Initialize and run the dynamic backtest with random conditions around a parameter
# dynamic_backtest = DynamicBacktest(df)
# stats = dynamic_backtest.run_backtest(ta.rsi, indicator_params, parameter, "Close")

# # Print the performance statistics
# print(stats)


# import random
# import pandas as pd
# import pandas_ta as ta
# from backtesting import Backtest, Strategy

# class DynamicIndicatorStrategy(Strategy):
#     def __init__(self, indicator_func, buy_condition, sell_condition):
#         """
#         Initialize the dynamic strategy with a single indicator and conditions.

#         Parameters:
#         - indicator_func: A function that computes the indicator on the data.
#         - buy_condition: A lambda function that returns True when the buy condition is met.
#         - sell_condition: A lambda function that returns True when the sell condition is met.
#         """
#         self.buy_condition = buy_condition
#         self.sell_condition = sell_condition
#         self.indicator_func = indicator_func

#     def init(self):
#         """
#         Initialize the indicator dynamically using the provided pandas-ta function.
#         """
#         # Compute the indicator using the pandas-ta function and store it
#         self.indicator = self.I(self.indicator_func, self.data.Close)
    
#     def next(self):
#         """
#         Execute buy/sell signals based on provided conditions.
#         """
#         # Check buy condition
#         if self.buy_condition(self.indicator):
#             self.buy()

#         # Check sell condition
#         elif self.sell_condition(self.indicator):
#             self.sell()

# class DynamicBacktest:
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
    
#     def generate_random_conditions(self, indicator_name):
#         """
#         Generate random buy and sell conditions for the indicator.

#         Parameters:
#         - indicator_name: Name of the indicator (e.g., 'RSI') for labeling.

#         Returns:
#         - buy_condition: A lambda function for the buy condition.
#         - sell_condition: A lambda function for the sell condition.
#         """
#         # Random threshold values for buy/sell
#         buy_threshold = random.randint(20, 40)
#         sell_threshold = random.randint(60, 80)

#         # Random operators
#         buy_operator = random.choice(['<', '>'])
#         sell_operator = random.choice(['<', '>'])

#         # Create lambda functions with dynamic operators
#         buy_condition = (
#             lambda indicator: eval(f"indicator[-1] {buy_operator} {buy_threshold}")
#         )
#         sell_condition = (
#             lambda indicator: eval(f"indicator[-1] {sell_operator} {sell_threshold}")
#         )

#         print(f"{indicator_name} Buy Condition: indicator[-1] {buy_operator} {buy_threshold}")
#         print(f"{indicator_name} Sell Condition: indicator[-1] {sell_operator} {sell_threshold}")
        
#         return buy_condition, sell_condition

#     def run_backtest(self, indicator_func, indicator_name="Indicator"):
#         """
#         Run the backtest with a single indicator and random buy/sell conditions.

#         Parameters:
#         - indicator_func: A pandas-ta function to compute the indicator.
#         - indicator_name: Name of the indicator for labeling (optional).
        
#         Returns:
#         - stats: Performance statistics of the backtest.
#         """
#         # Generate random buy and sell conditions
#         buy_condition, sell_condition = self.generate_random_conditions(indicator_name)
        
#         # Define the strategy dynamically by setting its parameters
#         strategy = lambda: DynamicIndicatorStrategy(indicator_func, buy_condition, sell_condition)
        
#         # Initialize the Backtest instance
#         bt = Backtest(self.data, strategy, cash=self.cash, commission=self.commission)
        
#         # Run the backtest
#         stats = bt.run()
#         # bt.plot()
        
#         return stats

# # Example usage
# # Load historical data
# data = pd.DataFrame({
#     'Open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
#     'High': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
#     'Low': [99, 98, 97, 96, 95, 94, 93, 92, 91, 90],
#     'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
# }, index=pd.date_range(start='2022-01-01', periods=10))

# # Define a custom pandas-ta indicator function (e.g., RSI)
# def rsi_indicator(close):
#     return ta.rsi(close, length=14)

# # Initialize and run the dynamic backtest with random conditions
# dynamic_backtest = DynamicBacktest(data)
# stats = dynamic_backtest.run_backtest(rsi_indicator, indicator_name="RSI")

# # Print the performance statistics
# print(stats)
