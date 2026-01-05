import numpy as np
import pandas as pd

# Volatility Indicators
class VolatilityIndicators:
    def __init__(self, data):
        self.data = data
    
    @staticmethod
    def bollinger_bands(self, period=20, multiplier=2):
        # BB = SMA +/- (Multiplier * Standard Deviation)
        sma = self.data['close'].rolling(window=period).mean()
        std = self.data['close'].rolling(window=period).std()
        upper_band = sma + (multiplier * std)
        lower_band = sma - (multiplier * std)
        return upper_band, lower_band

    @staticmethod
    def bollinger_bandwidth(self, period=20, multiplier=2):
        # BBW = (Upper Band - Lower Band) / Middle Band
        upper_band, lower_band = VolatilityIndicators.bollinger_bands(self, period, multiplier)
        sma = self.data['close'].rolling(window=period).mean()
        bandwidth = (upper_band - lower_band) / sma
        return bandwidth

    @staticmethod
    def bollinger_percent_b(self, period=20, multiplier=2):
        # %B = (Price - Lower Band) / (Upper Band - Lower Band)
        upper_band, lower_band = VolatilityIndicators.bollinger_bands(self, period, multiplier)
        percent_b = (self['close'] - lower_band) / (upper_band - lower_band)
        return percent_b

    @staticmethod
    def keltner_channels(self, period=20, multiplier=2):
        # KC = EMA +/- (Multiplier * ATR)
        ema = self.data['close'].ewm(span=period, min_periods=period).mean()
        atr = VolatilityIndicators.average_true_range(self, period)
        upper_band = ema + (multiplier * atr)
        lower_band = ema - (multiplier * atr)
        return upper_band, lower_band

    @staticmethod
    def donchian_channels(self, period=20):
        # DC = Highest High and Lowest Low over period
        upper_band = self.data['high'].rolling(window=period).max()
        lower_band = self.data['low'].rolling(window=period).min()
        return upper_band, lower_band

    @staticmethod
    def standard_deviation(self, period=20):
        # SD = Standard Deviation of closing prices over period
        std = self.data['close'].rolling(window=period).std()
        return std

    @staticmethod
    def average_true_range(self, period=14):
        # ATR = EMA of True Range over period
        high_low = self.data['high'] - self.data['low']
        high_close = np.abs(self['high'] - self.data['close'].shift(1))
        low_close = np.abs(self['low'] - self.data['close'].shift(1))
        true_range = high_low.combine(high_close, np.maximum).combine(low_close, np.maximum)
        atr = true_range.ewm(span=period, min_periods=period).mean()
        return atr

    @staticmethod
    def relative_volatility_index(self, period=14):
        # RVI = Standard Deviation of up days / (Standard Deviation of up days + Standard Deviation of down days)
        price_change = self.data['close'].diff()
        up_days_std = price_change.where(price_change > 0, 0).rolling(window=period).std()
        down_days_std = price_change.where(price_change < 0, 0).rolling(window=period).std()
        rvi = up_days_std / (up_days_std + down_days_std)
        return rvi

    @staticmethod
    def chaikin_volatility(self, period=10):
        # CV = (EMA of High-Low over period) / (EMA of High-Low over previous period) - 1
        high_low = self.data['high'] - self.data['low']
        ema_current = high_low.ewm(span=period, min_periods=period).mean()
        ema_previous = high_low.shift(1).ewm(span=period, min_periods=period).mean()
        cv = (ema_current / ema_previous) - 1
        return cv

    @staticmethod
    def volatility_index(self, period=14):
        # VIX = (Standard Deviation of Log Returns) * sqrt(252)
        log_returns = np.log(self['close'] / self.data['close'].shift(1))
        vix = log_returns.rolling(window=period).std() * np.sqrt(252)
        return vix

    @staticmethod
    def historical_volatility(self, period=14):
        # HV = Standard Deviation of log returns over period
        log_returns = np.log(self['close'] / self.data['close'].shift(1))
        hv = log_returns.rolling(window=period).std()
        return hv

    @staticmethod
    def implied_volatility(self, period=14):
        # IV = Standard Deviation of option prices over period
        option_prices = self.data['option_price']
        iv = option_prices.rolling(window=period).std()
        return iv

    @staticmethod
    def market_facilitation_index(self):
        # MFI = (High - Low) / Volume
        mfi = (self['high'] - self.data['low']) / self.data['volume']
        return mfi

    @staticmethod
    def choppiness_index(self, period=14):
        # CI = 100 * Log10(sum(True Range) / (Highest High - Lowest Low)) / Log10(period)
        true_range = VolatilityIndicators.average_true_range(self, period)
        high_max = self.data['high'].rolling(window=period).max()
        low_min = self.data['low'].rolling(window=period).min()
        ci = 100 * np.log10(true_range.sum() / (high_max - low_min)) / np.log10(period)
        return ci

    @staticmethod
    def average_true_range_bands(self, period=14):
        # ATR Bands = SMA +/- (Multiplier * ATR)
        sma = self.data['close'].rolling(window=period).mean()
        atr = VolatilityIndicators.average_true_range(self, period)
        upper_band = sma + (2 * atr)
        lower_band = sma - (2 * atr)
        return upper_band, lower_band

    @staticmethod
    def average_true_range_channels(self, period=14):
        # ATR Channels = SMA +/- (Multiplier * ATR)
        sma = self.data['close'].rolling(window=period).mean()
        atr = VolatilityIndicators.average_true_range(self, period)
        upper_band = sma + (2 * atr)
        lower_band = sma - (2 * atr)
        return upper_band, lower_band


# # Volatility Indicators
# class BollingerBands(Indicator):
#     # Upper Band = MA + (Standard Deviation * Multiplier)
#     # Lower Band = MA - (Standard Deviation * Multiplier)
#     def calculate(self, period=20, multiplier=2):
#         ma = self.data['Close'].rolling(window=period).mean()
#         std = self.data['Close'].rolling(window=period).std()
#         upper_band = ma + (std * multiplier)
#         lower_band = ma - (std * multiplier)
#         return pd.DataFrame({'Upper Band': upper_band, 'Lower Band': lower_band, 'MA': ma})

# class BollingerBandwidth(Indicator):
#     # Bollinger Bandwidth = (Upper Band - Lower Band) / MA
#     def calculate(self, period=20, multiplier=2):
#         bb = BollingerBands(self.data).calculate(period, multiplier)
#         bandwidth = (bb['Upper Band'] - bb['Lower Band']) / bb['MA']
#         return bandwidth

# class BollingerPercentB(Indicator):
#     # %B = (Close - Lower Band) / (Upper Band - Lower Band)
#     def calculate(self, period=20, multiplier=2):
#         bb = BollingerBands(self.data).calculate(period, multiplier)
#         percent_b = (self.data['Close'] - bb['Lower Band']) / (bb['Upper Band'] - bb['Lower Band'])
#         return percent_b

# class KeltnerChannels(Indicator):
#     # Upper Channel = EMA + (ATR * Multiplier)
#     # Lower Channel = EMA - (ATR * Multiplier)
#     def calculate(self, period=20, multiplier=2):
#         ema = self.data['Close'].ewm(span=period, adjust=False).mean()
#         atr = ATR(self.data).calculate(period)
#         upper_channel = ema + (atr * multiplier)
#         lower_channel = ema - (atr * multiplier)
#         return pd.DataFrame({'Upper Channel': upper_channel, 'Lower Channel': lower_channel, 'EMA': ema})

# class DonchianChannels(Indicator):
#     # Upper Channel = Highest High over n periods
#     # Lower Channel = Lowest Low over n periods
#     def calculate(self, period=20):
#         upper_channel = self.data['High'].rolling(window=period).max()
#         lower_channel = self.data['Low'].rolling(window=period).min()
#         return pd.DataFrame({'Upper Channel': upper_channel, 'Lower Channel': lower_channel})

# class StandardDeviation(Indicator):
#     # Standard Deviation = sqrt(sum((Close - MA)^2) / n)
#     def calculate(self, period=20):
#         std = self.data['Close'].rolling(window=period).std()
#         return std

# class ATR(Indicator):
#     # ATR = (Previous ATR * (n - 1) + TR) / n
#     def calculate(self, period=14):
#         high_low = self.data['High'] - self.data['Low']
#         high_close = np.abs(self.data['High'] - self.data['Close'].shift())
#         low_close = np.abs(self.data['Low'] - self.data['Close'].shift())
#         tr = high_low.combine(high_close, max).combine(low_close, max)
#         atr = tr.rolling(window=period).mean()
#         return atr

# class RVI(Indicator):
#     # RVI = 100 * (Standard Deviation of Up Days) / (Standard Deviation of All Days)
#     def calculate(self, period=14):
#         std_up = self.data['Close'].diff().where(self.data['Close'].diff() > 0, 0).rolling(window=period).std()
#         std_all = self.data['Close'].diff().rolling(window=period).std()
#         rvi = 100 * (std_up / std_all)
#         return rvi

# class ChaikinVolatility(Indicator):
#     # CHV = (EMA(High - Low, period) / EMA(High - Low, period).shift(period) - 1) * 100
#     def calculate(self, period=10):
#         hl = self.data['High'] - self.data['Low']
#         ema_hl = hl.ewm(span=period, adjust=False).mean()
#         chv = (ema_hl / ema_hl.shift(period) - 1) * 100
#         return chv

# class VIX(Indicator):
#     # VIX is not calculated directly but typically obtained from market data providers
#     def calculate(self):
#         raise NotImplementedError("VIX is typically obtained from market data providers and not calculated directly")

# class HistoricalVolatility(Indicator):
#     # Historical Volatility = Standard Deviation of Log Returns
#     def calculate(self, period=20):
#         log_returns = np.log(self.data['Close'] / self.data['Close'].shift(1))
#         hv = log_returns.rolling(window=period).std() * np.sqrt(252)
#         return hv

# class ImpliedVolatility(Indicator):
#     # Implied Volatility is not calculated directly but typically obtained from market data providers
#     def calculate(self):
#         raise NotImplementedError("Implied Volatility is typically obtained from market data providers and not calculated directly")

# class MarketFacilitationIndex(Indicator):
#     # MFI = (High - Low) / Volume
#     def calculate(self):
#         mfi = (self.data['High'] - self.data['Low']) / self.data['Volume']
#         return mfi

# class ChoppinessIndex(Indicator):
#     # CHOP = 100 * log10((sum(TR) / (Highest High - Lowest Low)) / log10(n))
#     def calculate(self, period=14):
#         high_low = self.data['High'] - self.data['Low']
#         high_close = np.abs(self.data['High'] - self.data['Close'].shift())
#         low_close = np.abs(self.data['Low'] - self.data['Close'].shift())
#         tr = high_low.combine(high_close, max).combine(low_close, max)
#         sum_tr = tr.rolling(window=period).sum()
#         highest_high = self.data['High'].rolling(window=period).max()
#         lowest_low = self.data['Low'].rolling(window=period).min()
#         chop = 100 * np.log10(sum_tr / (highest_high - lowest_low)) / np.log10(period)
#         return chop

# class ATRBands(Indicator):
#     # Upper Band = Close + (ATR * Multiplier)
#     # Lower Band = Close - (ATR * Multiplier)
#     def calculate(self, period=14, multiplier=2):
#         atr = ATR(self.data).calculate(period)
#         upper_band = self.data['Close'] + (atr * multiplier)
#         lower_band = self.data['Close'] - (atr * multiplier)
#         return pd.DataFrame({'Upper Band': upper_band, 'Lower Band': lower_band})

# class ATRChannels(Indicator):
#     # Upper Channel = MA + (ATR * Multiplier)
#     # Lower Channel = MA - (ATR * Multiplier)
#     def calculate(self, period=14, multiplier=2):
#         ma = self.data['Close'].rolling(window=period).mean()
#         atr = ATR(self.data).calculate(period)
#         upper_channel = ma + (atr * multiplier)
#         lower_channel = ma - (atr * multiplier)
#         return pd.DataFrame({'Upper Channel': upper_channel, 'Lower Channel': lower_channel, 'MA': ma})

# # Example usage:
# # df = pd.read_csv('data.csv')
# # pp = PivotPoints(df)
# # pp_values = pp.calculate()
# # print(pp_values)
