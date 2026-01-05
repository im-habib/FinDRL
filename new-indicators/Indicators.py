from indicators import Base

# MACD Indicator
class MACD(Base):
    def __init__(self, short_period=12, long_period=26, signal_period=9):
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period

    def calculate(self, data):
        short_ema = data['close'].ewm(span=self.short_period, adjust=False).mean()
        long_ema = data['close'].ewm(span=self.long_period, adjust=False).mean()
        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        macd_histogram = macd_line - signal_line
        data['macd_line'] = macd_line
        data['signal_line'] = signal_line
        data['macd_histogram'] = macd_histogram
        return data

# Bollinger Bands Indicator
class BollingerBands(Base):
    def __init__(self, period=20, num_std=2):
        self.period = period
        self.num_std = num_std

    def calculate(self, data):
        sma = data['close'].rolling(window=self.period).mean()
        std = data['close'].rolling(window=self.period).std()
        data['boll_ub'] = sma + (std * self.num_std)
        data['boll_lb'] = sma - (std * self.num_std)
        return data

# RSI Indicator
class RSI(Base):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data):
        delta = data['close'].diff(1)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        rs = avg_gain / avg_loss
        data['rsi'] = 100 - (100 / (1 + rs))
        return data

# CCI Indicator
class CCI(Base):
    def __init__(self, period=30):
        self.period = period

    def calculate(self, data):
        tp = (data['high'] + data['low'] + data['close']) / 3  # Typical Price
        sma = tp.rolling(window=self.period).mean()
        mad = (tp - sma).abs().rolling(window=self.period).mean()  # Mean Absolute Deviation
        data['cci'] = (tp - sma) / (0.015 * mad)
        return data

# DX Indicator
class DX(Base):
    def __init__(self, period=30):
        self.period = period

    def calculate(self, data):
        up_move = data['high'].diff(1)
        down_move = data['low'].diff(1)
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
        tr = pd.concat([data['high'] - data['low'], abs(data['high'] - data['close'].shift(1)), abs(data['low'] - data['close'].shift(1))], axis=1).max(axis=1)
        atr = tr.rolling(window=self.period).mean()
        plus_di = 100 * (plus_dm.rolling(window=self.period).sum() / atr)
        minus_di = 100 * (minus_dm.rolling(window=self.period).sum() / atr)
        data['dx'] = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        return data

# SMA Indicator
class SMA(Base):
    def __init__(self, period, column='close'):
        self.period = period
        self.column = column

    def calculate(self, data):
        data[f'{self.column}_sma_{self.period}'] = data[self.column].rolling(window=self.period).mean()
        return data
    

# import pandas as pd

# class Indicators:
#     def __init__(self, data):
#         """
#         Initialize the class with stock data. Converts to DataFrame if necessary
#         and ensures column names are lowercase.
#         :param data: DataFrame or data convertible to DataFrame (e.g., dict, list of dicts)
#         """
#         # Convert data to DataFrame if it's not already
#         if not isinstance(data, pd.DataFrame):
#             self.data = pd.DataFrame(data)
#         else:
#             self.data = data
        
#         # Convert column names to lowercase
#         self.data.columns = [col.lower() for col in self.data.columns]

#     def macd(self, short_period=12, long_period=26, signal_period=9):
#         short_ema = self.data['close'].ewm(span=short_period, adjust=False).mean()
#         long_ema = self.data['close'].ewm(span=long_period, adjust=False).mean()
#         macd_line = short_ema - long_ema
#         signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
#         macd_histogram = macd_line - signal_line
#         self.data['macd_line'] = macd_line
#         self.data['signal_line'] = signal_line
#         self.data['macd_histogram'] = macd_histogram

#     def bollinger_bands(self, period=20, num_std=2):
#         sma = self.data['close'].rolling(window=period).mean()
#         std = self.data['close'].rolling(window=period).std()
#         boll_ub = sma + (std * num_std)
#         boll_lb = sma - (std * num_std)
#         self.data['boll_ub'] = boll_ub
#         self.data['boll_lb'] = boll_lb

#     def rsi(self, period=14):
#         delta = self.data['close'].diff(1)
#         gain = delta.where(delta > 0, 0)
#         loss = -delta.where(delta < 0, 0)
#         avg_gain = gain.rolling(window=period).mean()
#         avg_loss = loss.rolling(window=period).mean()
#         rs = avg_gain / avg_loss
#         rsi = 100 - (100 / (1 + rs))
#         self.data['rsi'] = rsi

#     def cci(self, period=30):
#         tp = (self.data['high'] + self.data['low'] + self.data['close']) / 3  # Typical Price
#         sma = tp.rolling(window=period).mean()
#         mad = (tp - sma).abs().rolling(window=period).mean()  # Mean Absolute Deviation
#         cci = (tp - sma) / (0.015 * mad)
#         self.data['cci'] = cci

#     def dx(self, period=30):
#         up_move = self.data['high'].diff(1)
#         down_move = self.data['low'].diff(1)
#         plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
#         minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
#         tr = pd.concat([self.data['high'] - self.data['low'],
#                         abs(self.data['high'] - self.data['close'].shift(1)),
#                         abs(self.data['low'] - self.data['close'].shift(1))], axis=1).max(axis=1)
#         atr = tr.rolling(window=period).mean()
#         plus_di = 100 * (plus_dm.rolling(window=period).sum() / atr)
#         minus_di = 100 * (minus_dm.rolling(window=period).sum() / atr)
#         dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
#         self.data['dx'] = dx

#     def sma(self, period, column_name):
#         self.data[f'{column_name}_sma_{period}'] = self.data[column_name].rolling(window=period).mean()

#     def compute_all(self):
#         # Example of computing all indicators at once
#         self.macd()
#         self.bollinger_bands()
#         self.rsi()
#         self.cci()
#         self.dx()
#         self.sma(30, 'close')
#         self.sma(60, 'close')


# # Usage Example

# # Example dataset with capitalized column names and non-DataFrame input
# example_data = {
#     'CLOSE': [110, 112, 115, 117, 120, 122, 125],
#     'HIGH': [111, 113, 116, 118, 121, 123, 126],
#     'LOW': [109, 110, 113, 115, 119, 120, 123]
# }

# # Create an object of the Indicators class
# indicators = Indicators(example_data)

# # Compute all indicators
# indicators.compute_all()

# # Now 'indicators.data' contains all the indicators
# print(indicators.data.tail())
