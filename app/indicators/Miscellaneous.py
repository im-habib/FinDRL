import numpy as np
import pandas as pd

# Miscellaneous Indicators
class MiscIndicators:
    def __init__(self, data):
        self.data = data

    @staticmethod
    def coppock_curve(self, short_period=11, long_period=14, wma_period=10):
        # Coppock Curve = WMA of (ROC(long_period) + ROC(short_period))
        roc1 = MomentumIndicators.rate_of_change(self.data['close'], period=long_period)
        roc2 = MomentumIndicators.rate_of_change(self.data['close'], period=short_period)
        coppock_curve = TrendIndicators.weighted_moving_average(roc1 + roc2, period=wma_period)
        return coppock_curve

    @staticmethod
    def ulcer_index(self, period=14):
        # Ulcer Index = sqrt(mean((maximum drawdown)^2))
        max_close = self.data['close'].rolling(window=period).max()
        drawdown = self.data['close'] / max_close - 1
        ulcer_index = np.sqrt((drawdown ** 2).mean())
        return ulcer_index

    @staticmethod
    def market_profile(self):
        # Market Profile = Histogram of volume traded at each price level
        market_profile = self.data['volume'] * (self.data['high'] - self.data['low'])
        return market_profile

    @staticmethod
    def relative_strength_comparative(self):
        # Relative Strength Comparative = (Price1 / Price2)
        rsc = self.data1['close'] / self.data2['close']
        return rsc

    @staticmethod
    def moving_average_comparative(self, period=14):
        # Moving Average Comparative = (SMA1 - SMA2)
        sma1 = TrendIndicators.simple_moving_average(self.data1['close'], period)
        sma2 = TrendIndicators.simple_moving_average(self.data2['close'], period)
        mac = sma1 - sma2
        return mac

    @staticmethod
    def dynamic_momentum_index(self, period=14):
        # Dynamic Momentum Index = (Close - Lowest Low) / (Highest High - Lowest Low)
        highest_high = self.data['high'].rolling(window=period).max()
        lowest_low = self.data['low'].rolling(window=period).min()
        dmi = (self.data['close'] - lowest_low) / (highest_high - lowest_low)
        return dmi

    @staticmethod
    def center_of_gravity(self, period=14):
        # Center of Gravity = (sum of weighted self.data) / (sum of weights)
        weights = np.arange(1, period + 1)
        cog = self.data['close'].rolling(window=period).apply(lambda x: np.sum(x * weights) / np.sum(weights), raw=True)
        return cog

    @staticmethod
    def efficiency_ratio(self, period=14):
        # Efficiency Ratio = (Change in closing price) / (Sum of absolute changes)
        price_change = self.data['close'].diff(period).abs().sum()
        total_change = self.data['close'].diff().abs().rolling(window=period).sum()
        er = price_change / total_change
        return er

    @staticmethod
    def gopalakrishnan_range_index(self, period=14):
        # Gopalakrishnan Range Index = (Max High - Min Low) / (Max Close - Min Close)
        max_high = self.data['high'].rolling(window=period).max()
        min_low = self.data['low'].rolling(window=period).min()
        max_close = self.data['close'].rolling(window=period).max()
        min_close = self.data['close'].rolling(window=period).min()
        gapo = (max_high - min_low) / (max_close - min_close)
        return gapo

    @staticmethod
    def least_squares_moving_average(self, period=14):
        # Least Squares Moving Average = Sum of (price - mean price)^2 / n
        lsma = self.data['close'].rolling(window=period).apply(lambda x: np.sum((x - x.mean()) ** 2) / len(x), raw=True)
        return lsma

    @staticmethod
    def z_score(self, period=14):
        # Z-Score = (Close - Mean Close) / Standard Deviation of Close
        mean_close = self.data['close'].rolling(window=period).mean()
        std_close = self.data['close'].rolling(window=period).std()
        z_score = (self.data['close'] - mean_close) / std_close
        return z_score

    @staticmethod
    def mcclellan_oscillator(self, short_period=19, long_period=39):
        # McClellan Oscillator = Short EMA - Long EMA
        short_ema = self.data['close'].ewm(span=short_period, min_periods=short_period).mean()
        long_ema = self.data['close'].ewm(span=long_period, min_periods=long_period).mean()
        mcclellan_oscillator = short_ema - long_ema
        return mcclellan_oscillator

    @staticmethod
    def mcclellan_summation_index(self, short_period=19, long_period=39):
        # McClellan Summation Index = Sum of McClellan Oscillator
        mcclellan_oscillator = MiscIndicators.mcclellan_oscillator(self, short_period, long_period)
        mcclellan_summation_index = mcclellan_oscillator.cumsum()
        return mcclellan_summation_index

    @staticmethod
    def swing_chart(self):
        # Swing Chart
        swing = []
        direction = 'up'
        for i in range(1, len(self.data)):
            if direction == 'up':
                if self.data['close'].iloc[i] >= self.data['close'].iloc[i-1]:
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
                else:
                    direction = 'down'
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
            else:
                if self.data['close'].iloc[i] <= self.data['close'].iloc[i-1]:
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
                else:
                    direction = 'up'
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
        return pd.DataFrame(swing, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def swing_points(self):
        # Swing Points
        swing_points = []
        for i in range(1, len(self.data)):
            swing_points.append((self.data.index[i], self.data['close'].iloc[i] - self.data['close'].iloc[i-1]))
        return pd.DataFrame(swing_points, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def trend_intensity_index(self, period=14):
        # Trend Intensity Index = (Sum of Up Closes) / (Sum of Up Closes + Sum of Down Closes)
        up_closes = self.data['close'].diff().where(self.data['close'].diff() > 0, 0).rolling(window=period).sum()
        down_closes = self.data['close'].diff().where(self.data['close'].diff() < 0, 0).rolling(window=period).sum()
        tii = up_closes / (up_closes + down_closes)
        return tii

    @staticmethod
    def z_score_indicator(self, period=14):
        # Z-Score Indicator = (Close - Mean Close) / Standard Deviation of Close
        mean_close = self.data['close'].rolling(window=period).mean()
        std_close = self.data['close'].rolling(window=period).std()
        z_score = (self.data['close'] - mean_close) / std_close
        return z_score

    @staticmethod
    def price_volume_trend(self):
        # Price Volume Trend = Sum of (Volume * (Close - Previous Close) / Previous Close)
        pvt = self.data['volume'] * (self.data['close'] - self.data['close'].shift(1)) / self.data['close'].shift(1)
        return pvt.cumsum()

    @staticmethod
    def gann_swing(self):
        # Gann Swing Indicator
        swing = []
        direction = 'up'
        for i in range(1, len(self.data)):
            if direction == 'up':
                if self.data['close'].iloc[i] >= self.data['close'].iloc[i-1]:
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
                else:
                    direction = 'down'
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
            else:
                if self.data['close'].iloc[i] <= self.data['close'].iloc[i-1]:
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
                else:
                    direction = 'up'
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
        return pd.DataFrame(swing, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def gann_hi_lo_activator(self, period=14):
        # Gann Hi-Lo Activator
        gann_hi = self.data['high'].rolling(window=period).max()
        gann_lo = self.data['low'].rolling(window=period).min()
        return gann_hi, gann_lo

    @staticmethod
    def detrended_oscillator(self, period=14):
        # Detrended Oscillator = (Close - SMA) / Standard Deviation of Close
        sma = TrendIndicators.simple_moving_average(self.data['close'], period)
        std_close = self.data['close'].rolling(window=period).std()
        detrended = (self.data['close'] - sma) / std_close
        return detrended

    @staticmethod
    def price_oscillator(self, short_period=12, long_period=26):
        # Price Oscillator = Short EMA - Long EMA
        short_ema = self.data['close'].ewm(span=short_period, min_periods=short_period).mean()
        long_ema = self.data['close'].ewm(span=long_period, min_periods=long_period).mean()
        price_oscillator = short_ema - long_ema
        return price_oscillator

    @staticmethod
    def volume_oscillator(self, short_period=12, long_period=26):
        # Volume Oscillator = Short EMA - Long EMA
        short_ema = self.data['volume'].ewm(span=short_period, min_periods=short_period).mean()
        long_ema = self.data['volume'].ewm(span=long_period, min_periods=long_period).mean()
        volume_oscillator = short_ema - long_ema
        return volume_oscillator

    @staticmethod
    def projection_bands(self, period=14):
        # Projection Bands = High and Low Bands based on Linear Regression
        lrl = TrendIndicators.linear_regression_line(self.data['close'], period)
        std = self.data['close'].rolling(window=period).std()
        upper_band = lrl + std
        lower_band = lrl - std
        return upper_band, lower_band

    @staticmethod
    def projection_oscillator(self, period=14):
        # Projection Oscillator = (Close - Lower Band) / (Upper Band - Lower Band)
        upper_band, lower_band = MiscIndicators.projection_bands(self, period)
        projection_oscillator = (self.data['close'] - lower_band) / (upper_band - lower_band)
        return projection_oscillator

    @staticmethod
    def fractal_chaos_bands(self, period=14):
        # Fractal Chaos Bands = Highest High and Lowest Low over period
        upper_band = self.data['high'].rolling(window=period).max()
        lower_band = self.data['low'].rolling(window=period).min()
        return upper_band, lower_band

    @staticmethod
    def fractal_chaos_oscillator(self, period=14):
        # Fractal Chaos Oscillator = (Close - Lowest Low) / (Highest High - Lowest Low)
        highest_high = self.data['high'].rolling(window=period).max()
        lowest_low = self.data['low'].rolling(window=period).min()
        fractal_chaos = (self.data['close'] - lowest_low) / (highest_high - lowest_low)
        return fractal_chaos

    @staticmethod
    def hull_moving_average(self, period=14):
        # Hull Moving Average = WMA(2*WMA(n/2) - WMA(n)), sqrt(n)
        half_period = int(period / 2)
        sqrt_period = int(np.sqrt(period))
        wma_half = TrendIndicators.weighted_moving_average(self.data['close'], period=half_period)
        wma_full = TrendIndicators.weighted_moving_average(self.data['close'], period=period)
        hull = TrendIndicators.weighted_moving_average(2 * wma_half - wma_full, period=sqrt_period)
        return hull

    @staticmethod
    def regression_weighted_moving_average(self, period=14):
        # Regression Weighted Moving Average = (Sum of weighted self.data) / (Sum of weights)
        weights = np.arange(1, period + 1)
        rwma = self.data['close'].rolling(window=period).apply(lambda x: np.sum(x * weights) / np.sum(weights), raw=True)
        return rwma

    @staticmethod
    def sine_weighted_moving_average(self, period=14):
        # Sine Weighted Moving Average = (Sum of sine-weighted self.data) / (Sum of sine weights)
        weights = np.sin(np.linspace(0, np.pi, period))
        swma = self.data['close'].rolling(window=period).apply(lambda x: np.sum(x * weights) / np.sum(weights), raw=True)
        return swma

    @staticmethod
    def zero_lag_exponential_moving_average(self, period=14):
        # Zero Lag Exponential Moving Average = EMA with zero lag
        ema = self.data['close'].ewm(span=period, min_periods=period).mean()
        zlema = 2 * ema - ema.shift(1)
        return zlema

    @staticmethod
    def filtered_moving_average(self, period=14):
        # Filtered Moving Average = EMA with additional filtering
        alpha = 2 / (period + 1)
        fma = [self.data['close'].iloc[0]]
        for i in range(1, len(self.data)):
            fma.append(alpha * self.data['close'].iloc[i] + (1 - alpha) * fma[-1])
        return pd.Series(fma, index=self.data.index)

    @staticmethod
    def displaced_moving_average(self, period=14, displacement=3):
        # Displaced Moving Average = SMA shifted by a number of periods
        sma = TrendIndicators.simple_moving_average(self.data['close'], period)
        dma = sma.shift(displacement)
        return dma

    @staticmethod
    def range_action_verification_index(self, period=14):
        # Range Action Verification Index = (High - Low) / Close
        rvi = (self.data['high'] - self.data['low']) / self.data['close']
        return rvi.rolling(window=period).mean()

    @staticmethod
    def mcClellan_oscillator(self, short_period=19, long_period=39):
        # McClellan Oscillator = Short EMA - Long EMA
        short_ema = self.data['close'].ewm(span=short_period, min_periods=short_period).mean()
        long_ema = self.data['close'].ewm(span=long_period, min_periods=long_period).mean()
        mcClellan_oscillator = short_ema - long_ema
        return mcClellan_oscillator

    @staticmethod
    def mcClellan_summation_index(self, short_period=19, long_period=39):
        # McClellan Summation Index = Sum of McClellan Oscillator
        mcClellan_oscillator = MiscIndicators.mcClellan_oscillator(self, short_period, long_period)
        mcClellan_summation_index = mcClellan_oscillator.cumsum()
        return mcClellan_summation_index

    @staticmethod
    def trend_intensity_index(self, period=14):
        # Trend Intensity Index = (Sum of Up Closes) / (Sum of Up Closes + Sum of Down Closes)
        up_closes = self.data['close'].diff().where(self.data['close'].diff() > 0, 0).rolling(window=period).sum()
        down_closes = self.data['close'].diff().where(self.data['close'].diff() < 0, 0).rolling(window=period).sum()
        tii = up_closes / (up_closes + down_closes)
        return tii

    @staticmethod
    def squeeze_momentum_indicator(self, period=20, multiplier=2):
        # Squeeze Momentum Indicator
        upper_band, lower_band = VolatilityIndicators.bollinger_bands(self, period, multiplier)
        keltner_upper, keltner_lower = VolatilityIndicators.keltner_channels(self, period, multiplier)
        squeeze_on = (lower_band > keltner_lower) & (upper_band < keltner_upper)
        return squeeze_on

    @staticmethod
    def adaptive_price_zone(self, period=14):
        # Adaptive Price Zone = SMA +/- (2 * ATR)
        sma = TrendIndicators.simple_moving_average(self.data['close'], period)
        atr = VolatilityIndicators.average_true_range(self, period)
        upper_band = sma + (2 * atr)
        lower_band = sma - (2 * atr)
        return upper_band, lower_band

    @staticmethod
    def fractal_chaos_bands(self, period=14):
        # Fractal Chaos Bands = Highest High and Lowest Low over period
        upper_band = self.data['high'].rolling(window=period).max()
        lower_band = self.data['low'].rolling(window=period).min()
        return upper_band, lower_band

    @staticmethod
    def fractal_chaos_oscillator(self, period=14):
        # Fractal Chaos Oscillator = (Close - Lowest Low) / (Highest High - Lowest Low)
        highest_high = self.data['high'].rolling(window=period).max()
        lowest_low = self.data['low'].rolling(window=period).min()
        fractal_chaos = (self.data['close'] - lowest_low) / (highest_high - lowest_low)
        return fractal_chaos

    @staticmethod
    def projection_bands(self, period=14):
        # Projection Bands = High and Low Bands based on Linear Regression
        lrl = TrendIndicators.linear_regression_line(self.data['close'], period)
        std = self.data['close'].rolling(window=period).std()
        upper_band = lrl + std
        lower_band = lrl - std
        return upper_band, lower_band

    @staticmethod
    def projection_oscillator(self, period=14):
        # Projection Oscillator = (Close - Lower Band) / (Upper Band - Lower Band)
        upper_band, lower_band = MiscIndicators.projection_bands(self, period)
        projection_oscillator = (self.data['close'] - lower_band) / (upper_band - lower_band)
        return projection_oscillator

    @staticmethod
    def coppock_curve(self, short_period=11, long_period=14, wma_period=10):
        # Coppock Curve = WMA of (ROC(long_period) + ROC(short_period))
        roc1 = MomentumIndicators.rate_of_change(self.data['close'], period=long_period)
        roc2 = MomentumIndicators.rate_of_change(self.data['close'], period=short_period)
        coppock_curve = TrendIndicators.weighted_moving_average(roc1 + roc2, period=wma_period)
        return coppock_curve

    @staticmethod
    def relative_strength_comparative(self):
        # Relative Strength Comparative = (Price1 / Price2)
        rsc = self.data1['close'] / self.data2['close']
        return rsc

    @staticmethod
    def moving_average_comparative(self, period=14):
        # Moving Average Comparative = (SMA1 - SMA2)
        sma1 = TrendIndicators.simple_moving_average(self.data1['close'], period)
        sma2 = TrendIndicators.simple_moving_average(self.data2['close'], period)
        mac = sma1 - sma2
        return mac

    @staticmethod
    def dynamic_momentum_index(self, period=14):
        # Dynamic Momentum Index = (Close - Lowest Low) / (Highest High - Lowest Low)
        highest_high = self.data['high'].rolling(window=period).max()
        lowest_low = self.data['low'].rolling(window=period).min()
        dmi = (self.data['close'] - lowest_low) / (highest_high - lowest_low)
        return dmi

    @staticmethod
    def efficiency_ratio(self, period=14):
        # Efficiency Ratio = (Change in closing price) / (Sum of absolute changes)
        price_change = self.data['close'].diff(period).abs().sum()
        total_change = self.data['close'].diff().abs().rolling(window=period).sum()
        er = price_change / total_change
        return er

    @staticmethod
    def gopalakrishnan_range_index(self, period=14):
        # Gopalakrishnan Range Index = (Max High - Min Low) / (Max Close - Min Close)
        max_high = self.data['high'].rolling(window=period).max()
        min_low = self.data['low'].rolling(window=period).min()
        max_close = self.data['close'].rolling(window=period).max()
        min_close = self.data['close'].rolling(window=period).min()
        gapo = (max_high - min_low) / (max_close - min_close)
        return gapo

    @staticmethod
    def least_squares_moving_average(self, period=14):
        # Least Squares Moving Average = Sum of (price - mean price)^2 / n
        lsma = self.data['close'].rolling(window=period).apply(lambda x: np.sum((x - x.mean()) ** 2) / len(x), raw=True)
        return lsma

    @staticmethod
    def z_score(self, period=14):
        # Z-Score = (Close - Mean Close) / Standard Deviation of Close
        mean_close = self.data['close'].rolling(window=period).mean()
        std_close = self.data['close'].rolling(window=period).std()
        z_score = (self.data['close'] - mean_close) / std_close
        return z_score

    @staticmethod
    def z_score_indicator(self, period=14):
        # Z-Score Indicator = (Close - Mean Close) / Standard Deviation of Close
        mean_close = self.data['close'].rolling(window=period).mean()
        std_close = self.data['close'].rolling(window=period).std()
        z_score = (self.data['close'] - mean_close) / std_close
        return z_score

    @staticmethod
    def price_volume_trend(self):
        # Price Volume Trend = Sum of (Volume * (Close - Previous Close) / Previous Close)
        pvt = self.data['volume'] * (self.data['close'] - self.data['close'].shift(1)) / self.data['close'].shift(1)
        return pvt.cumsum()

    @staticmethod
    def swing_chart(self):
        # Swing Chart
        swing = []
        direction = 'up'
        for i in range(1, len(self.data)):
            if direction == 'up':
                if self.data['close'].iloc[i] >= self.data['close'].iloc[i-1]:
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
                else:
                    direction = 'down'
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
            else:
                if self.data['close'].iloc[i] <= self.data['close'].iloc[i-1]:
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
                else:
                    direction = 'up'
                    swing.append((self.data.index[i], self.data['close'].iloc[i]))
        return pd.DataFrame(swing, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def swing_points(self):
        # Swing Points
        swing_points = []
        for i in range(1, len(self.data)):
            swing_points.append((self.data.index[i], self.data['close'].iloc[i] - self.data['close'].iloc[i-1]))
        return pd.DataFrame(swing_points, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def trend_intensity_index(self, period=14):
        # Trend Intensity Index = (Sum of Up Closes) / (Sum of Up Closes + Sum of Down Closes)
        up_closes = self.data['close'].diff().where(self.data['close'].diff() > 0, 0).rolling(window=period).sum()
        down_closes = self.data['close'].diff().where(self.data['close'].diff() < 0, 0).rolling(window=period).sum()
        tii = up_closes / (up_closes + down_closes)
        return tii
