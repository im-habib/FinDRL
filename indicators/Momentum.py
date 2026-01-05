import inspect
import itertools
import pandas as pd
import pandas_ta as ta

class MomentumIndicators:
    """
    A class to calculate all momentum indicators in pandas_ta dynamically.
    Automatically handles required arguments based on function signatures.
    """
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.results = []
        self.method_info = {}
        self.indicators = ta.Category["momentum"]  # Retrieve all momentum indicators

    def generate_parameters(self, func):
        """
        Generate parameter ranges dynamically for the given function based on its signature.
        """
        signature = inspect.signature(func)
        parameters = signature.parameters
        param_ranges = {}

        for param_name, param in parameters.items():
            if param_name == "self":
                continue  # Skip 'self' parameter
            # Define parameter ranges for common arguments
            if param_name == "period":
                param_ranges[param_name] = range(5, 100, 5)
            elif param_name == "fast":
                param_ranges[param_name] = range(10, 100, 2)
            elif param_name == "slow":
                param_ranges[param_name] = range(20, 100, 5)
            elif param_name == "signal":
                param_ranges[param_name] = range(5, 100, 2)
            elif param_name == "k":
                param_ranges[param_name] = range(10, 100, 2)
            elif param_name == "d":
                param_ranges[param_name] = range(2, 100, 1)
            else:
                param_ranges[param_name] = [None]  # Default for unexpected parameters

        return param_ranges

    def calculate(self):
        """
        Calculate all momentum indicators dynamically with proper arguments.
        """
        new_columns = {}  # Store new columns in a dictionary for efficient concatenation

        for indicator in self.indicators:
            try:
                # Get the function reference from pandas_ta
                func = getattr(ta, indicator, None)
                if not func:
                    print(f"Skipping {indicator}: Function not found in pandas_ta.")
                    continue

                # Generate parameter ranges
                param_ranges = self.generate_parameters(func)
                param_keys = list(param_ranges.keys())
                param_values = list(param_ranges.values())

                # Create all combinations of parameters
                combinations = list(itertools.product(*param_values))

                # Identify required arguments
                required_params = inspect.signature(func).parameters.keys()
                required_args = {
                    "high": self.dataframe.get("high"),
                    "low": self.dataframe.get("low"),
                    "close": self.dataframe.get("close"),
                    "open_": self.dataframe.get("open"),
                    "volume": self.dataframe.get("volume"),
                }

                # Filter only available required arguments
                args = {k: v for k, v in required_args.items() if k in required_params}

                # Calculate the indicator for each combination of parameters
                for combo in combinations:
                    params = dict(zip(param_keys, combo))
                    params.update(args)  # Add required arguments
                    params = {k: v for k, v in params.items() if v is not None}  # Remove None params

                    result = func(**params)

                    # Store results in the dictionary
                    if isinstance(result, pd.Series):
                        column_name = f"{indicator}_{'_'.join([f'{k}_{v}' for k, v in params.items() if k not in args])}"
                        new_columns[column_name] = result
                    elif isinstance(result, pd.DataFrame):
                        for col in result.columns:
                            column_name = f"{indicator}_{col}_{'_'.join([f'{k}_{v}' for k, v in params.items() if k not in args])}"
                            new_columns[column_name] = result[col]

            except Exception as e:
                self.results.append({"indicator": indicator, "error": str(e)})
                print(f"Error calculating {indicator}: {e}")

        # Concatenate all new columns to the original DataFrame at once
        new_data = pd.DataFrame(new_columns, index=self.dataframe.index)
        self.dataframe = pd.concat([self.dataframe, new_data], axis=1)

        return self.dataframe

# class MomentumIndicators:
#     """
#     A class to calculate all momentum indicators in pandas_ta dynamically.
#     Automatically handles required arguments based on function signatures.
#     """
#     def __init__(self, dataframe):
#         self.dataframe = dataframe
#         self.results = []
#         self.method_info = {}
#         self.indicators = ta.Category["momentum"]  # Retrieve all momentum indicators

#     def generate_parameters(self, func):
#         """
#         Generate parameter ranges dynamically for the given function based on its signature.
#         """
#         signature = inspect.signature(func)
#         parameters = signature.parameters
#         param_ranges = {}

#         for param_name, param in parameters.items():
#             if param_name == "self":
#                 continue  # Skip 'self' parameter

#             # Define parameter ranges for common arguments
#             if param_name == "period":
#                 param_ranges[param_name] = range(5, 31, 5)
#             elif param_name == "fast":
#                 param_ranges[param_name] = range(10, 20, 2)
#             elif param_name == "slow":
#                 param_ranges[param_name] = range(20, 40, 5)
#             elif param_name == "signal":
#                 param_ranges[param_name] = range(5, 15, 2)
#             elif param_name == "k":
#                 param_ranges[param_name] = range(10, 20, 2)
#             elif param_name == "d":
#                 param_ranges[param_name] = range(2, 8, 1)
#             else:
#                 param_ranges[param_name] = [None]  # Default for unexpected parameters

#         return param_ranges

#     def calculate(self):
#         """
#         Calculate all momentum indicators dynamically with proper arguments.
#         """
#         new_columns = {}  # Store new columns in a dictionary for efficient concatenation

#         for indicator in self.indicators:
#             try:
#                 # Get the function reference from pandas_ta
#                 func = getattr(ta, indicator, None)
#                 if not func:
#                     print(f"Skipping {indicator}: Function not found in pandas_ta.")
#                     continue

#                 # Generate parameter ranges
#                 param_ranges = self.generate_parameters(func)
#                 param_keys = list(param_ranges.keys())
#                 param_values = list(param_ranges.values())

#                 # Create all combinations of parameters
#                 combinations = list(itertools.product(*param_values))

#                 # Identify required arguments
#                 required_params = inspect.signature(func).parameters.keys()
#                 required_args = {
#                     "high": self.dataframe.get("high"),
#                     "low": self.dataframe.get("low"),
#                     "close": self.dataframe.get("close"),
#                     "open_": self.dataframe.get("open"),
#                     "volume": self.dataframe.get("volume"),
#                 }

#                 # Filter only available required arguments
#                 args = {k: v for k, v in required_args.items() if k in required_params}

#                 # Calculate the indicator for each combination of parameters
#                 for combo in combinations:
#                     params = dict(zip(param_keys, combo))
#                     params.update(args)  # Add required arguments
#                     params = {k: v for k, v in params.items() if v is not None}  # Remove None params

#                     result = func(**params)

#                     # Store results in the dictionary
#                     if isinstance(result, pd.Series):
#                         column_name = f"{indicator}_{'_'.join([f'{k}_{v}' for k, v in params.items() if k not in args])}"
#                         new_columns[column_name] = result
#                     elif isinstance(result, pd.DataFrame):
#                         for col in result.columns:
#                             column_name = f"{indicator}_{col}_{'_'.join([f'{k}_{v}' for k, v in params.items() if k not in args])}"
#                             new_columns[column_name] = result[col]

#             except Exception as e:
#                 self.results.append({"indicator": indicator, "error": str(e)})
#                 print(f"Error calculating {indicator}: {e}")

#         # Concatenate all new columns to the original DataFrame at once
#         new_data = pd.DataFrame(new_columns, index=self.dataframe.index)
#         # self.dataframe = pd.concat([self.dataframe, new_data], axis=1)

#         return new_data


# import pandas_ta as ta
# from utils.Utils import hoc_print
# from indicators.base import Indicator
# from backtest.Backtest import Backtesting

# class MomentumIndicators(Indicator):
#     # def __init__(self):
#     #     print(f"MomentumIndicators Data: {self.data.head(5)}")

#     def rsi(self, length=1):
#         rsi =  ta.rsi(close=self.data[self.check_field], length=length)
#         # self.temporarily_columns[f"rsi_{length}"] =  ta.rsi(close=self.data[self.check_field], length=length)
#         # self.data[f'rsi_{window}'] = rsi
#         # return ta.momentum(close=self.data['close'], window=window).rsi()
#         # hoc_print(rsi, f"RSI {length}")
#         # Initialize and run the dynamic backtest with random conditions around a parameter
#         dynamic_backtest = Backtesting(self.data)

#         stats = dynamic_backtest.run_backtest(indicator_series=rsi, parameter=length)

#         # # # Print the performance statistics
#         hoc_print(stats, f"RSI {length}")
# ta.macd
    # def calculate_stochastic_oscillator(self, k=1, d=1):
    #             # Ensure unique column name
    #     column_name = f"stoch_{k}_{d}"
        
    #     if column_name in self.temporarily_columns:
    #         print(f"Column {column_name} already exists. Skipping calculation.")
    #         return
    #     # self.temporarily_columns[f"stoch_{k}_{d}"] = ta.stoch(high=self.data['high'], low=self.data['low'], close=self.data['close'], k=k, d=d) 
        
    #     # Calculate stochastic oscillator and add it as a new column
    #     stoch_values = ta.stoch(
    #         high=self.data['high'],
    #         low=self.data['low'],
    #         close=self.data['close'],
    #         k=k,
    #         d=d
    #     )
    #     parameter = rd.randint(k, d)

    #     # Initialize and run the dynamic backtest with random conditions around a parameter
    #     dynamic_backtest = DynamicBacktest(self.data)
    #     stats = dynamic_backtest.run_backtest(stoch_values, parameter)

    #     # # Print the performance statistics
    #     hoc_print(stats, column_name)


        # Add to temporarily_columns dictionary
        # self.temporarily_columns[column_name] = stoch_values

        # hoc_print(stoch, f"STOCH ( k={k} d={d} ) indicator calculated.")
        
        # StochasticOscillator(
        #     high=self.data['high'], low=self.data['low'], close=self.data['close'], window=window, smooth_window=smooth_window)
        # return stoch.stoch(), stoch.stoch_signal()
    
    # def calculate_stochastic_oscillator(self, window=14, smooth_window=3):
    #   stoch = pta.stoch(
    #       high=self.data['high'], 
    #       low=self.data['low'], 
    #       close=self.data['close'], 
    #       k=window, 
    #       d=smooth_window
    #   )

    #   hoc_print(stoch)
      # return stoch['STOCHk_14_3_3'], stoch['STOCHd_14_3_3']

    # def calculate_macd(self, fast=12, slow=26, signal=9):
    #     macd = ta.trend.MACD(close=self.data['Close'], window_slow=slow, window_fast=fast, window_sign=signal)
    #     return macd.macd(), macd.macd_signal(), macd.macd_diff()
    
    # def calculate_cci(self, window=20):
    #     return ta.trend.CCIIndicator(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window=window).cci()
    
    # def calculate_roc(self, window=12):
    #     return ta.momentum.ROCIndicator(close=self.data['Close'], window=window).roc()
    
    # def calculate_williams_r(self, window=14):
    #     return ta.momentum.WilliamsRIndicator(
    #         high=self.data['High'], low=self.data['Low'], close=self.data['Close'], lbp=window).wr()
    
    # def calculate_momentum(self, window=10):
    #     return ta.momentum.MomentumIndicator(close=self.data['Close'], window=window).momentum()
    
    # def calculate_awesome_oscillator(self, fast=5, slow=34):
    #     return ta.momentum.AwesomeOscillatorIndicator(
    #         high=self.data['High'], low=self.data['Low'], window1=fast, window2=slow).awesome_oscillator()
    
    # def calculate_rvi(self, window=10):
    #     rvi = ta.momentum.RelativeVigorIndex(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window=window)
    #     return rvi.rvi(), rvi.rvi_signal()
    
    # def calculate_mfi(self, window=14):
    #     return ta.volume.MFIIndicator(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], volume=self.data['Volume'], window=window).money_flow_index()
    
    # def calculate_cmo(self, window=14):
    #     return ta.momentum.ChandeMomentumOscillator(close=self.data['Close'], window=window).cmo()
    
    # def calculate_tsi(self, slow=25, fast=13):
    #     return ta.momentum.TSIIndicator(close=self.data['Close'], window_slow=slow, window_fast=fast).tsi()
    
    # def calculate_elder_ray(self, window=13):
    #     return ta.trend.EMAIndicator(close=self.data['Close'], window=window).ema_indicator() - self.data['Low'], ta.trend.EMAIndicator(close=self.data['Close'], window=window).ema_indicator() - self.data['High']
    
    # def calculate_ultimate_oscillator(self, short=7, medium=14, long=28):
    #     return ta.momentum.UltimateOscillator(
    #         high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window1=short, window2=medium, window3=long).ultimate_oscillator()
    
    # def calculate_force_index(self, window=13):
    #     return ta.volume.ForceIndexIndicator(close=self.data['Close'], volume=self.data['Volume'], window=window).force_index()
    
    # def calculate_ppo(self, fast=12, slow=26):
    #     ppo = ta.momentum.PercentagePriceOscillator(close=self.data['Close'], window_fast=fast, window_slow=slow)
    #     return ppo.ppo(), ppo.ppo_signal(), ppo.ppo_hist()
    
    # def calculate_dmi(self, window=14):
    #     dmi = ta.trend.ADXIndicator(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window=window)
    #     return dmi.adx(), dmi.adx_pos(), dmi.adx_neg()
    
    # def calculate_kvo(self, fast=34, slow=55):
    #     kvo = ta.volume.KlingerVolumeOscillator(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], volume=self.data['Volume'], window_fast=fast, window_slow=slow)
    #     return kvo.kvo(), kvo.kvo_signal()
    
    # def calculate_mass_index(self, fast=9, slow=25):
    #     return ta.trend.MassIndex(high=self.data['High'], low=self.data['Low'], window_fast=fast, window_slow=slow).mass_index()
    
    # def calculate_trix(self, window=15):
    #     return ta.trend.TRIXIndicator(close=self.data['Close'], window=window).trix()
    
    # def calculate_dpo(self, window=20):
    #     return ta.trend.DPOIndicator(close=self.data['Close'], window=window).dpo()
    
    # def calculate_vortex(self, window=14):
    #     vortex = ta.trend.VortexIndicator(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window=window)
    #     return vortex.vortex_indicator_pos(), vortex.vortex_indicator_neg()
    
    # def calculate_tema(self, window=9):
    #     return ta.trend.TEMAIndicator(close=self.data['Close'], window=window).tema()
    
    # def calculate_obv(self):
    #     return ta.volume.OnBalanceVolumeIndicator(close=self.data['Close'], volume=self.data['Volume']).on_balance_volume()
    
    # def calculate_adi(self):
    #     return ta.volume.AccDistIndexIndicator(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], volume=self.data['Volume']).acc_dist_index()


    # def relative_strength_index(self, period=14):
    #     rsi = ta.momentum.rsi(close=self.data['Close'], window=period)
    #     return rsi

    # def moving_average_convergence_divergence(self, slow=26, fast=12, signal=9):
    #     macd = ta.trend.macd(close=self.data['Close'], window_slow=slow, window_fast=fast, window_sign=signal)
    #     return macd, ta.trend.macd_signal(close=self.data['Close'], window_slow=slow, window_fast=fast, window_sign=signal)

    # def rate_of_change(self, period=12):
    #     roc = ta.momentum.roc(close=self.data['Close'], window=period)
    #     return roc

    # def stochastic_oscillator(self, period=14):
    #     stoch = ta.momentum.stoch(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window=period)
    #     return stoch

    # def commodity_channel_index(self, period=20):
    #     cci = ta.trend.cci(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window=period)
    #     return cci

    # # def momentum_indicator(self, period=10):
    # #     mom = ta.momentum.momentum(close=self.data['Close'], window=period)
    # #     return mom

    # def williams_r(self, period=14):
    #     willr = ta.momentum.williams_r(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], lbp=period)
    #     return willr

    # def ultimate_oscillator(self, period1=7, period2=14, period3=28):
    #     ult_osc = ta.momentum.ultimate_oscillator(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window1=period1, window2=period2, window3=period3)
    #     return ult_osc

    # def percentage_price_oscillator(self, fast=12, slow=26):
    #     ppo = ta.momentum.ppo(close=self.data['Close'], window_slow=slow, window_fast=fast)
    #     return ppo

    # def detrended_price_oscillator(self, period=14):
    #     dpo = ta.trend.dpo(close=self.data['Close'], window=period)
    #     return dpo

    # def true_strength_index(self, r=25, s=13):
    #     tsi = ta.momentum.tsi(close=self.data['Close'], window_slow=r, window_fast=s)
    #     return tsi

    # def stochastic_rsi(self, period=14):
    #     stoch_rsi = ta.momentum.stochrsi(close=self.data['Close'], window=period)
    #     return stoch_rsi

    # def aroon_indicator(self, period=25):
    #     aroon_up = ta.trend.aroon_up(high=self.data['High'], low=self.data['Low'], window=period)
    #     aroon_down = ta.trend.aroon_down(high=self.data['High'], low=self.data['Low'], window=period)
    #     return aroon_up, aroon_down

    # def elders_force_index(self, period=13):
    #     efi = ta.volume.force_index(close=self.data['Close'], volume=self.data['Volume'], window=period)
    #     return efi

    # def qstick_indicator(self, period=10):
    #     qstick = (self.data['Close'] - self.data['Open']).rolling(window=period).mean()
    #     return qstick

    # def chaikin_money_flow(self, period=20):
    #     cmf = ta.volume.chaikin_money_flow(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], volume=self.data['Volume'], window=period)
    #     return cmf

    # def ease_of_movement(self, period=14):
    #     eom = ta.volume.ease_of_movement(high=self.data['High'], low=self.data['Low'], volume=self.data['Volume'], window=period)
    #     return eom

    # def acc_dist_index(self):
    #     adi = ta.volume.acc_dist_index(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], volume=self.data['Volume'])
    #     return adi

    # def on_balance_volume(self):
    #     obv = ta.volume.on_balance_volume(close=self.data['Close'], volume=self.data['Volume'])
    #     return obv

    # def volatility_chaikin(self, period=10):
    #     chaikin_volatility = ta.volatility.chaikin_volatility(high=self.data['High'], low=self.data['Low'], window=period)
    #     return chaikin_volatility

    # def bollinger_bands(self, period=20, std_dev=2):
    #     bollinger = ta.volatility.bollinger_hband_indicator(close=self.data['Close'], window=period, window_dev=std_dev)
    #     return bollinger

    # def average_true_range(self, period=14):
    #     atr = ta.volatility.average_true_range(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window=period)
    #     return atr


# import ta
# import inspect

# class MomentumIndicators:
#     def __init__(self, data):
#         self.data = data
#         print("Initialized MomentumIndicators")

#                 # Dynamically generate the list of available indicators
#         self.available_indicators = [
#             name for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
#             if name not in ['__init__', 'get_indicator', 'call_indicator', 'list_indicators']
#         ]

#     def get_indicator(self, indicator_name):
#         indicator_method = getattr(self, indicator_name)
#         if indicator_method:
#             return indicator_method
#         else:
#             raise ValueError(f"Indicator {indicator_name} is not implemented")
        
#     def call_indicator(self, indicator, **kwargs):
#         if callable(indicator):
#             return indicator(**kwargs)
#         else:
#             raise ValueError(f"Indicator {indicator} is not implemented")
        
#     def list_indicators(self):
#         return self.available_indicators

#     def relative_strength_index(self, period=14):
#         rsi = ta.momentum.RSIIndicator(close=self.data['Close'], window=period).rsi()
#         return rsi

#     def moving_average_convergence_divergence(self, slow=26, fast=12, signal=9):
#         macd = ta.trend.MACD(close=self.data['Close'], window_slow=slow, window_fast=fast, window_sign=signal)
#         return macd.macd(), macd.macd_signal()

#     def rate_of_change(self, period=12):
#         roc = ta.momentum.ROCIndicator(close=self.data['Close'], window=period).roc()
#         return roc

#     def stochastic_oscillator(self, period=14):
#         stoch = ta.momentum.StochasticOscillator(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window=period)
#         return stoch.stoch()

#     def commodity_channel_index(self, period=20):
#         cci = ta.trend.CCIIndicator(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window=period)
#         return cci.cci()

#     def momentum_indicator(self, period=10):
#         mom = ta.momentum.MomentumIndicator(close=self.data['Close'], window=period)
#         return mom.momentum()

#     def williams_r(self, period=14):
#         willr = ta.momentum.WilliamsRIndicator(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], lbp=period)
#         return willr.williams_r()

#     def chande_momentum_oscillator(self, period=14):
#         cmo = ta.momentum.CMOIndicator(close=self.data['Close'], window=period)
#         return cmo.cmo()

#     def ultimate_oscillator(self, period1=7, period2=14, period3=28):
#         ult_osc = ta.momentum.UltimateOscillator(high=self.data['High'], low=self.data['Low'], close=self.data['Close'], window1=period1, window2=period2, window3=period3)
#         return ult_osc.ultimate_oscillator()

#     def price_rate_of_change(self, period=12):
#         proc = ta.momentum.ROCIndicator(close=self.data['Close'], window=period).roc()
#         return proc

#     def percentage_price_oscillator(self, fast=12, slow=26):
#         ppo = ta.momentum.PercentagePriceOscillator(close=self.data['Close'], window_slow=slow, window_fast=fast).ppo()
#         return ppo

#     def detrended_price_oscillator(self, period=14):
#         dpo = ta.trend.DPOIndicator(close=self.data['Close'], window=period).dpo()
#         return dpo

#     def true_strength_index(self, r=25, s=13):
#         tsi = ta.momentum.TSIIndicator(close=self.data['Close'], window_slow=r, window_fast=s).tsi()
#         return tsi

#     def connors_rsi(self, period_rsi=3, period_streak=2, period_rank=100):
#         rsi = ta.momentum.RSIIndicator(close=self.data['Close'], window=period_rsi).rsi()
#         streak = self.data['Close'].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)).rolling(window=period_streak).sum()
#         up_down_rsi = ta.momentum.RSIIndicator(close=streak, window=period_streak).rsi()
#         pct_rank = self.data['Close'].rank(pct=True) * 100
#         connors_rsi = (rsi + up_down_rsi + pct_rank) / 3
#         return connors_rsi

#     def intraday_momentum_index(self, period=14):
#         diff = self.data['Close'] - self.data['Open']
#         up_days = (diff.where(diff > 0, 0)).rolling(window=period).sum()
#         down_days = (-diff.where(diff < 0, 0)).rolling(window=period).sum()
#         imi = 100 * (up_days / (up_days + down_days))
#         return imi

#     def stochastic_rsi(self, period=14):
#         rsi = ta.momentum.RSIIndicator(close=self.data['Close'], window=period).rsi()
#         stoch_rsi = (rsi - rsi.rolling(window=period).min()) / (rsi.rolling(window=period).max() - rsi.rolling(window=period).min())
#         return stoch_rsi

#     def aroon_indicator(self, period=25):
#         aroon = ta.trend.AroonIndicator(high=self.data['High'], low=self.data['Low'], window=period)
#         return aroon.aroon_up(), aroon.aroon_down()

#     def elders_force_index(self, period=13):
#         efi = ta.volume.ForceIndexIndicator(close=self.data['Close'], volume=self.data['Volume'], window=period).force_index()
#         return efi

#     def qstick_indicator(self, period=10):
#         qstick = (self.data['Close'] - self.data['Open']).rolling(window=period).mean()
#         return qstick


# import numpy as np
# import pandas as pd
# # from backtesting import Backtest, Strategy
# from app.parameters.Parameters import hoc_print

# # Momentum Indicators
# class MomentumIndicators:
#     def __init__(self, data):
#         self.data = data
#         print("Initialized MomentumIndicators")
#         hoc_print(self.data.head(10), "Data Start")

#         self.available_indicators = [
#             'williams_r',
#             'connors_rsi',
#             'rate_of_change',
#             'stochastic_rsi',
#             'aroon_indicator',
#             'qstick_indicator',
#             'momentum_indicator',
#             'elders_force_index',
#             'ultimate_oscillator',
#             'true_strength_index',
#             'price_rate_of_change',
#             'stochastic_oscillator',
#             'relative_strength_index', 
#             'relative_momentum_index',
#             'commodity_channel_index',
#             'intraday_momentum_index',
#             'chande_momentum_oscillator',
#             'detrended_price_oscillator',
#             'percentage_price_oscillator',
#             'moving_average_convergence_divergence'
#         ]

#     def get_indicator(self, indicator_name):
#         indicator_method = getattr(self, indicator_name)
#         if indicator_method:
#             return indicator_method
#         else:
#             raise ValueError(f"Indicator {indicator_name} is not implemented")
        
#     def call_indicator(self, indicator, **kwargs):
#         if callable(indicator):
#             return indicator(**kwargs)
#         else:
#             raise ValueError(f"Indicator {indicator} is not implemented")
        
#     def list_indicators(self):
#         return self.available_indicators

#     def relative_strength_index(self, period=14):
#         delta = self.data['Close'].diff()
#         gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
#         loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
#         rs = gain / loss
#         rsi = 100 - (100 / (1 + rs))
#         return rsi

#     def moving_average_convergence_divergence(self, slow=26, fast=12, signal=9):
#         ema_fast = self.data['Close'].ewm(span=fast, min_periods=fast).mean()
#         ema_slow = self.data['Close'].ewm(span=slow, min_periods=slow).mean()
#         macd = ema_fast - ema_slow
#         signal_line = macd.ewm(span=signal, min_periods=signal).mean()
#         return macd, signal_line

#     def rate_of_change(self, period=12):
#         roc = ((self.data['Close'] - self.data['Close'].shift(period)) / self.data['Close'].shift(period)) * 100
#         return roc

#     def stochastic_oscillator(self, period=14):
#         low_min = self.data['Low'].rolling(window=period).min()
#         high_max = self.data['High'].rolling(window=period).max()
#         stoch = ((self.data['Close'] - low_min) / (high_max - low_min)) * 100
#         return stoch

#     def commodity_channel_index(self, period=20):
#         typical_price = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
#         sma = typical_price.rolling(window=period).mean()
#         mean_dev = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
#         cci = (typical_price - sma) / (0.015 * mean_dev)
#         return cci

#     def momentum_indicator(self, period=10):
#         momentum = self.data['Close'].diff(periods=period)
#         return momentum

#     def williams_r(self, period=14):
#         high_max = self.data['High'].rolling(window=period).max()
#         low_min = self.data['Low'].rolling(window=period).min()
#         will_r = ((high_max - self.data['Close']) / (high_max - low_min)) * -100
#         return will_r

#     def chande_momentum_oscillator(self, period=14):
#         delta = self.data['Close'].diff()
#         gain = (delta.where(delta > 0, 0)).rolling(window=period).sum()
#         loss = (-delta.where(delta < 0, 0)).rolling(window=period).sum()
#         cmo = ((gain - loss) / (gain + loss)) * 100
#         return cmo

#     def ultimate_oscillator(self, period1=7, period2=14, period3=28):
#         high_low = self.data['High'] - self.data['Low']
#         high_close = np.abs(self.data['High'] - self.data['Close'].shift(1))
#         low_close = np.abs(self.data['Low'] - self.data['Close'].shift(1))
#         true_range = high_low.combine(high_close, np.maximum).combine(low_close, np.maximum)
#         avg1 = true_range.rolling(window=period1).mean()
#         avg2 = true_range.rolling(window=period2).mean()
#         avg3 = true_range.rolling(window=period3).mean()
#         buying_pressure = self.data['Close'] - np.minimum(self.data['Low'], self.data['Close'].shift(1))
#         bp_avg1 = buying_pressure.rolling(window=period1).mean()
#         bp_avg2 = buying_pressure.rolling(window=period2).mean()
#         bp_avg3 = buying_pressure.rolling(window=period3).mean()
#         ult_osc = 100 * (4 * bp_avg1 + 2 * bp_avg2 + bp_avg3) / (4 * avg1 + 2 * avg2 + avg3)
#         return ult_osc

#     def price_rate_of_change(self, period=12):
#         proc = ((self.data['Close'] - self.data['Close'].shift(period)) / self.data['Close'].shift(period)) * 100
#         return proc

#     def percentage_price_oscillator(self, fast=12, slow=26):
#         ema_fast = self.data['Close'].ewm(span=fast, min_periods=fast).mean()
#         ema_slow = self.data['Close'].ewm(span=slow, min_periods=slow).mean()
#         ppo = (ema_fast - ema_slow) / ema_slow * 100
#         return ppo

#     def detrended_price_oscillator(self, period=14):
#         sma = self.data['Close'].rolling(window=int(period/2 + 1)).mean()
#         dpo = self.data['Close'] - sma
#         return dpo

#     def true_strength_index(self, r=25, s=13):
#         diff = self.data['Close'].diff()
#         abs_diff = np.abs(diff)
#         smoothed_pc = diff.ewm(span=r, min_periods=r).mean().ewm(span=s, min_periods=s).mean()
#         smoothed_abs_pc = abs_diff.ewm(span=r, min_periods=r).mean().ewm(span=s, min_periods=s).mean()
#         tsi = 100 * (smoothed_pc / smoothed_abs_pc)
#         return tsi

#     def relative_momentum_index(self, period=14):
#         momentum = self.data['Close'].diff(period)
#         return self.relative_strength_index(momentum, period=period)

#     def connors_rsi(self, period_rsi=3, period_streak=2, period_rank=100):
#         rsi = self.relative_strength_index(period=period_rsi)
#         streak = self.data['Close'].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)).rolling(window=period_streak).sum()
#         up_down_rsi = self.relative_strength_index(streak, period=period_streak)
#         pct_rank = self.data['Close'].rank(pct=True) * 100
#         connors_rsi = (rsi + up_down_rsi + pct_rank) / 3
#         return connors_rsi

#     def intraday_momentum_index(self, period=14):
#         diff = self.data['Close'] - self.data['Open']
#         up_days = (diff.where(diff > 0, 0)).rolling(window=period).sum()
#         down_days = (-diff.where(diff < 0, 0)).rolling(window=period).sum()
#         imi = 100 * (up_days / (up_days + down_days))
#         return imi

#     def stochastic_rsi(self, period=14):
#         rsi = self.relative_strength_index(period=period)
#         stoch_rsi = (rsi - rsi.rolling(window=period).min()) / (rsi.rolling(window=period).max() - rsi.rolling(window=period).min())
#         return stoch_rsi

#     def aroon_indicator(self, period=25):
#         aroon_up = (period - self.data['Close'].rolling(window=period).apply(lambda x: period - np.argmax(x))) / period * 100
#         aroon_down = (period - self.data['Close'].rolling(window=period).apply(lambda x: period - np.argmin(x))) / period * 100
#         return aroon_up, aroon_down

#     def elders_force_index(self, period=13):
#         efi = self.data['Volume'] * (self.data['Close'] - self.data['Close'].shift(1))
#         efi_sma = efi.rolling(window=period).mean()
#         return efi_sma

#     def qstick_indicator(self, period=10):
#         qstick = (self.data['Close'] - self.data['Open']).rolling(window=period).mean()
#         return qstick


# from backtesting.test import GOOG  # For testing purposes

# class IndicatorBacktest:
#     def __init__(self, data, indicator_function, **indicator_params):
#         self.data = data
#         self.indicator_function = indicator_function
#         self.indicator_params = indicator_params

#     def run_backtest(self):
#         class IndicatorStrategy(Strategy):
#             def init(self):
#                 self.indicator = self.I(self.indicator_function, **self.indicator_params)
            
#             def next(self):
#                 if self.indicator[-1] > self.data.Close[-1]:
#                     self.buy()
#                 elif self.indicator[-1] < self.data.Close[-1]:
#                     self.sell()

#         bt = Backtest(self.data, IndicatorStrategy, cash=10_000, commission=.002)
#         stats = bt.run()
#         bt.plot()
#         return stats

# # Example usage:
# data = GOOG  # Use your own DataFrame with the specified columns

# # Make sure your DataFrame's columns are properly named and indexed by Datetime
# # Example of required columns: ['Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

# indicators = MomentumIndicators(data)

# # Running backtest for RSI
# bt_rsi = IndicatorBacktest(data, indicators.relative_strength_index, period=14)
# stats_rsi = bt_rsi.run_backtest()
# print(stats_rsi)

# # Running backtest for MACD
# bt_macd = IndicatorBacktest(data, indicators.moving_average_convergence_divergence, slow=26, fast=12, signal=9)
# stats_macd = bt_macd.run_backtest()
# print(stats_macd)













# import numpy as np
# import backtrader as bt


# class MomentumIndicators(bt.Indicator):
#     lines = (
#         'rsi', 'macd', 'macd_signal', 'roc', 'stoch', 'cci', 'will_r', 'cmo',
#         'ult_osc', 'proc', 'ppo', 'dpo', 'tsi', 'connors_rsi', 'imi', 'stoch_rsi',
#         'aroon_up', 'aroon_down', 'efi', 'qstick'
#     )
    
#     params = (
#         ('period_rsi', 14),
#         ('period_macd1', 12),
#         ('period_macd2', 26),
#         ('period_macd_signal', 9),
#         ('period_roc', 12),
#         ('period_stoch', 14),
#         ('period_cci', 20),
#         ('period_will_r', 14),
#         ('period_cmo', 14),
#         ('period1_ult', 7),
#         ('period2_ult', 14),
#         ('period3_ult', 28),
#         ('period_proc', 12),
#         ('period_ppo_fast', 12),
#         ('period_ppo_slow', 26),
#         ('period_dpo', 14),
#         ('period_tsi_r', 25),
#         ('period_tsi_s', 13),
#         ('period_rsi_connors', 3),
#         ('period_streak_connors', 2),
#         ('period_rank_connors', 100),
#         ('period_imi', 14),
#         ('period_stoch_rsi', 14),
#         ('period_aroon', 25),
#         ('period_efi', 13),
#         ('period_qstick', 10),
#     )

#     def __init__(self):
#         # Initialize all indicators with dynamic parameters
#         self.lines.rsi = self.relative_strength_index(self.data.close, self.p.period_rsi)
#         self.lines.macd, self.lines.macd_signal = self.moving_average_convergence_divergence(self.data.close, self.p.period_macd1, self.p.period_macd2, self.p.period_macd_signal)
#         self.lines.roc = self.rate_of_change(self.data.close, self.p.period_roc)
#         self.lines.stoch = self.stochastic_oscillator(self.data, self.p.period_stoch)
#         self.lines.cci = self.commodity_channel_index(self.data, self.p.period_cci)
#         self.lines.will_r = self.williams_r(self.data.high, self.data.low, self.data.close, self.p.period_will_r)
#         self.lines.cmo = self.chande_momentum_oscillator(self.data.close, self.p.period_cmo)
#         self.lines.ult_osc = self.ultimate_oscillator(self.data.high, self.data.low, self.data.close, self.p.period1_ult, self.p.period2_ult, self.p.period3_ult)
#         self.lines.proc = self.price_rate_of_change(self.data.close, self.p.period_proc)
#         self.lines.ppo = self.percentage_price_oscillator(self.data.close, self.p.period_ppo_fast, self.p.period_ppo_slow)
#         self.lines.dpo = self.detrended_price_oscillator(self.data.close, self.p.period_dpo)
#         self.lines.tsi = self.true_strength_index(self.data.close, self.p.period_tsi_r, self.p.period_tsi_s)
#         self.lines.connors_rsi = self.connors_rsi(self.data.close, self.p.period_rsi_connors, self.p.period_streak_connors, self.p.period_rank_connors)
#         self.lines.imi = self.intraday_momentum_index(self.data.open, self.data.close, self.p.period_imi)
#         self.lines.stoch_rsi = self.stochastic_rsi(self.data.close, self.p.period_stoch_rsi)
#         self.lines.aroon_up, self.lines.aroon_down = self.aroon_indicator(self.data, self.p.period_aroon)
#         self.lines.efi = self.elders_force_index(self.data.volume, self.data.close, self.p.period_efi)
#         self.lines.qstick = self.qstick_indicator(self.data.open, self.data.close, self.p.period_qstick)

#     def get_params(self):
#         return self.params

#     def relative_strength_index(self, data, period):
#         delta = data.diff()
#         gain = delta.where(delta > 0, 0).rolling(window=period).mean()
#         loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
#         rs = gain / loss
#         rsi = 100 - (100 / (1 + rs))
#         return rsi

#     def moving_average_convergence_divergence(self, data, fast, slow, signal):
#         ema_fast = data.ewm(span=fast, min_periods=fast).mean()
#         ema_slow = data.ewm(span=slow, min_periods=slow).mean()
#         macd = ema_fast - ema_slow
#         signal_line = macd.ewm(span=signal, min_periods=signal).mean()
#         return macd, signal_line

#     def rate_of_change(self, data, period):
#         roc = ((data - data.shift(period)) / data.shift(period)) * 100
#         return roc

#     def stochastic_oscillator(self, data, period):
#         low_min = data.low.rolling(window=period).min()
#         high_max = data.high.rolling(window=period).max()
#         stoch = ((data.close - low_min) / (high_max - low_min)) * 100
#         return stoch

#     def commodity_channel_index(self, data, period):
#         typical_price = (data.high + data.low + data.close) / 3
#         sma = typical_price.rolling(window=period).mean()
#         mean_dev = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
#         cci = (typical_price - sma) / (0.015 * mean_dev)
#         return cci

#     def williams_r(self, high, low, close, period):
#         high_max = high.rolling(window=period).max()
#         low_min = low.rolling(window=period).min()
#         will_r = ((high_max - close) / (high_max - low_min)) * -100
#         return will_r

#     def chande_momentum_oscillator(self, data, period):
#         delta = data.diff()
#         gain = delta.where(delta > 0, 0).rolling(window=period).sum()
#         loss = -delta.where(delta < 0, 0).rolling(window=period).sum()
#         cmo = ((gain - loss) / (gain + loss)) * 100
#         return cmo

#     def ultimate_oscillator(self, high, low, close, period1, period2, period3):
#         high_low = high - low
#         high_close = np.abs(high - close.shift(1))
#         low_close = np.abs(low - close.shift(1))
#         true_range = high_low.combine(high_close, np.maximum).combine(low_close, np.maximum)
#         avg1 = true_range.rolling(window=period1).mean()
#         avg2 = true_range.rolling(window=period2).mean()
#         avg3 = true_range.rolling(window=period3).mean()
#         buying_pressure = close - np.minimum(low, close.shift(1))
#         bp_avg1 = buying_pressure.rolling(window=period1).mean()
#         bp_avg2 = buying_pressure.rolling(window=period2).mean()
#         bp_avg3 = buying_pressure.rolling(window=period3).mean()
#         ult_osc = 100 * (4 * bp_avg1 + 2 * bp_avg2 + bp_avg3) / (4 * avg1 + 2 * avg2 + avg3)
#         return ult_osc

#     def price_rate_of_change(self, data, period):
#         proc = ((data - data.shift(period)) / data.shift(period)) * 100
#         return proc

#     def percentage_price_oscillator(self, data, fast, slow):
#         ema_fast = data.ewm(span=fast, min_periods=fast).mean()
#         ema_slow = data.ewm(span=slow, min_periods=slow).mean()
#         ppo = (ema_fast - ema_slow) / ema_slow * 100
#         return ppo

#     def detrended_price_oscillator(self, data, period):
#         sma = data.rolling(window=int(period/2 + 1)).mean()
#         dpo = data - sma
#         return dpo

#     def true_strength_index(self, data, r, s):
#         diff = data.diff()
#         abs_diff = np.abs(diff)
#         smoothed_pc = diff.ewm(span=r, min_periods=r).mean().ewm(span=s, min_periods=s).mean()
#         smoothed_abs_pc = abs_diff.ewm(span=r, min_periods=r).mean().ewm(span=s, min_periods=s).mean()
#         tsi = 100 * (smoothed_pc / smoothed_abs_pc)
#         return tsi

#     def connors_rsi(self, data, period_rsi, period_streak, period_rank):
#         rsi = self.relative_strength_index(data, period=period_rsi)
#         streak = data.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)).rolling(window=period_streak).sum()
#         up_down_rsi = self.relative_strength_index(streak, period=period_streak)
#         pct_rank = data.rank(pct=True) * 100
#         connors_rsi = (rsi + up_down_rsi + pct_rank) / 3
#         return connors_rsi

#     def intraday_momentum_index(self, open_, close, period):
#         diff = close - open_
#         up_days = (diff.where(diff > 0, 0)).rolling(window=period).sum()
#         down_days = -diff.where(diff < 0, 0).rolling(window=period).sum()
#         imi = 100 * (up_days / (up_days + down_days))
#         return imi

#     def stochastic_rsi(self, data, period):
#         rsi = self.relative_strength_index(data, period=period)
#         stoch_rsi = (rsi - rsi.rolling(window=period).min()) / (rsi.rolling(window=period).max() - rsi.rolling(window=period).min())
#         return stoch_rsi

#     def aroon_indicator(self, data, period):
#         aroon_up = (period - data.high.rolling(window=period).apply(lambda x: period - np.argmax(x))) / period * 100
#         aroon_down = (period - data.low.rolling(window=period).apply(lambda x: period - np.argmin(x))) / period * 100
#         return aroon_up, aroon_down

#     def elders_force_index(self, volume, close, period):
#         efi = volume * (close - close.shift(1))
#         efi_sma = efi.rolling(window=period).mean()
#         return efi_sma

#     def qstick_indicator(self, open_, close, period):
#         qstick = (close - open_).rolling(window=period).mean()
#         return qstick


#     def next(self):
#         print(f'RSI: {self.momentum_indicators.rsi[0]:.2f}, MACD: {self.momentum_indicators.macd[0]:.2f}, MACD Signal: {self.momentum_indicators.macd_signal[0]:.2f}')

# # Load data
# data = pd.read_csv('data.csv', parse_dates=True, index_col='Datetime')

# # Create a Backtrader Data Feed
# data_feed = bt.feeds.PandasData(dataname=data)

# # Initialize Cerebro engine
# cerebro = bt.Cerebro()

# # Add strategy to Cerebro
# cerebro.addstrategy(TestStrategy)

# # Add Data Feed to Cerebro
# cerebro.adddata(data_feed)

# # Set our desired cash start
# cerebro.broker.setcash(10000.0)

# # Add a FixedSize sizer according to the stake
# cerebro.addsizer(bt.sizers.FixedSize, stake=10)

# # Set the commission
# cerebro.broker.setcommission(commission=0.001)

# # Print out the starting conditions
# print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')

# # Run over everything
# cerebro.run()

# # Print out the final result
# print(f'Ending Portfolio Value: {cerebro.broker.getvalue():.2f}')

# # Plot the result
# cerebro.plot()



# import numpy as np

# # Momentum Indicators
# class MomentumIndicators():

#     def __init__(self, data):
#         self.data = data

#     lines = ('rsi', 'macd', 'macd_signal', 'roc', 'stoch', 'cci', 'momentum', 'will_r', 'cmo', 
#              'ult_osc', 'proc', 'ppo', 'dpo', 'tsi', 'rmi', 'connors_rsi', 'imi', 'stoch_rsi',
#              'aroon_up', 'aroon_down', 'efi', 'qstick')
    
#     # List of available indicator methods
#     available_indicators = [
#         'relative_strength_index', 
#         'moving_average_convergence_divergence',
#         'rate_of_change',
#         'stochastic_oscillator',
#         'commodity_channel_index',
#         'momentum_indicator',
#         'williams_r',
#         'chande_momentum_oscillator',
#         'ultimate_oscillator',
#         'price_rate_of_change',
#         'percentage_price_oscillator',
#         'detrended_price_oscillator',
#         'true_strength_index',
#         'relative_momentum_index',
#         'connors_rsi',
#         'intraday_momentum_index',
#         'stochastic_rsi',
#         'aroon_indicator',
#         'elders_force_index',
#         'qstick_indicator'
#     ]

#     def get_indicator(self, indicator_name):
#         indicator_method = getattr(self, indicator_name)
#         if indicator_method:
#             return indicator_method
#         else:
#             raise ValueError(f"Indicator {indicator_name} is not implemented")
        
#     def call_indicator(self, indicator, *args, **kwargs):
#         if callable(indicator):
#             return indicator(**kwargs)
#         else:
#             raise ValueError(f"Indicator {indicator} is not implemented")
        
#     def list_indicators(self):
#         return self.available_indicators



#     def relative_strength_index(self, period=14):
#         delta = self.data.diff()
#         gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
#         loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
#         rs = gain / loss
#         rsi = 100 - (100 / (1 + rs))
#         return rsi

#     def moving_average_convergence_divergence(self, slow=26, fast=12, signal=9):
#         ema_fast = self.data.ewm(span=fast, min_periods=fast).mean()
#         ema_slow = self.data.ewm(span=slow, min_periods=slow).mean()
#         macd = ema_fast - ema_slow
#         signal_line = macd.ewm(span=signal, min_periods=signal).mean()
#         return macd, signal_line

#     def rate_of_change(self, period=12):
#         roc = ((self.data - self.data.shift(period)) / self.data.shift(period)) * 100
#         return roc

#     def stochastic_oscillator(self, period=14):
#         low_min = self.data.rolling(window=period).min()
#         high_max = self.data.rolling(window=period).max()
#         stoch = ((self.data - low_min) / (high_max - low_min)) * 100
#         return stoch

#     def commodity_channel_index(self, period=20):
#         # CCI = (Typical Price - SMA of Typical Price) / (0.015 * Mean Deviation)
#         typical_price = (self['High'] + self.data['Low'] + self.data['Close']) / 3
#         sma = typical_price.rolling(window=period).mean()
#         mean_dev = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
#         cci = (typical_price - sma) / (0.015 * mean_dev)
#         return cci

#     def momentum_indicator(self, period=10):
#         momentum = self.data.diff(periods=period)
#         return momentum

#     def williams_r(self, high, low, close, period=14):
#         high_max = high.rolling(window=period).max()
#         low_min = low.rolling(window=period).min()
#         will_r = ((high_max - close) / (high_max - low_min)) * -100
#         return will_r

#     def chande_momentum_oscillator(self, period=14):
#         delta = self.data.diff()
#         gain = (delta.where(delta > 0, 0)).rolling(window=period).sum()
#         loss = (-delta.where(delta < 0, 0)).rolling(window=period).sum()
#         cmo = ((gain - loss) / (gain + loss)) * 100
#         return cmo

#     def ultimate_oscillator(self, high, low, close, period1=7, period2=14, period3=28):
#         high_low = high - low
#         high_close = np.abs(high - close.shift(1))
#         low_close = np.abs(low - close.shift(1))
#         true_range = high_low.combine(high_close, np.maximum).combine(low_close, np.maximum)
#         avg1 = true_range.rolling(window=period1).mean()
#         avg2 = true_range.rolling(window=period2).mean()
#         avg3 = true_range.rolling(window=period3).mean()
#         buying_pressure = close - np.minimum(low, close.shift(1))
#         bp_avg1 = buying_pressure.rolling(window=period1).mean()
#         bp_avg2 = buying_pressure.rolling(window=period2).mean()
#         bp_avg3 = buying_pressure.rolling(window=period3).mean()
#         ult_osc = 100 * (4 * bp_avg1 + 2 * bp_avg2 + bp_avg3) / (4 * avg1 + 2 * avg2 + avg3)
#         return ult_osc

#     def price_rate_of_change(self, period=12):
#         proc = ((self.data - self.data.shift(period)) / self.data.shift(period)) * 100
#         return proc

#     def percentage_price_oscillator(self, fast=12, slow=26):
#         ema_fast = self.data.ewm(span=fast, min_periods=fast).mean()
#         ema_slow = self.data.ewm(span=slow, min_periods=slow).mean()
#         ppo = (ema_fast - ema_slow) / ema_slow * 100
#         return ppo

#     def detrended_price_oscillator(self, period=14):
#         sma = self.data.rolling(window=int(period/2 + 1)).mean()
#         dpo = self.data - sma
#         return dpo

#     def true_strength_index(self, r=25, s=13):
#         diff = self.data.diff()
#         abs_diff = np.abs(diff)
#         smoothed_pc = diff.ewm(span=r, min_periods=r).mean().ewm(span=s, min_periods=s).mean()
#         smoothed_abs_pc = abs_diff.ewm(span=r, min_periods=r).mean().ewm(span=s, min_periods=s).mean()
#         tsi = 100 * (smoothed_pc / smoothed_abs_pc)
#         return tsi

#     def relative_momentum_index(self, period=14):
#         momentum = self.data.diff(period)
#         return self.relative_strength_index(momentum, period=period)

#     def connors_rsi(self, period_rsi=3, period_streak=2, period_rank=100):
#         rsi = self.relative_strength_index(period=period_rsi)
#         streak = self.data.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)).rolling(window=period_streak).sum()
#         up_down_rsi = self.relative_strength_index(streak, period=period_streak)
#         pct_rank = self.data.rank(pct=True) * 100
#         connors_rsi = (rsi + up_down_rsi + pct_rank) / 3
#         return connors_rsi

#     def intraday_momentum_index(self, open_, close, period=14):
#         diff = close - open_
#         up_days = (diff.where(diff > 0, 0)).rolling(window=period).sum()
#         down_days = (-diff.where(diff < 0, 0)).rolling(window=period).sum()
#         imi = 100 * (up_days / (up_days + down_days))
#         return imi

#     def stochastic_rsi(self, period=14):
#         rsi = self.relative_strength_index(period=period)
#         stoch_rsi = (rsi - rsi.rolling(window=period).min()) / (rsi.rolling(window=period).max() - rsi.rolling(window=period).min())
#         return stoch_rsi

#     def aroon_indicator(self, period=25):
#         aroon_up = (period - self.data.rolling(window=period).apply(lambda x: period - np.argmax(x))) / period * 100
#         aroon_down = (period - self.data.rolling(window=period).apply(lambda x: period - np.argmin(x))) / period * 100
#         return aroon_up, aroon_down

#     def elders_force_index(self, volume, close, period=13):
#         efi = volume * (close - close.shift(1))
#         efi_sma = efi.rolling(window=period).mean()
#         return efi_sma

#     def qstick_indicator(self, open_, close, period=10):
#         qstick = (close - open_).rolling(window=period).mean()
#         return qstick

# import numpy as np

# # Momentum Indicators
# class MomentumIndicators():
    
#     # List of available indicator methods
#     available_indicators = [
#         'relative_strength_index', 
#         'moving_average_convergence_divergence',
#         'rate_of_change',
#         'stochastic_oscillator',
#         'commodity_channel_index',
#         'momentum_indicator',
#         'williams_r',
#         'chande_momentum_oscillator',
#         'ultimate_oscillator',
#         'price_rate_of_change',
#         'percentage_price_oscillator',
#         'detrended_price_oscillator',
#         'true_strength_index',
#         'relative_momentum_index',
#         'connors_rsi',
#         'intraday_momentum_index',
#         'stochastic_rsi',
#         'aroon_indicator',
#         'elders_force_index',
#         'qstick_indicator'
#     ]

#     def __init__(self, data):
#         self.data = data

#     def get_indicator(self, indicator_name):
#         indicator_method = getattr(self, indicator_name)
#         if indicator_method:
#             return indicator_method
#         else:
#             raise ValueError(f"Indicator {indicator_name} is not implemented")
        
#     def call_indicator(self, indicator, *args, **kwargs):
#         if callable(indicator):

#             print(f' *args:{args}, **kwargs:{kwargs}')

#             return indicator(*args, **kwargs)
#         else:
#             raise ValueError(f"Indicator {indicator} is not implemented")
        
#     def list_indicators(self):
#         return self.available_indicators
    
#     def relative_strength_index(self, period=14):
#         # RSI = 100 - (100 / (1 + RS))
#         delta = self.data.diff()
#         gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
#         loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
#         rs = gain / loss
#         rsi = 100 - (100 / (1 + rs))
#         return rsi

#     def moving_average_convergence_divergence(self, slow=26, fast=12, signal=9):
#         # MACD Line: (12-day EMA - 26-day EMA)
#         # Signal Line: 9-day EMA of MACD Line
#         ema_fast = self.data.ewm(span=fast, min_periods=fast).mean()
#         ema_slow = self.data.ewm(span=slow, min_periods=slow).mean()
#         macd = ema_fast - ema_slow
#         signal_line = macd.ewm(span=signal, min_periods=signal).mean()
#         return macd, signal_line

#     def rate_of_change(self, period=12):
#         # ROC = ((Current Price - Price n periods ago) / Price n periods ago) * 100
#         roc = ((self - self.data.shift(period)) / self.data.shift(period)) * 100
#         return roc

#     def stochastic_oscillator(self, period=14):
#         # %K = (Current Close - Lowest Low)/(Highest High - Lowest Low) * 100
#         low_min = self.data.rolling(window=period).min()
#         high_max = self.data.rolling(window=period).max()
#         stoch = ((self - low_min) / (high_max - low_min)) * 100
#         return stoch

#     def commodity_channel_index(self, period=20):
#         # CCI = (Typical Price - SMA of Typical Price) / (0.015 * Mean Deviation)
#         typical_price = (self['High'] + self.data['Low'] + self.data['Close']) / 3
#         sma = typical_price.rolling(window=period).mean()
#         mean_dev = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
#         cci = (typical_price - sma) / (0.015 * mean_dev)
#         return cci

#     def momentum_indicator(self, period=10):
#         # Momentum = Close - Close n periods ago
#         momentum = self.data.diff(periods=period)
#         return momentum

#     def williams_r(self, period=14):
#         # %R = (Highest High - Close)/(Highest High - Lowest Low) * -100
#         high_max = self.data.rolling(window=period).max()
#         low_min = self.data.rolling(window=period).min()
#         will_r = ((high_max - self.data) / (high_max - low_min)) * -100
#         return will_r

#     def chande_momentum_oscillator(self, period=14):
#         # CMO = ((Sum of Gains for n periods - Sum of Losses for n periods) / (Sum of Gains for n periods + Sum of Losses for n periods)) * 100
#         delta = self.data.diff()
#         gain = (delta.where(delta > 0, 0)).rolling(window=period).sum()
#         loss = (-delta.where(delta < 0, 0)).rolling(window=period).sum()
#         cmo = ((gain - loss) / (gain + loss)) * 100
#         return cmo

#     def ultimate_oscillator(self, period1=7, period2=14, period3=28):
#         # UO = 100 * (4 * avg7 + 2 * avg14 + avg28) / (4 + 2 + 1)
#         high_low = self.data['High'] - self.data['Low']
#         high_close = np.abs(self['High'] - self.data['Close'].shift(1))
#         low_close = np.abs(self['Low'] - self.data['Close'].shift(1))
#         true_range = high_low.combine(high_close, np.maximum).combine(low_close, np.maximum)
#         avg1 = true_range.rolling(window=period1).mean()
#         avg2 = true_range.rolling(window=period2).mean()
#         avg3 = true_range.rolling(window=period3).mean()
#         buying_pressure = self.data['Close'] - np.minimum(self['Low'], self.data['Close'].shift(1))
#         bp_avg1 = buying_pressure.rolling(window=period1).mean()
#         bp_avg2 = buying_pressure.rolling(window=period2).mean()
#         bp_avg3 = buying_pressure.rolling(window=period3).mean()
#         ult_osc = 100 * (4 * bp_avg1 + 2 * bp_avg2 + bp_avg3) / (4 * avg1 + 2 * avg2 + avg3)
#         return ult_osc

#     def price_rate_of_change(self, period=12):
#         # PROC = (Current Price - Price n periods ago) / Price n periods ago * 100
#         proc = ((self - self.data.shift(period)) / self.data.shift(period)) * 100
#         return proc

#     def percentage_price_oscillator(self, fast=12, slow=26):
#         # PPO = (FastEMA - SlowEMA) / SlowEMA * 100
#         ema_fast = self.data.ewm(span=fast, min_periods=fast).mean()
#         ema_slow = self.data.ewm(span=slow, min_periods=slow).mean()
#         ppo = (ema_fast - ema_slow) / ema_slow * 100
#         return ppo

#     def detrended_price_oscillator(self, period=14):
#         # DPO = Price - SMA(Price, Period/2 + 1)
#         sma = self.data.rolling(window=int(period/2 + 1)).mean()
#         dpo = self.data - sma
#         return dpo

#     def true_strength_index(self, r=25, s=13):
#         # TSI = 100 * (Smoothed PC - Smoothed SPC) / (Smoothed Absolute PC - Smoothed SPC)
#         diff = self.data.diff()
#         abs_diff = np.abs(diff)
#         smoothed_pc = diff.ewm(span=r, min_periods=r).mean().ewm(span=s, min_periods=s).mean()
#         smoothed_abs_pc = abs_diff.ewm(span=r, min_periods=r).mean().ewm(span=s, min_periods=s).mean()
#         tsi = 100 * (smoothed_pc / smoothed_abs_pc)
#         return tsi

#     def relative_momentum_index(self, period=14):
#         # RMI = RSI of momentum over period n
#         momentum = self.data.diff(period)
#         return MomentumIndicators.relative_strength_index(momentum, period=period)

#     def connors_rsi(self, period_rsi=3, period_streak=2, period_rank=100):
#         # ConnorsRSI = (RSI + UpDownRSI + PercentRank) / 3
#         rsi = MomentumIndicators.relative_strength_index(self, period=period_rsi)
#         streak = self.data.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)).rolling(window=period_streak).sum()
#         up_down_rsi = MomentumIndicators.relative_strength_index(streak, period=period_streak)
#         pct_rank = self.data.rank(pct=True) * 100
#         connors_rsi = (rsi + up_down_rsi + pct_rank) / 3
#         return connors_rsi

#     def intraday_momentum_index(self, period=14):
#         # IMI = 100 * (Sum of Up Days / (Sum of Up Days + Sum of Down Days))
#         diff = self.data['Close'] - self.data['open']
#         up_days = (diff.where(diff > 0, 0)).rolling(window=period).sum()
#         down_days = (-diff.where(diff < 0, 0)).rolling(window=period).sum()
#         imi = 100 * (up_days / (up_days + down_days))
#         return imi

#     def stochastic_rsi(self, period=14):
#         # StochRSI = (RSI - min(RSI, n)) / (max(RSI, n) - min(RSI, n))
#         rsi = MomentumIndicators.relative_strength_index(self, period=period)
#         stoch_rsi = (rsi - rsi.rolling(window=period).min()) / (rsi.rolling(window=period).max() - rsi.rolling(window=period).min())
#         return stoch_rsi

#     def aroon_indicator(self, period=25):
#         # Aroon Up = ((N - Days Since N-high) / N) * 100
#         # Aroon Down = ((N - Days Since N-low) / N) * 100
#         aroon_up = (period - self.data.rolling(window=period).apply(lambda x: period - np.argmax(x))) / period * 100
#         aroon_down = (period - self.data.rolling(window=period).apply(lambda x: period - np.argmin(x))) / period * 100
#         return aroon_up, aroon_down

#     def elders_force_index(self, period=13):
#         # EFI = Volume * (Close - Close(1))
#         efi = self.data['volume'] * (self['Close'] - self.data['Close'].shift(1))
#         efi_sma = efi.rolling(window=period).mean()
#         return efi_sma

#     def qstick_indicator(self, period=10):
#         # QStick = n-period moving average of (Open - Close)
#         qstick = (self['Close'] - self.data['open']).rolling(window=period).mean()
#         return qstick



# class RSI(Indicator):
#     # RSI = 100 - (100 / (1 + RS))
#     # RS = Average Gain / Average Loss
#     def calculate(self, period=14):
#         delta = self.data['Close'].diff()
#         gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
#         loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
#         rs = gain / loss
#         rsi = 100 - (100 / (1 + rs))
#         return rsi

# class MACD(Indicator):
#     # MACD = 12-Period EMA - 26-Period EMA
#     # Signal Line = 9-Period EMA of MACD
#     def calculate(self, short_period=12, long_period=26, signal_period=9):
#         short_ema = self.data['Close'].ewm(span=short_period, adjust=False).mean()
#         long_ema = self.data['Close'].ewm(span=long_period, adjust=False).mean()
#         macd = short_ema - long_ema
#         signal = macd.ewm(span=signal_period, adjust=False).mean()
#         return macd, signal

# class ROC(Indicator):
#     # ROC = ((Close - Close_n) / Close_n) * 100
#     def calculate(self, period=12):
#         roc = (self.data['Close'].diff(periods=period) / self.data['Close'].shift(periods=period)) * 100
#         return roc

# class StochasticOscillator(Indicator):
#     # %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
#     # %D = 3-Period SMA of %K
#     def calculate(self, period=14, smooth_k=3, smooth_d=3):
#         low_min = self.data['Low'].rolling(window=period).min()
#         high_max = self.data['High'].rolling(window=period).max()
#         k = ((self.data['Close'] - low_min) / (high_max - low_min)) * 100
#         d = k.rolling(window=smooth_d).mean()
#         k = k.rolling(window=smooth_k).mean()
#         return k, d

# class CCI(Indicator):
#     # CCI = (Typical Price - MA) / (0.015 * Mean Deviation)
#     def calculate(self, period=20):
#         tp = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
#         ma = tp.rolling(window=period).mean()
#         md = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
#         cci = (tp - ma) / (0.015 * md)
#         return cci

# class MomentumIndicator(Indicator):
#     # Momentum = Close - Close_n
#     def calculate(self, period=10):
#         momentum = self.data['Close'] - self.data['Close'].shift(period)
#         return momentum

# class WilliamsR(Indicator):
#     # %R = (Highest High - Close) / (Highest High - Lowest Low) * -100
#     def calculate(self, period=14):
#         high_max = self.data['High'].rolling(window=period).max()
#         low_min = self.data['Low'].rolling(window=period).min()
#         williams_r = (high_max - self.data['Close']) / (high_max - low_min) * -100
#         return williams_r

# class CMO(Indicator):
#     # CMO = (Sum of Up Changes - Sum of Down Changes) / (Sum of Up Changes + Sum of Down Changes) * 100
#     def calculate(self, period=14):
#         delta = self.data['Close'].diff()
#         up = delta.where(delta > 0, 0).rolling(window=period).sum()
#         down = -delta.where(delta < 0, 0).rolling(window=period).sum()
#         cmo = (up - down) / (up + down) * 100
#         return cmo

# class UltimateOscillator(Indicator):
#     # UO = 100 * [(4 * AVG7) + (2 * AVG14) + AVG28] / (4 + 2 + 1)
#     def calculate(self, period1=7, period2=14, period3=28):
#         avg1 = (self.data['Close'] - self.data['Low']).rolling(window=period1).mean() / (self.data['High'] - self.data['Low']).rolling(window=period1).mean()
#         avg2 = (self.data['Close'] - self.data['Low']).rolling(window=period2).mean() / (self.data['High'] - self.data['Low']).rolling(window=period2).mean()
#         avg3 = (self.data['Close'] - self.data['Low']).rolling(window=period3).mean() / (self.data['High'] - self.data['Low']).rolling(window=period3).mean()
#         uo = 100 * ((4 * avg1) + (2 * avg2) + avg3) / (4 + 2 + 1)
#         return uo

# class PROC(Indicator):
#     # PROC = ((Close - Close_n) / Close_n) * 100
#     def calculate(self, period=12):
#         proc = ((self.data['Close'] - self.data['Close'].shift(period)) / self.data['Close'].shift(period)) * 100
#         return proc

# class PPO(Indicator):
#     # PPO = (EMA_short - EMA_long) / EMA_long * 100
#     def calculate(self, short_period=12, long_period=26):
#         short_ema = self.data['Close'].ewm(span=short_period, adjust=False).mean()
#         long_ema = self.data['Close'].ewm(span=long_period, adjust=False).mean()
#         ppo = (short_ema - long_ema) / long_ema * 100
#         return ppo

# class DPO(Indicator):
#     # DPO = Price - SMA
#     def calculate(self, period=20):
#         sma = self.data['Close'].rolling(window=period).mean()
#         dpo = self.data['Close'].shift(int((period / 2) + 1)) - sma
#         return dpo

# class TSI(Indicator):
#     # TSI = (25-period EMA of 13-period EMA of Momentum) / (25-period EMA of 13-period EMA of Absolute Momentum) * 100
#     def calculate(self, r=25, s=13):
#         momentum = self.data['Close'].diff(1)
#         ema1 = momentum.ewm(span=s, adjust=False).mean()
#         ema2 = ema1.ewm(span=r, adjust=False).mean()
#         abs_momentum = abs(momentum)
#         abs_ema1 = abs_momentum.ewm(span=s, adjust=False).mean()
#         abs_ema2 = abs_ema1.ewm(span=r, adjust=False).mean()
#         tsi = (ema2 / abs_ema2) * 100
#         return tsi

# class RMI(Indicator):
#     # RMI = RSI but using n-period close changes
#     def calculate(self, period=14, momentum_period=3):
#         close_diff = self.data['Close'].diff(momentum_period)
#         gain = (close_diff.where(close_diff > 0, 0)).rolling(window=period).mean()
#         loss = (-close_diff.where(close_diff < 0, 0)).rolling(window=period).mean()
#         rs = gain / loss
#         rmi = 100 - (100 / (1 + rs))
#         return rmi

# class ConnorsRSI(Indicator):
#     # ConnorsRSI = (RSI(Close) + RSI(UpDown Streak) + PercentRank(100-day ROC)) / 3
#     def calculate(self, rsi_period=3, streak_rsi_period=2, roc_period=100):
#         rsi = RSI(self.data).calculate(rsi_period)
#         up_down_streak = (self.data['Close'] - self.data['Close'].shift(1)).apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)).cumsum()
#         streak_rsi = RSI(pd.DataFrame(up_down_streak)).calculate(streak_rsi_period)
#         roc = ROC(self.data).calculate(roc_period)
#         percent_rank = roc.rank(pct=True) * 100
#         connors_rsi = (rsi + streak_rsi + percent_rank) / 3
#         return connors_rsi

# class IMI(Indicator):
#     # IMI = 100 * SUM(gains) / SUM(gains + losses)
#     def calculate(self, period=14):
#         diff = self.data['Close'] - self.data['Open']
#         gain = diff.where(diff > 0, 0)
#         loss = -diff.where(diff < 0, 0)
#         imi = 100 * gain.rolling(window=period).sum() / (gain.rolling(window=period).sum() + loss.rolling(window=period).sum())
#         return imi

# class StochRSI(Indicator):
#     # StochRSI = (RSI - Lowest Low RSI) / (Highest High RSI - Lowest Low RSI)
#     def calculate(self, period=14):
#         rsi = RSI(self.data).calculate(period)
#         stochrsi = (rsi - rsi.rolling(window=period).min()) / (rsi.rolling(window=period).max() - rsi.rolling(window=period).min())
#         return stochrsi

# class Aroon(Indicator):
#     # Aroon Up = ((N - Days Since N-period High) / N) * 100
#     # Aroon Down = ((N - Days Since N-period Low) / N) * 100
#     def calculate(self, period=25):
#         aroon_up = ((period - self.data['High'].rolling(window=period).apply(lambda x: period - x[::-1].argmax() - 1)) / period) * 100
#         aroon_down = ((period - self.data['Low'].rolling(window=period).apply(lambda x: period - x[::-1].argmin() - 1)) / period) * 100
#         return aroon_up, aroon_down

# class EFI(Indicator):
#     # EFI = Volume * (Close - Close_prev)
#     def calculate(self, period=13):
#         efi = (self.data['Close'] - self.data['Close'].shift(1)) * self.data['Volume']
#         efi = efi.rolling(window=period).mean()
#         return efi

# class Qstick(Indicator):
#     # Qstick = N-period SMA of (Close - Open)
#     def calculate(self, period=10):
#         qstick = (self.data['Close'] - self.data['Open']).rolling(window=period).mean()
#         return qstick

# # Example usage:
# # df = pd.read_csv('data.csv')
# # pp = PivotPoints(df)
# # pp_values = pp.calculate()
# # print(pp_values)


    # def __init__(self, data):
    #     self.data = data
    #     print("Initialized MomentumIndicators")

    #     # Dynamically generate the list of available indicators
    #     self.available_indicators = [
    #         name for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
    #         if name not in ['__init__', 'get_indicator', 'call_indicator', 'list_indicators']
    #     ]

    # def get_indicator(self, indicator_name):
    #     indicator_method = getattr(self, indicator_name)
    #     if indicator_method:
    #         return indicator_method
    #     else:
    #         raise ValueError(f"Indicator {indicator_name} is not implemented")
        
    # def call_indicator(self, indicator, **kwargs):
    #     if callable(indicator):
    #         return indicator(**kwargs)
    #     else:
    #         raise ValueError(f"Indicator {indicator} is not implemented")
        
    # def list_indicators(self):
    #     return self.available_indicators