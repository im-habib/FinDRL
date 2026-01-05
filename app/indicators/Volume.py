import numpy as np
import pandas as pd
from indicators.base import Indicator

# Volume Indicators
class VolumeIndicators:
    def __init__(self, data):
        self.data = data

    @staticmethod
    def on_balance_volume(self):
        # OBV = Previous OBV + Volume if close > previous close
        # OBV = Previous OBV - Volume if close < previous close
        obv = [0]
        for i in range(1, len(self)):
            if self.data['close'][i] > self.data['close'][i-1]:
                obv.append(obv[-1] + self.data['volume'][i])
            elif self.data['close'][i] < self.data['close'][i-1]:
                obv.append(obv[-1] - self.data['volume'][i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=self.data.index)

    @staticmethod
    def chaikin_money_flow(self, period=20):
        # CMF = (Sum of ((Close - Low) - (High - Close)) / (High - Low) * Volume) / Sum of Volume over period
        mf_multiplier = ((self['close'] - self.data['low']) - (self['high'] - self.data['close'])) / (self['high'] - self.data['low'])
        mf_volume = mf_multiplier * self.data['volume']
        cmf = mf_volume.rolling(window=period).sum() / self.data['volume'].rolling(window=period).sum()
        return cmf

    @staticmethod
    def money_flow_index(self, period=14):
        # MFI = 100 - (100 / (1 + Money Flow Ratio))
        typical_price = (self['high'] + self.data['low'] + self.data['close']) / 3
        money_flow = typical_price * self.data['volume']
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(window=period).sum()
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(window=period).sum()
        money_flow_ratio = positive_flow / negative_flow
        mfi = 100 - (100 / (1 + money_flow_ratio))
        return mfi

    @staticmethod
    def accumulation_distribution_line(self):
        # ADL = Previous ADL + (Close - Low) - (High - Close) / (High - Low) * Volume
        adl = [0]
        for i in range(len(self)):
            mfm = ((self['close'][i] - self.data['low'][i]) - (self['high'][i] - self.data['close'][i])) / (self['high'][i] - self.data['low'][i])
            adl.append(adl[-1] + mfm * self.data['volume'][i])
        return pd.Series(adl[1:], index=self.data.index)

    @staticmethod
    def volume_price_trend(self):
        # VPT = Previous VPT + Volume * (Current Close - Previous Close) / Previous Close
        vpt = [0]
        for i in range(1, len(self)):
            vpt.append(vpt[-1] + self.data['volume'][i] * (self['close'][i] - self.data['close'][i-1]) / self.data['close'][i-1])
        return pd.Series(vpt, index=self.data.index)

    @staticmethod
    def klinger_volume_oscillator(self, short_period=34, long_period=55, signal_period=13):
        # KVO = Short EMA - Long EMA
        hlc = (self['high'] + self.data['low'] + self.data['close']) / 3
        trend = np.sign(hlc.diff())
        volume = self.data['volume'] * trend
        ema_short = volume.ewm(span=short_period, min_periods=short_period).mean()
        ema_long = volume.ewm(span=long_period, min_periods=long_period).mean()
        kvo = ema_short - ema_long
        signal = kvo.ewm(span=signal_period, min_periods=signal_period).mean()
        return kvo, signal

    @staticmethod
    def volume_oscillator(self, short_period=14, long_period=28):
        # VO = Short SMA - Long SMA
        short_sma = self.data['volume'].rolling(window=short_period).mean()
        long_sma = self.data['volume'].rolling(window=long_period).mean()
        vo = short_sma - long_sma
        return vo

    @staticmethod
    def volume_accumulation_oscillator(self):
        # VAO = Previous VAO + (Volume * (2 * (Close - Low) / (High - Low) - 1))
        vao = [0]
        for i in range(len(self)):
            vao.append(vao[-1] + self.data['volume'][i] * (2 * (self['close'][i] - self.data['low'][i]) / (self['high'][i] - self.data['low'][i]) - 1))
        return pd.Series(vao[1:], index=self.data.index)

    @staticmethod
    def weis_wave_volume(self):
        # WWV = Sum of volume for each swing
        wave = self.data['close'].diff().apply(lambda x: 'up' if x > 0 else ('down' if x < 0 else 'flat'))
        wwv = [self.data['volume'][0]]
        for i in range(1, len(self)):
            if wave[i] == wave[i-1]:
                wwv[-1] += self.data['volume'][i]
            else:
                wwv.append(self['volume'][i])
        return pd.Series(wwv, index=self.data.index[:len(wwv)])

    @staticmethod
    def chaikin_oscillator(self, short_period=3, long_period=10):
        # CO = ADL Short EMA - ADL Long EMA
        adl = VolumeIndicators.accumulation_distribution_line(self)
        adl_short_ema = adl.ewm(span=short_period, min_periods=short_period).mean()
        adl_long_ema = adl.ewm(span=long_period, min_periods=long_period).mean()
        co = adl_short_ema - adl_long_ema
        return co

    @staticmethod
    def demand_index(self, period=14):
        # DI = Sum of (up_volume * price_change) / Sum of (down_volume * price_change)
        price_change = self.data['close'].diff()
        up_volume = self.data['volume'].where(price_change > 0, 0)
        down_volume = self.data['volume'].where(price_change < 0, 0)
        di = up_volume.rolling(window=period).sum() / down_volume.rolling(window=period).sum()
        return di

    @staticmethod
    def intraday_intensity_index(self, period=21):
        # III = Sum of (Volume * (2 * (Close - Low) / (High - Low) - 1)) / Sum of Volume over period
        intraday_intensity = self.data['volume'] * (2 * (self['close'] - self.data['low']) / (self['high'] - self.data['low']) - 1)
        iii = intraday_intensity.rolling(window=period).sum() / self.data['volume'].rolling(window=period).sum()
        return iii

    @staticmethod
    def positive_volume_index(self):
        # PVI = Previous PVI + Volume if volume > previous volume
        # PVI = Previous PVI if volume <= previous volume
        pvi = [self.data['close'][0]]
        for i in range(1, len(self)):
            if self.data['volume'][i] > self.data['volume'][i-1]:
                pvi.append(pvi[-1] + self.data['volume'][i])
            else:
                pvi.append(pvi[-1])
        return pd.Series(pvi, index=self.data.index)

    @staticmethod
    def negative_volume_index(self):
        # NVI = Previous NVI + Volume if volume < previous volume
        # NVI = Previous NVI if volume >= previous volume
        nvi = [self.data['close'][0]]
        for i in range(1, len(self)):
            if self.data['volume'][i] < self.data['volume'][i-1]:
                nvi.append(nvi[-1] + self.data['volume'][i])
            else:
                nvi.append(nvi[-1])
        return pd.Series(nvi, index=self.data.index)

    @staticmethod
    def volume_weighted_average_price(self, period=14):
        # VWAP = Sum of (Typical Price * Volume) / Sum of Volume over period
        typical_price = (self['high'] + self.data['low'] + self.data['close']) / 3
        volume_sum = self.data['volume'].rolling(window=period).sum()
        vwap = (typical_price * self.data['volume']).rolling(window=period).sum() / volume_sum
        return vwap

    @staticmethod
    def volume_profile(self, bins=20):
        # Volume Profile = Histogram of volume traded at each price level
        hist, bin_edges = np.histogram(self['close'], bins=bins, weights=self.data['volume'])
        return pd.DataFrame({'Volume': hist}, index=pd.IntervalIndex.from_breaks(bin_edges))


# # Volume Indicators
# class OBV(Indicator):
#     # OBV = OBV(previous) + Volume (if Close > Close(previous)) or - Volume (if Close < Close(previous))
#     def calculate(self):
#         obv = np.where(self.data['Close'] > self.data['Close'].shift(1), self.data['Volume'],
#                        np.where(self.data['Close'] < self.data['Close'].shift(1), -self.data['Volume'], 0))
#         obv = obv.cumsum()
#         return obv

# class CMF(Indicator):
#     # CMF = Sum of ( (Close - Low) - (High - Close) ) / (High - Low) * Volume / Sum of Volume
#     def calculate(self, period=20):
#         mfv = ((self.data['Close'] - self.data['Low']) - (self.data['High'] - self.data['Close'])) / \
#               (self.data['High'] - self.data['Low']) * self.data['Volume']
#         cmf = mfv.rolling(window=period).sum() / self.data['Volume'].rolling(window=period).sum()
#         return cmf

# class MFI(Indicator):
#     # MFI = 100 - (100 / (1 + Money Flow Ratio))
#     def calculate(self, period=14):
#         typical_price = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
#         money_flow = typical_price * self.data['Volume']
#         positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
#         negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
#         money_flow_ratio = positive_flow.rolling(window=period).sum() / negative_flow.rolling(window=period).sum()
#         mfi = 100 - (100 / (1 + money_flow_ratio))
#         return mfi

# class ADL(Indicator):
#     # ADL = Previous ADL + ( (Close - Low) - (High - Close) ) / (High - Low) * Volume
#     def calculate(self):
#         adl = ((self.data['Close'] - self.data['Low']) - (self.data['High'] - self.data['Close'])) / \
#               (self.data['High'] - self.data['Low']) * self.data['Volume']
#         adl = adl.cumsum()
#         return adl

# class VPT(Indicator):
#     # VPT = Previous VPT + Volume * ( (Close - Close(previous)) / Close(previous) )
#     def calculate(self):
#         vpt = self.data['Volume'] * ((self.data['Close'] - self.data['Close'].shift(1)) / self.data['Close'].shift(1))
#         vpt = vpt.cumsum()
#         return vpt

# class KVO(Indicator):
#     # KVO = 34-period EMA of VPT - 55-period EMA of VPT
#     def calculate(self, short_period=34, long_period=55):
#         vpt = self.data['Volume'] * ((self.data['Close'] - self.data['Close'].shift(1)) / self.data['Close'].shift(1))
#         vpt = vpt.cumsum()
#         short_ema = vpt.ewm(span=short_period, adjust=False).mean()
#         long_ema = vpt.ewm(span=long_period, adjust=False).mean()
#         kvo = short_ema - long_ema
#         return kvo

# class VolumeOscillator(Indicator):
#     # Volume Oscillator = ((Short-term SMA of Volume - Long-term SMA of Volume) / Long-term SMA of Volume) * 100
#     def calculate(self, short_period=14, long_period=28):
#         short_sma = self.data['Volume'].rolling(window=short_period).mean()
#         long_sma = self.data['Volume'].rolling(window=long_period).mean()
#         volume_oscillator = ((short_sma - long_sma) / long_sma) * 100
#         return volume_oscillator

# class VolumeAccumulationOscillator(Indicator):
#     # Volume Accumulation Oscillator = (Close - Open) / (High - Low) * Volume
#     def calculate(self):
#         vao = (self.data['Close'] - self.data['Open']) / (self.data['High'] - self.data['Low']) * self.data['Volume']
#         vao = vao.cumsum()
#         return vao

# class WWV(Indicator):
#     # WWV = Sum of (Accumulation/Distribution) for each wave
#     def calculate(self):
#         ad = (self.data['Close'] - self.data['Low']) - (self.data['High'] - self.data['Close'])
#         ad = ad / (self.data['High'] - self.data['Low']) * self.data['Volume']
#         wwv = ad.cumsum()
#         return wwv

# class ChaikinOscillator(Indicator):
#     # Chaikin Oscillator = 3-period EMA of ADL - 10-period EMA of ADL
#     def calculate(self, short_period=3, long_period=10):
#         adl = ((self.data['Close'] - self.data['Low']) - (self.data['High'] - self.data['Close'])) / \
#               (self.data['High'] - self.data['Low']) * self.data['Volume']
#         adl = adl.cumsum()
#         short_ema = adl.ewm(span=short_period, adjust=False).mean()
#         long_ema = adl.ewm(span=long_period, adjust=False).mean()
#         chaikin_oscillator = short_ema - long_ema
#         return chaikin_oscillator

# class DemandIndex(Indicator):
#     # Demand Index = (Volume * Price Change) / (Volume Change * Price)
#     def calculate(self):
#         price_change = self.data['Close'].diff()
#         volume_change = self.data['Volume'].diff()
#         demand_index = (self.data['Volume'] * price_change) / (volume_change * self.data['Close'])
#         return demand_index

# class IntradayIntensityIndex(Indicator):
#     # III = (2 * Close - High - Low) / (High - Low) * Volume
#     def calculate(self):
#         iii = (2 * self.data['Close'] - self.data['High'] - self.data['Low']) / (self.data['High'] - self.data['Low']) * self.data['Volume']
#         return iii

# class PVI(Indicator):
#     # PVI = Previous PVI + ((Close - Close(previous)) / Close(previous)) * Volume (if Volume > Volume(previous))
#     def calculate(self):
#         pvi = np.where(self.data['Volume'] > self.data['Volume'].shift(1),
#                        (self.data['Close'] - self.data['Close'].shift(1)) / self.data['Close'].shift(1) * self.data['Volume'], 0)
#         pvi = pvi.cumsum()
#         return pvi

# class NVI(Indicator):
#     # NVI = Previous NVI + ((Close - Close(previous)) / Close(previous)) * Volume (if Volume < Volume(previous))
#     def calculate(self):
#         nvi = np.where(self.data['Volume'] < self.data['Volume'].shift(1),
#                        (self.data['Close'] - self.data['Close'].shift(1)) / self.data['Close'].shift(1) * self.data['Volume'], 0)
#         nvi = nvi.cumsum()
#         return nvi

# class VWAP(Indicator):
#     # VWAP = Cumulative (Typical Price * Volume) / Cumulative Volume
#     def calculate(self):
#         typical_price = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
#         vwap = (typical_price * self.data['Volume']).cumsum() / self.data['Volume'].cumsum()
#         return vwap

# class VolumeProfile(Indicator):
#     # Volume Profile = Histogram of volume traded at different price levels
#     def calculate(self, bins=20):
#         volume_profile = pd.cut(self.data['Close'], bins=bins).value_counts().sort_index()
#         return volume_profile

# # Example usage:
# # df = pd.read_csv('data.csv')
# # pp = PivotPoints(df)
# # pp_values = pp.calculate()
# # print(pp_values)
