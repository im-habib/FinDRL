import numpy as np
import pandas as pd

# Custom and Combination Indicators
class CustomIndicators:
    def __init__(self, data):
        self.data = data
        
    @staticmethod
    def rainbow_moving_average(self, periods=[2, 4, 6, 8, 10]):
        # Rainbow Moving Average
        rainbow = pd.DataFrame(index=self.data.index)
        for period in periods:
            rainbow[f'SMA_{period}'] = TrendIndicators.simple_moving_average(self['close'], period)
        return rainbow

    @staticmethod
    def acceleration_bands(self, period=20, multiplier=4):
        # Acceleration Bands = High/Low * (1 + 4 * (High - Low) / (High + Low))
        high = self.data['high']
        low = self.data['low']
        upper_band = high * (1 + multiplier * (high - low) / (high + low))
        lower_band = low * (1 - multiplier * (high - low) / (high + low))
        return upper_band, lower_band

    @staticmethod
    def disparity_index(self, period=14):
        # Disparity Index = (Close - SMA) / SMA * 100
        sma = TrendIndicators.simple_moving_average(self['close'], period)
        disparity = (self['close'] - sma) / sma * 100
        return disparity

    @staticmethod
    def squeeze_momentum_indicator(self, period=20, multiplier=2):
        # Squeeze Momentum Indicator
        upper_band, lower_band = VolatilityIndicators.bollinger_bands(self, period, multiplier)
        keltner_upper, keltner_lower = VolatilityIndicators.keltner_channels(self, period, multiplier)
        squeeze_on = (lower_band > keltner_lower) & (upper_band < keltner_upper)
        return squeeze_on

    @staticmethod
    def relative_vigor_index(self, period=14):
        # RVI = (Close - Open) / (High - Low)
        rvi = (self['close'] - self.data['open']) / (self['high'] - self.data['low'])
        return rvi.rolling(window=period).mean()

    @staticmethod
    def price_momentum_oscillator(self, period1=35, period2=20, period3=10):
        # PMO = (35-period EMA of (Close - 20-period EMA of Close)) / (10-period EMA of (Close - 20-period EMA of Close))
        ema1 = self.data['close'].ewm(span=period1, min_periods=period1).mean()
        ema2 = self.data['close'].ewm(span=period2, min_periods=period2).mean()
        pmo = (self['close'] - ema2).ewm(span=period3, min_periods=period3).mean()
        return pmo

    @staticmethod
    def fisher_transform(self, period=14):
        # Fisher Transform = 0.5 * Log((1 + value) / (1 - value))
        high_max = self.data['high'].rolling(window=period).max()
        low_min = self.data['low'].rolling(window=period).min()
        value = 2 * ((self['close'] - low_min) / (high_max - low_min) - 0.5)
        fisher = 0.5 * np.log((1 + value) / (1 - value))
        return fisher

    @staticmethod
    def ehlers_fisher_transform(self, period=14):
        # Ehlers Fisher Transform
        high_max = self.data['high'].rolling(window=period).max()
        low_min = self.data['low'].rolling(window=period).min()
        value = 2 * ((self['close'] - low_min) / (high_max - low_min) - 0.5)
        fisher = 0.5 * np.log((1 + value) / (1 - value))
        return fisher

    @staticmethod
    def ehlers_early_onset_trend_detector(self, period=14):
        # Ehlers Early Onset Trend Detector
        high_max = self.data['high'].rolling(window=period).max()
        low_min = self.data['low'].rolling(window=period).min()
        value = 2 * ((self['close'] - low_min) / (high_max - low_min) - 0.5)
        trend_detector = 0.5 * np.log((1 + value) / (1 - value))
        return trend_detector

    @staticmethod
    def ehlers_fractal_dimension(self, period=14):
        # Ehlers Fractal Dimension
        high_max = self.data['high'].rolling(window=period).max()
        low_min = self.data['low'].rolling(window=period).min()
        fractal_dimension = (self['close'] - low_min) / (high_max - low_min)
        return fractal_dimension

    @staticmethod
    def ehlers_super_smoother_filter(self, period=14):
        # Ehlers Super Smoother Filter
        alpha = 2 / (period + 1)
        smooth = [self.data['close'].iloc[0]]
        for i in range(1, len(self)):
            smooth.append(alpha * self.data['close'].iloc[i] + (1 - alpha) * smooth[-1])
        return pd.Series(smooth, index=self.data.index)

    @staticmethod
    def jurik_moving_average(self, period=14):
        # Jurik Moving Average
        alpha = 2 / (period + 1)
        jma = [self.data['close'].iloc[0]]
        for i in range(1, len(self)):
            jma.append(alpha * self.data['close'].iloc[i] + (1 - alpha) * jma[-1])
        return pd.Series(jma, index=self.data.index)

    @staticmethod
    def jurik_volatility_bands(self, period=14):
        # Jurik Volatility Bands
        alpha = 2 / (period + 1)
        jma = CustomIndicators.jurik_moving_average(self, period)
        std = self.data['close'].rolling(window=period).std()
        upper_band = jma + (2 * std)
        lower_band = jma - (2 * std)
        return upper_band, lower_band

    @staticmethod
    def jurik_volatility_indicator(self, period=14):
        # Jurik Volatility Indicator
        alpha = 2 / (period + 1)
        jma = CustomIndicators.jurik_moving_average(self, period)
        std = self.data['close'].rolling(window=period).std()
        jvi = (self['close'] - jma) / std
        return jvi

    @staticmethod
    def jurik_rsx(self, period=14):
        # Jurik RSX
        alpha = 2 / (period + 1)
        jma = CustomIndicators.jurik_moving_average(self, period)
        rsx = (self['close'] - jma) / jma
        return rsx

    @staticmethod
    def mesa_adaptive_moving_average(self, period=14):
        # MESA Adaptive Moving Average
        alpha = 2 / (period + 1)
        mama = [self.data['close'].iloc[0]]
        for i in range(1, len(self)):
            mama.append(alpha * self.data['close'].iloc[i] + (1 - alpha) * mama[-1])
        return pd.Series(mama, index=self.data.index)

    @staticmethod
    def mesa_sine_wave(self, period=14):
        # MESA Sine Wave
        alpha = 2 / (period + 1)
        sine_wave = [np.sin(self['close'].iloc[0])]
        for i in range(1, len(self)):
            sine_wave.append(alpha * np.sin(self['close'].iloc[i]) + (1 - alpha) * sine_wave[-1])
        return pd.Series(sine_wave, index=self.data.index)

    @staticmethod
    def hilbert_transform_instantaneous_trendline(self, period=14):
        # Hilbert Transform - Instantaneous Trendline
        alpha = 2 / (period + 1)
        trendline = [self.data['close'].iloc[0]]
        for i in range(1, len(self)):
            trendline.append(alpha * self.data['close'].iloc[i] + (1 - alpha) * trendline[-1])
        return pd.Series(trendline, index=self.data.index)

    @staticmethod
    def hilbert_transform_dominant_cycle_period(self, period=14):
        # Hilbert Transform - Dominant Cycle Period
        alpha = 2 / (period + 1)
        dominant_cycle = [self.data['close'].iloc[0]]
        for i in range(1, len(self)):
            dominant_cycle.append(alpha * self.data['close'].iloc[i] + (1 - alpha) * dominant_cycle[-1])
        return pd.Series(dominant_cycle, index=self.data.index)

    @staticmethod
    def hilbert_transform_dominant_cycle_phase(self, period=14):
        # Hilbert Transform - Dominant Cycle Phase
        alpha = 2 / (period + 1)
        dominant_cycle_phase = [self.data['close'].iloc[0]]
        for i in range(1, len(self)):
            dominant_cycle_phase.append(alpha * self.data['close'].iloc[i] + (1 - alpha) * dominant_cycle_phase[-1])
        return pd.Series(dominant_cycle_phase, index=self.data.index)

    @staticmethod
    def hilbert_transform_sinewave(self, period=14):
        # Hilbert Transform - Sinewave
        alpha = 2 / (period + 1)
        sine_wave = [np.sin(self['close'].iloc[0])]
        for i in range(1, len(self)):
            sine_wave.append(alpha * np.sin(self['close'].iloc[i]) + (1 - alpha) * sine_wave[-1])
        return pd.Series(sine_wave, index=self.data.index)

    @staticmethod
    def schaff_trend_cycle(self, short_period=23, long_period=50, cycle_period=10):
        # Schaff Trend Cycle
        macd = MomentumIndicators.moving_average_convergence_divergence(self['close'], slow=long_period, fast=short_period)[0]
        fastk = MomentumIndicators.stochastic_oscillator(macd, period=cycle_period)
        slowd = MomentumIndicators.stochastic_oscillator(fastk, period=cycle_period)
        stc = slowd
        return stc
