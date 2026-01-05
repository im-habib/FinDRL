import numpy as np
import pandas as pd
from indicators.base import Indicator

# Support/Resistance and Overlay Indicators

class RainbowMA(Indicator):
    def __init__(self, data, max_period=10):
        super().__init__(data)
        self.max_period = max_period

    def calculate(self):
        """
        Rainbow Moving Average
        Series of moving averages with increasing periods
        """
        rainbow_ma = pd.DataFrame(index=self.data.index)
        for i in range(1, self.max_period + 1):
            rainbow_ma[f'MA_{i}'] = self.data['Close'].rolling(window=i).mean()
        return rainbow_ma

class AccelerationBands(Indicator):
    def __init__(self, data, window=20):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Acceleration Bands
        Upper Band = (High * (1 + 4 * (High - Low) / (High + Low)))
        Lower Band = (Low * (1 - 4 * (High - Low) / (High + Low)))
        """
        high_low_range = self.data['High'] - self.data['Low']
        high_low_sum = self.data['High'] + self.data['Low']
        upper_band = self.data['High'] * (1 + 4 * (high_low_range / high_low_sum))
        lower_band = self.data['Low'] * (1 - 4 * (high_low_range / high_low_sum))
        return upper_band, lower_band

class DisparityIndex(Indicator):
    def __init__(self, data, window=14):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Disparity Index
        Disparity Index = (Close - SMA) / SMA * 100
        """
        sma = self.data['Close'].rolling(window=self.window).mean()
        disparity_index = (self.data['Close'] - sma) / sma * 100
        return disparity_index

class SqueezeMomentumIndicator(Indicator):
    def __init__(self, data, bollinger_window=20, keltner_window=20):
        super().__init__(data)
        self.bollinger_window = bollinger_window
        self.keltner_window = keltner_window

    def calculate(self):
        """
        Squeeze Momentum Indicator
        Squeeze = Bollinger Bands - Keltner Channels
        """
        std = self.data['Close'].rolling(window=self.bollinger_window).std()
        bollinger_upper = self.data['Close'].rolling(window=self.bollinger_window).mean() + (std * 2)
        bollinger_lower = self.data['Close'].rolling(window=self.bollinger_window).mean() - (std * 2)
        keltner_upper = self.data['Close'].rolling(window=self.keltner_window).mean() + (self.data['Close'].rolling(window=self.keltner_window).apply(lambda x: x.max() - x.min()))
        keltner_lower = self.data['Close'].rolling(window=self.keltner_window).mean() - (self.data['Close'].rolling(window=self.keltner_window).apply(lambda x: x.max() - x.min()))
        squeeze_momentum = bollinger_upper - keltner_upper - (bollinger_lower - keltner_lower)
        return squeeze_momentum

class RelativeVigorIndex(Indicator):
    def __init__(self, data, window=10):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Relative Vigor Index (RVI)
        RVI = (Close - Open) / (High - Low)
        """
        rvi = ((self.data['Close'] - self.data['Open']) / (self.data['High'] - self.data['Low'])).rolling(window=self.window).mean()
        return rvi

class PriceMomentumOscillator(Indicator):
    def __init__(self, data, window=35):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Price Momentum Oscillator (PMO)
        PMO = 10 * EMA_35(ROC_35)
        """
        roc = self.data['Close'].diff(self.window) / self.data['Close'].shift(self.window)
        pmo = 10 * roc.ewm(span=self.window, adjust=False).mean()
        return pmo

class FisherTransform(Indicator):
    def __init__(self, data, window=10):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Fisher Transform
        Fisher Transform = 0.5 * log((1 + Normalized Price) / (1 - Normalized Price))
        """
        max_price = self.data['High'].rolling(window=self.window).max()
        min_price = self.data['Low'].rolling(window=self.window).min()
        normalized_price = (2 * ((self.data['Close'] - min_price) / (max_price - min_price))) - 1
        fisher_transform = 0.5 * np.log((1 + normalized_price) / (1 - normalized_price))
        return fisher_transform

class EhlersFisherTransform(Indicator):
    def __init__(self, data, window=10):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Ehlers Fisher Transform
        Fisher Transform = 0.5 * log((1 + Normalized Price) / (1 - Normalized Price))
        """
        max_price = self.data['High'].rolling(window=self.window).max()
        min_price = self.data['Low'].rolling(window=self.window).min()
        normalized_price = (2 * ((self.data['Close'] - min_price) / (max_price - min_price))) - 1
        fisher_transform = 0.5 * np.log((1 + normalized_price) / (1 - normalized_price))
        return fisher_transform

class EhlersEarlyOnsetTrendDetector(Indicator):
    def __init__(self, data, window=10):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Ehlers Early Onset Trend Detector
        Trend Detector = EMA of Close - EMA of EMA of Close
        """
        ema1 = self.data['Close'].ewm(span=self.window, adjust=False).mean()
        ema2 = ema1.ewm(span=self.window, adjust=False).mean()
        trend_detector = ema1 - ema2
        return trend_detector

class EhlersFractalDimension(Indicator):
    def __init__(self, data, window=10):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Ehlers Fractal Dimension
        Fractal Dimension = log(N1 + N2) - log(N1) / log(2)
        """
        p1 = self.data['Close'].diff(self.window).abs()
        p2 = self.data['Close'].diff(self.window // 2).abs()
        N1 = p1.rolling(window=self.window).mean()
        N2 = p2.rolling(window=self.window).mean()
        fractal_dimension = (np.log(N1 + N2) - np.log(N1)) / np.log(2)
        return fractal_dimension

class EhlersSuperSmootherFilter(Indicator):
    def __init__(self, data, window=10):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Ehlers Super Smoother Filter
        Super Smoother Filter = EMA of Close
        """
        super_smoother = self.data['Close'].ewm(span=self.window, adjust=False).mean()
        return super_smoother

class JurikMovingAverage(Indicator):
    def __init__(self, data, window=14):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Jurik Moving Average (JMA)
        JMA = Price * (2 / (window + 1)) + JMA_yesterday * (1 - (2 / (window + 1)))
        """
        jma = self.data['Close'].ewm(span=self.window, adjust=False).mean()
        return jma

class JurikVolatilityBands(Indicator):
    def __init__(self, data, window=14):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Jurik Volatility Bands
        Upper Band = EMA + (ATR * multiplier)
        Lower Band = EMA - (ATR * multiplier)
        """
        atr = self.data['High'].rolling(window=self.window).max() - self.data['Low'].rolling(window=self.window).min()
        upper_band = self.data['Close'].ewm(span=self.window, adjust=False).mean() + (atr * 1.5)
        lower_band = self.data['Close'].ewm(span=self.window, adjust=False).mean() - (atr * 1.5)
        return upper_band, lower_band

class JurikVolatilityIndicator(Indicator):
    def __init__(self, data, window=14):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Jurik Volatility Indicator
        Volatility Indicator = EMA of High-Low Range
        """
        volatility = (self.data['High'] - self.data['Low']).ewm(span=self.window, adjust=False).mean()
        return volatility

class JurikRSX(Indicator):
    def __init__(self, data, window=14):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Jurik RSX
        RSX = Smoothed RSI
        """
        delta = self.data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=self.window).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=self.window).mean()
        RS = gain / loss
        RSI = 100 - (100 / (1 + RS))
        rsx = RSI.ewm(span=self.window, adjust=False).mean()
        return rsx

class MESAAdaptiveMovingAverage(Indicator):
    def __init__(self, data, window=14):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        MESA Adaptive Moving Average (MAMA)
        MAMA = Price * (2 / (window + 1)) + MAMA_yesterday * (1 - (2 / (window + 1)))
        """
        mama = self.data['Close'].ewm(span=self.window, adjust=False).mean()
        return mama

class MESASineWave(Indicator):
    def __init__(self, data, window=14):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        MESA Sine Wave
        Sine Wave = Sine of Dominant Cycle
        """
        sine_wave = self.data['Close'].rolling(window=self.window).apply(lambda x: np.sin(np.mean(np.fft.fft(x))))
        return sine_wave

class HilbertTransformInstantaneousTrendline(Indicator):
    def __init__(self, data, window=14):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Hilbert Transform - Instantaneous Trendline
        Trendline = EMA of Close
        """
        trendline = self.data['Close'].ewm(span=self.window, adjust=False).mean()
        return trendline

class HilbertTransformDominantCyclePeriod(Indicator):
    def __init__(self, data, window=14):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Hilbert Transform - Dominant Cycle Period
        Cycle Period = Average Dominant Cycle Period
        """
        dominant_cycle_period = self.data['Close'].rolling(window=self.window).apply(lambda x: np.mean(np.diff(np.where(x == np.max(x)))))
        return dominant_cycle_period

class HilbertTransformDominantCyclePhase(Indicator):
    def __init__(self, data, window=14):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Hilbert Transform - Dominant Cycle Phase
        Cycle Phase = Angle of Dominant Cycle
        """
        dominant_cycle_phase = self.data['Close'].rolling(window=self.window).apply(lambda x: np.angle(np.mean(np.fft.fft(x))))
        return dominant_cycle_phase

class HilbertTransformSinewave(Indicator):
    def __init__(self, data, window=14):
        super().__init__(data)
        self.window = window

    def calculate(self):
        """
        Hilbert Transform - Sinewave
        Sinewave = Sine of Dominant Cycle
        """
        sinewave = self.data['Close'].rolling(window=self.window).apply(lambda x: np.sin(np.mean(np.fft.fft(x))))
        return sinewave

class SchaffTrendCycle(Indicator):
    def __init__(self, data, short_window=10, long_window=20):
        super().__init__(data)
        self.short_window = short_window
        self.long_window = long_window

    def calculate(self):
        """
        Schaff Trend Cycle (STC)
        STC = 100 * (EMA_10 - EMA_20) / EMA_20
        """
        short_ema = self.data['Close'].ewm(span=self.short_window, adjust=False).mean()
        long_ema = short_ema.ewm(span=self.long_window, adjust=False).mean()
        stc = 100 * (short_ema - long_ema) / long_ema
        return stc

# Example Usage
if __name__ == "__main__":
    # Sample data
    dates = pd.date_range(start='2020-01-01', periods=100)
    data = pd.DataFrame(index=dates)
    data['Open'] = np.random.randn(100).cumsum() + 100
    data['High'] = data['Open'] + (np.random.rand(100) * 10)
    data['Low'] = data['Open'] - (np.random.rand(100) * 10)
    data['Close'] = data[['Open', 'High', 'Low']].mean(axis=1) + (np.random.rand(100) * 5 - 2.5)
    data['Volume'] = np.random.randint(1, 1000, size=100)

    # Instantiate and calculate each indicator
    indicators = [
        RainbowMA(data),
        AccelerationBands(data),
        DisparityIndex(data),
        SqueezeMomentumIndicator(data),
        RelativeVigorIndex(data),
        PriceMomentumOscillator(data),
        FisherTransform(data),
        EhlersFisherTransform(data),
        EhlersEarlyOnsetTrendDetector(data),
        EhlersFractalDimension(data),
        EhlersSuperSmootherFilter(data),
        JurikMovingAverage(data),
        JurikVolatilityBands(data),
        JurikVolatilityIndicator(data),
        JurikRSX(data),
        MESAAdaptiveMovingAverage(data),
        MESASineWave(data),
        HilbertTransformInstantaneousTrendline(data),
        HilbertTransformDominantCyclePeriod(data),
        HilbertTransformDominantCyclePhase(data),
        HilbertTransformSinewave(data),
        SchaffTrendCycle(data),
    ]

    for indicator in indicators:
        print(f"{indicator.__class__.__name__}:")
        print(indicator.calculate())
        print("\n")


# Example usage:
# df = pd.read_csv('data.csv')
# pp = PivotPoints(df)
# pp_values = pp.calculate()
# print(pp_values)
