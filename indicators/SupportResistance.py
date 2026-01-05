import numpy as np
import pandas as pd

# Support/Resistance and Overlay Indicators
class SupportResistanceIndicators:
    def __init__(self, data):
        self.data = data

    @staticmethod
    def pivot_points(self):
        # PP = (High + Low + Close) / 3
        pp = (self['high'] + self.data['low'] + self.data['close']) / 3
        return pp

    @staticmethod
    def fibonacci_retracement(self):
        # Fibonacci levels
        high = self.data['high'].max()
        low = self.data['low'].min()
        diff = high - low
        return {
            "level_0.0": high,
            "level_0.236": high - 0.236 * diff,
            "level_0.382": high - 0.382 * diff,
            "level_0.5": high - 0.5 * diff,
            "level_0.618": high - 0.618 * diff,
            "level_0.786": high - 0.786 * diff,
            "level_1.0": low
        }

    @staticmethod
    def fibonacci_extensions(self):
        # Fibonacci extensions
        high = self.data['high'].max()
        low = self.data['low'].min()
        diff = high - low
        return {
            "level_1.0": high,
            "level_1.236": high + 0.236 * diff,
            "level_1.382": high + 0.382 * diff,
            "level_1.5": high + 0.5 * diff,
            "level_1.618": high + 0.618 * diff,
            "level_2.0": high + diff
        }

    @staticmethod
    def fibonacci_arcs(self):
        # Fibonacci arcs
        high = self.data['high'].max()
        low = self.data['low'].min()
        diff = high - low
        midpoint = (high + low) / 2
        return {
            "arc_1": (midpoint, 0.236 * diff),
            "arc_2": (midpoint, 0.382 * diff),
            "arc_3": (midpoint, 0.5 * diff),
            "arc_4": (midpoint, 0.618 * diff)
        }

    @staticmethod
    def fibonacci_fan(self):
        # Fibonacci fan
        high = self.data['high'].max()
        low = self.data['low'].min()
        diff = high - low
        return {
            "fan_0.0": high,
            "fan_0.236": high - 0.236 * diff,
            "fan_0.382": high - 0.382 * diff,
            "fan_0.5": high - 0.5 * diff,
            "fan_0.618": high - 0.618 * diff,
            "fan_0.786": high - 0.786 * diff,
            "fan_1.0": low
        }

    @staticmethod
    def fibonacci_time_zones(self):
        # Fibonacci time zones
        high = self.data['high'].idxmax()
        low = self.data['low'].idxmin()
        diff = (high - low).days
        return {
            "time_0.0": low,
            "time_0.236": low + pd.Timedelta(days=0.236 * diff),
            "time_0.382": low + pd.Timedelta(days=0.382 * diff),
            "time_0.5": low + pd.Timedelta(days=0.5 * diff),
            "time_0.618": low + pd.Timedelta(days=0.618 * diff),
            "time_0.786": low + pd.Timedelta(days=0.786 * diff),
            "time_1.0": high
        }

    @staticmethod
    def gann_angles(self):
        # Gann angles
        high = self.data['high'].max()
        low = self.data['low'].min()
        return {
            "1x1": high / 1,
            "1x2": high / 2,
            "1x3": high / 3,
            "1x4": high / 4,
            "1x8": high / 8
        }

    @staticmethod
    def gann_fan(self):
        # Gann fan
        high = self.data['high'].max()
        low = self.data['low'].min()
        return {
            "1x1": high / 1,
            "1x2": high / 2,
            "1x3": high / 3,
            "1x4": high / 4,
            "1x8": high / 8
        }

    @staticmethod
    def gann_square_of_nine(self):
        # Gann square of nine
        high = self.data['high'].max()
        low = self.data['low'].min()
        return {
            "0.0": high,
            "0.25": high * 0.25,
            "0.5": high * 0.5,
            "0.75": high * 0.75,
            "1.0": low
        }

    @staticmethod
    def gann_box(self):
        # Gann box
        high = self.data['high'].max()
        low = self.data['low'].min()
        return {
            "0.0": high,
            "0.25": high * 0.25,
            "0.5": high * 0.5,
            "0.75": high * 0.75,
            "1.0": low
        }

    @staticmethod
    def gann_grid(self):
        # Gann grid
        high = self.data['high'].max()
        low = self.data['low'].min()
        return {
            "1x1": high / 1,
            "1x2": high / 2,
            "1x3": high / 3,
            "1x4": high / 4,
            "1x8": high / 8
        }

    @staticmethod
    def horizontal_support_resistance(self):
        # Horizontal support/resistance levels
        high = self.data['high'].max()
        low = self.data['low'].min()
        return {
            "support": low,
            "resistance": high
        }

    @staticmethod
    def vertical_support_resistance(self):
        # Vertical support/resistance levels
        high = self.data['high'].idxmax()
        low = self.data['low'].idxmin()
        return {
            "support": low,
            "resistance": high
        }

    @staticmethod
    def price_channels(self, period=20):
        # Price Channels = Highest High and Lowest Low over period
        upper_channel = self.data['high'].rolling(window=period).max()
        lower_channel = self.data['low'].rolling(window=period).min()
        return upper_channel, lower_channel

    @staticmethod
    def andrews_pitchfork(self):
        # Andrews' Pitchfork
        high = self.data['high'].max()
        low = self.data['low'].min()
        midpoint = (high + low) / 2
        return {
            "upper_trendline": high,
            "median_line": midpoint,
            "lower_trendline": low
        }

    @staticmethod
    def speed_resistance_lines(self):
        # Speed resistance lines
        high = self.data['high'].max()
        low = self.data['low'].min()
        diff = high - low
        return {
            "line_1": high - 0.33 * diff,
            "line_2": high - 0.67 * diff,
            "line_3": low
        }

    @staticmethod
    def speed_lines(self):
        # Speed lines
        high = self.data['high'].max()
        low = self.data['low'].min()
        diff = high - low
        return {
            "line_1": high - 0.33 * diff,
            "line_2": high - 0.67 * diff,
            "line_3": low
        }

    @staticmethod
    def trend_lines(self):
        # Trend lines
        high = self.data['high'].max()
        low = self.data['low'].min()
        return {
            "support": low,
            "resistance": high
        }

    @staticmethod
    def pitchfork_channel(self):
        # Pitchfork channel
        high = self.data['high'].max()
        low = self.data['low'].min()
        midpoint = (high + low) / 2
        return {
            "upper_trendline": high,
            "median_line": midpoint,
            "lower_trendline": low
        }

    @staticmethod
    def raff_regression_channel(self, period=14):
        # Raff Regression Channel
        lrl = TrendIndicators.linear_regression_line(self['close'], period)
        high_max = self.data['high'].rolling(window=period).max()
        low_min = self.data['low'].rolling(window=period).min()
        upper_channel = lrl + high_max
        lower_channel = lrl - low_min
        return upper_channel, lower_channel

    @staticmethod
    def standard_deviation_channel(self, period=14):
        # Standard Deviation Channel
        lrl = TrendIndicators.linear_regression_line(self['close'], period)
        std = TrendIndicators.standard_deviation(self['close'], period)
        upper_channel = lrl + std
        lower_channel = lrl - std
        return upper_channel, lower_channel

    @staticmethod
    def trend_channel(self, period=20):
        # Trend Channel
        upper_channel = self.data['high'].rolling(window=period).max()
        lower_channel = self.data['low'].rolling(window=period).min()
        return upper_channel, lower_channel

    @staticmethod
    def linear_regression_channel(self, period=14):
        # Linear Regression Channel
        lrl = TrendIndicators.linear_regression_line(self['close'], period)
        high_max = self.data['high'].rolling(window=period).max()
        low_min = self.data['low'].rolling(window=period).min()
        upper_channel = lrl + high_max
        lower_channel = lrl - low_min
        return upper_channel, lower_channel

    @staticmethod
    def moving_average_envelopes(self, period=20, percentage=2):
        # MAE = SMA +/- (SMA * percentage)
        sma = self.data['close'].rolling(window=period).mean()
        upper_envelope = sma + (sma * percentage / 100)
        lower_envelope = sma - (sma * percentage / 100)
        return upper_envelope, lower_envelope
