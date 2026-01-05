import numpy as np
import pandas as pd
from indicators.base.CalcIndicator import Indicator
import pandas_ta as ta

# 2. Implement all Momentum indicators
class RSI(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

class MACD(Indicator):
    def __init__(self, short_period=12, long_period=26, signal_period=9):
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        short_ema = data['Close'].ewm(span=self.short_period, adjust=False).mean()
        long_ema = data['Close'].ewm(span=self.long_period, adjust=False).mean()
        macd = short_ema - long_ema
        signal_line = macd.ewm(span=self.signal_period, adjust=False).mean()
        return macd - signal_line

class BollingerBands(Indicator):
    def __init__(self, period=20, num_std=2):
        self.period = period
        self.num_std = num_std

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        rolling_mean = data['Close'].rolling(window=self.period).mean()
        rolling_std = data['Close'].rolling(window=self.period).std()
        upper_band = rolling_mean + (rolling_std * self.num_std)
        Lower_band = rolling_mean - (rolling_std * self.num_std)
        return pd.DataFrame({
            'upper_band': upper_band,
            'Lower_band': Lower_band,
            'middle_band': rolling_mean
        })

class Stochastic(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        Low_min = data['Low'].rolling(window=self.period).min()
        High_max = data['High'].rolling(window=self.period).max()
        stoch = 100 * (data['Close'] - Low_min) / (High_max - Low_min)
        return stoch

class CCI(Indicator):
    def __init__(self, period=20):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        rolling_mean = typical_price.rolling(window=self.period).mean()
        rolling_std = typical_price.rolling(window=self.period).std()
        cci = (typical_price - rolling_mean) / (0.015 * rolling_std)
        return cci

class ATR(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        tr = pd.DataFrame({
            'tr': [
                max(data['High'][i] - data['Low'][i],
                    abs(data['High'][i] - data['Close'][i-1]),
                    abs(data['Low'][i] - data['Close'][i-1])) for i in range(1, len(data))
            ]
        })
        atr = tr['tr'].rolling(window=self.period).mean()
        return atr

class PPO(Indicator):
    def __init__(self, fast_period=12, sLow_period=26):
        self.fast_period = fast_period
        self.sLow_period = sLow_period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        fast_ema = data['Close'].ewm(span=self.fast_period, adjust=False).mean()
        sLow_ema = data['Close'].ewm(span=self.sLow_period, adjust=False).mean()
        ppo = (fast_ema - sLow_ema) / sLow_ema * 100
        return ppo

class StochRSI(Indicator):
    def __init__(self, period=14, stoch_period=14):
        self.period = period
        self.stoch_period = stoch_period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        rsi = RSI(self.period).calculate(data)
        stoch_rsi = (rsi - rsi.rolling(window=self.stoch_period).min()) / (rsi.rolling(window=self.stoch_period).max() - rsi.rolling(window=self.stoch_period).min())
        return stoch_rsi * 100

# 3. Continue for all other Indicators
class AO(Indicator):
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # Awesome Oscillator
        ao = data['Close'].rolling(window=5).mean() - data['Close'].rolling(window=34).mean()
        return ao

class BOP(Indicator):
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # Balance of Power
        bop = (data['Close'] - data['Open']) / (data['High'] - data['Low'])
        return bop

class Bias(Indicator):
    def __init__(self, period=9):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        bias = (data['Close'] - data['Close'].rolling(window=self.period).mean()) / data['Close'].rolling(window=self.period).mean() * 100
        return bias

class Fisher(Indicator):
    def __init__(self, period=9):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        High_max = data['High'].rolling(window=self.period).max()
        Low_min = data['Low'].rolling(window=self.period).min()
        fisher = 0.5 * np.log((High_max + Low_min) / (data['Close'] - High_max))
        return fisher

class Brar(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        brar = (data['Close'].rolling(window=self.period).max() - data['Close'].rolling(window=self.period).min()) / \
               (data['High'] - data['Low'])
        return brar

class CG(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        cg = (data['High'] + data['Low']) / 2
        return cg

class CMO(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).sum()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).sum()
        cmo = (gain - loss) / (gain + loss) * 100
        return cmo

class Coppock(Indicator):
    def __init__(self, long_period=14, short_period=11, signal_period=10):
        self.long_period = long_period
        self.short_period = short_period
        self.signal_period = signal_period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        roc1 = data['Close'].pct_change(self.short_period) * 100
        roc2 = data['Close'].pct_change(self.long_period) * 100
        coppock = (roc1 + roc2).rolling(window=self.signal_period).sum()
        return coppock

class CTI(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        cti = data['Close'].diff().rolling(window=self.period).mean()
        return cti

class ER(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        er = (data['Close'] - data['Close'].shift(self.period)) / data['Close'].shift(self.period)
        return er

class Eri(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['Close'].diff(periods=self.period)

class Inertia(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        inertia = (data['Close'] - data['Close'].shift(self.period)) / data['Close'].shift(self.period)
        return inertia

class KDJ(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        Low_min = data['Low'].rolling(window=self.period).min()
        High_max = data['High'].rolling(window=self.period).max()
        rsv = 100 * (data['Close'] - Low_min) / (High_max - Low_min)
        k = rsv.ewm(span=3).mean()
        d = k.ewm(span=3).mean()
        j = 3 * k - 2 * d
        return j

class KST(Indicator):
    def __init__(self, periods=[10, 15, 20, 30], weights=[1, 1, 1, 1]):
        self.periods = periods
        self.weights = weights

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        kst = sum([data['Close'].diff(p).rolling(window=p).mean() * w for p, w in zip(self.periods, self.weights)])
        return kst

class PGO(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        pgo = (data['Close'] - data['Close'].shift(self.period)) / data['Close'].shift(self.period)
        return pgo

class PVO(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        pvo = (data['Close'].diff(periods=self.period) / data['Close'].shift(self.period)) * 100
        return pvo

class QQE(Indicator):
    def __init__(self, period=14, factor=4.236):
        self.period = period
        self.factor = factor

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        ema = data['Close'].ewm(span=self.period).mean()
        qqe = ema + self.factor * ema.rolling(window=self.period).std()
        return qqe

class ROC(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        roc = (data['Close'] - data['Close'].shift(self.period)) / data['Close'].shift(self.period) * 100
        return roc

class RSX(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).sum()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).sum()
        rsx = (gain / (gain + loss)) * 100
        return rsx

class RVGI(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        rvgi = (data['Close'] - data['Close'].shift(self.period)) / data['Close'].shift(self.period) * 100
        return rvgi

class Slope(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        slope = np.polyfit(np.arange(self.period), data['Close'][-self.period:], 1)[0]
        return slope

class SMI(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        smi = (data['Close'] - data['Close'].rolling(window=self.period).mean()) / \
              data['Close'].rolling(window=self.period).std()
        return smi

class Squeeze(Indicator):
    def __init__(self, period=20, num_std=2):
        self.period = period
        self.num_std = num_std

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        rolling_mean = data['Close'].rolling(window=self.period).mean()
        rolling_std = data['Close'].rolling(window=self.period).std()
        squeeze = (data['Close'] - rolling_mean) / rolling_std
        return squeeze

class SqueezePro(Indicator):
    def __init__(self, period=20, num_std=2):
        self.period = period
        self.num_std = num_std

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        rolling_mean = data['Close'].rolling(window=self.period).mean()
        rolling_std = data['Close'].rolling(window=self.period).std()
        squeeze_pro = (data['Close'] - rolling_mean) / (self.num_std * rolling_std)
        return squeeze_pro

class STC(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        stc = (data['Close'].diff(self.period) / data['Close'].shift(self.period)) * 100
        return stc

class TSI(Indicator):
    def __init__(self, long_period=25, short_period=13):
        self.long_period = long_period
        self.short_period = short_period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        tsi = data['Close'].diff().ewm(span=self.short_period).mean() / \
              data['Close'].diff().ewm(span=self.long_period).mean()
        return tsi

class TRIX(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        trix = data['Close'].pct_change().ewm(span=self.period).mean()
        return trix

class UO(Indicator):
    def __init__(self, short_period=7, medium_period=14, long_period=28):
        self.short_period = short_period
        self.medium_period = medium_period
        self.long_period = long_period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        uo = (
            (data['Close'] - data['Low']).rolling(window=self.short_period).sum() / (data['High'] - data['Low']).rolling(window=self.short_period).sum()
            * 0.33 +
            (data['Close'] - data['Low']).rolling(window=self.medium_period).sum() / (data['High'] - data['Low']).rolling(window=self.medium_period).sum()
            * 0.33 +
            (data['Close'] - data['Low']).rolling(window=self.long_period).sum() / (data['High'] - data['Low']).rolling(window=self.long_period).sum()
            * 0.34
        )
        return uo

class WillR(Indicator):
    def __init__(self, period=14):
        self.period = period

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        willr = (data['High'].rolling(window=self.period).max() - data['Close']) / (data['High'].rolling(window=self.period).max() - data['Low'].rolling(window=self.period).min()) * -100
        return willr

# # 3. Create a Context class
# class IndicatorContext:
#     def __init__(self, indicator: Indicator):
#         self._indicator = indicator

#     def set_indicator(self, indicator: Indicator):
#         self._indicator = indicator

#     def calculate_indicator(self, data: pd.DataFrame):
#         return self._indicator.calculate(data)

# # 4. Modify the `calculate_all_indicators` function to include the new indicators
# def calculate_all_indicators(data: pd.DataFrame):
#     indicators = [
#         RSI, MACD, BollingerBands,
#         Stochastic, CCI, ATR, PPO,
#         StochRSI, AO, BOP, Bias,
#         Fisher, Brar, CG, CMO,
#         Coppock, CTI, ER, Eri,
#         Inertia, KDJ, KST, PGO,
#         PVO, QQE, ROC, RSX,
#         RVGI, Slope, SMI, Squeeze,
#         SqueezePro, STC, TSI, TRIX,
#         UO, WillR
#     ]


#     results = {}
#     for indicator in indicators:
#         context = IndicatorContext(indicator)
#         results[indicator.__class__.__name__] = context.calculate_indicator(data)

#     return results

# # Sample data (replace with actual market data)
# data = pd.DataFrame({
#     'Close': np.random.rand(100) * 100,
#     'High': np.random.rand(100) * 100,
#     'Low': np.random.rand(100) * 100,
#     'Open': np.random.rand(100) * 100
# })

# # Calculate all indicators
# results = calculate_all_indicators(data)

# # Print the results
# for indicator_name, result in results.items():
#     print(f"{indicator_name}:")
#     print(result.tail(), "\n")