import pandas_ta as ta
from utils.Utils import hoc_print
from indicators.base import Indicator

# Trend Indicators
class TrendIndicators(Indicator):
    def simple_moving_average(self, length=1):
        # SMA = Sum of self.data over period / period
        sma = ta.sma(self.data[self.check_field], length=length)
        hoc_print(sma, f"SMA ( length={length} ) indicator calculated.")
        # self.data.rolling(window=period).mean()
        # return sma
    
    def exponential_moving_average(self, length=1):
        # EMA = Price(t) * k + EMA(y) * (1 - k)
        ema = ta.ema(self.data[self.check_field], length=length)
        hoc_print(ema, f"EMA ( length={length} ) indicator calculated.")
        # return ema

    def double_exponential_moving_average(self, length=1):
        dema = ta.dema(self.data[self.check_field], length=length)
        hoc_print(dema, f"DEMA ( length={length} ) indicator calculated.")
        # DEMA = 2 * EMA - EMA(EMA)
        # ema = ta.ema(self.data[self.check_field], length=period)
        # # ema = self.data.ewm(span=period, min_periods=period).mean()
        # dema = 2 * ema - ema.ewm(span=period, min_periods=period).mean()

        # return dema

    # @staticmethod

    # @staticmethod
    # def triple_exponential_moving_average(self, period=14):
    #     # TEMA = 3 * EMA - 3 * EMA(EMA) + EMA(EMA(EMA))
    #     ema = self.data.ewm(span=period, min_periods=period).mean()
    #     tema = 3 * ema - 3 * ema.ewm(span=period, min_periods=period).mean() + ema.ewm(span=period, min_periods=period).mean().ewm(span=period, min_periods=period).mean()
    #     return tema

    # @staticmethod

    # @staticmethod
    # def smoothed_moving_average(self, period=14):
    #     # SMMA = (Sum of self.data over period - first price + current price) / period
    #     smma = self.data.ewm(span=period, min_periods=period, adjust=False).mean()
    #     return smma

    # @staticmethod
    # def weighted_moving_average(self, period=14):
    #     # WMA = Sum of (price * weight) / sum of weights
    #     weights = np.arange(1, period + 1)
    #     wma = self.data.rolling(window=period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    #     return wma

    # @staticmethod
    # def hull_moving_average(self, period=14):
    #     # HMA = WMA(2*WMA(n/2) - WMA(n)), sqrt(n)
    #     half_period = int(period / 2)
    #     sqrt_period = int(np.sqrt(period))
    #     wma_half = TrendIndicators.weighted_moving_average(self, period=half_period)
    #     wma_full = TrendIndicators.weighted_moving_average(self, period=period)
    #     hull = TrendIndicators.weighted_moving_average(2 * wma_half - wma_full, period=sqrt_period)
    #     return hull

    # @staticmethod
    # def kaufman_adaptive_moving_average(self, period=10):
    #     # KAMA = Previous KAMA + (ER * SC * (Price - Previous KAMA))
    #     change = abs(self.data - self.data.shift(period))
    #     volatility = abs(self.data.diff()).rolling(window=period).sum()
    #     er = change / volatility
    #     fast_alpha = 2 / (2 + 1)
    #     slow_alpha = 2 / (30 + 1)
    #     sc = (er * (fast_alpha - slow_alpha) + slow_alpha) ** 2
    #     kama = [self.data.iloc[0]]
    #     for i in range(1, len(self.data)):
    #         kama.append(kama[-1] + sc[i] * (self.data[i] - kama[-1]))
    #     return pd.Series(kama, index=self.data.index)

    # @staticmethod
    # def adaptive_moving_average(self, period=10):
    #     # AMA = (Sum of self.data over period - first price + current price) / period
    #     ama = self.data.ewm(span=period, min_periods=period, adjust=False).mean()
    #     return ama

    # @staticmethod
    # def fractal_adaptive_moving_average(self, period=10):
    #     # FRAMA = Price(t) * k + FRAMA(y) * (1 - k)
    #     log_n = np.log(period)
    #     high_max = self.data.rolling(window=period).max()
    #     low_min = self.data.rolling(window=period).min()
    #     n1 = np.log(high_max - low_min) / log_n
    #     frama = self.data.ewm(span=n1, min_periods=n1).mean()
    #     return frama

    # @staticmethod
    # def mcginley_dynamic(self, period=14):
    #     # MD = MD-1 + (Price - MD-1) / (k * (Price / MD-1) ^ 4)
    #     k = 0.6
    #     md = [self.data.iloc[0]]
    #     for i in range(1, len(self.data)):
    #         md.append(md[-1] + (self.data[i] - md[-1]) / (k * (self.data[i] / md[-1]) ** 4))
    #     return pd.Series(md, index=self.data.index)

    # @staticmethod
    # def vidya(self, short_period=9, long_period=30):
    #     # VIDYA = EMA(short_period) / EMA(long_period)
    #     short_ema = self.data.ewm(span=short_period, min_periods=short_period).mean()
    #     long_ema = self.data.ewm(span=long_period, min_periods=long_period).mean()
    #     vidya = short_ema / long_ema
    #     return vidya

    # @staticmethod
    # def linear_regression_line(self, period=14):
    #     # LRL = a + b * x
    #     def linear_regression(series):
    #         x = np.arange(len(series))
    #         slope, intercept = np.polyfit(x, series, 1)
    #         return intercept + slope * x

    #     lrl = self.data.rolling(window=period).apply(linear_regression, raw=False)
    #     return lrl

    # @staticmethod
    # def linear_regression_slope(self, period=14):
    #     # LRS = b (slope of the linear regression line)
    #     def linear_regression_slope(series):
    #         x = np.arange(len(series))
    #         slope, intercept = np.polyfit(x, series, 1)
    #         return slope

    #     lrs = self.data.rolling(window=period).apply(linear_regression_slope, raw=False)
    #     return lrs

    # @staticmethod
    # def linear_regression_r_squared(self, period=14):
    #     # R^2 = 1 - (SS_res / SS_tot)
    #     def r_squared(series):
    #         x = np.arange(len(series))
    #         slope, intercept = np.polyfit(x, series, 1)
    #         y_fit = intercept + slope * x
    #         ss_res = np.sum((series - y_fit) ** 2)
    #         ss_tot = np.sum((series - np.mean(series)) ** 2)
    #         r2 = 1 - (ss_res / ss_tot)
    #         return r2

    #     r_squared = self.data.rolling(window=period).apply(r_squared, raw=False)
    #     return r_squared

    # @staticmethod
    # def polynomial_regression(self, degree=2, period=14):
    #     # Polynomial Regression Line
    #     def poly_regression(series):
    #         x = np.arange(len(series))
    #         coeffs = np.polyfit(x, series, degree)
    #         return np.polyval(coeffs, x)

    #     poly_line = self.data.rolling(window=period).apply(poly_regression, raw=False)
    #     return poly_line

    # @staticmethod
    # def parabolic_regression(self, period=14):
    #     # Parabolic Regression Line
    #     def parabolic_regression(series):
    #         x = np.arange(len(series))
    #         coeffs = np.polyfit(x, series, 2)
    #         return np.polyval(coeffs, x)

    #     parabola = self.data.rolling(window=period).apply(parabolic_regression, raw=False)
    #     return parabola

    # @staticmethod
    # def logarithmic_regression(self, period=14):
    #     # Logarithmic Regression Line
    #     def logarithmic_regression(series):
    #         x = np.arange(1, len(series) + 1)
    #         log_x = np.log(x)
    #         slope, intercept = np.polyfit(log_x, series, 1)
    #         return intercept + slope * log_x

    #     log_line = self.data.rolling(window=period).apply(logarithmic_regression, raw=False)
    #     return log_line

    # @staticmethod
    # def sinusoidal_regression(self, period=14):
    #     # Sinusoidal Regression Line
    #     def sinusoidal_regression(series):
    #         x = np.arange(len(series))
    #         coeffs = np.polyfit(x, np.sin(series), 1)
    #         return np.sin(np.polyval(coeffs, x))

    #     sinusoidal_line = self.data.rolling(window=period).apply(sinusoidal_regression, raw=False)
    #     return sinusoidal_line

    # @staticmethod
    # def inverse_regression(self, period=14):
    #     # Inverse Regression Line
    #     def inverse_regression(series):
    #         x = np.arange(1, len(series) + 1)
    #         inv_x = 1 / x
    #         slope, intercept = np.polyfit(inv_x, series, 1)
    #         return intercept + slope * inv_x

    #     inv_line = self.data.rolling(window=period).apply(inverse_regression, raw=False)
    #     return inv_line

    # @staticmethod
    # def supertrend_indicator(self, period=7, multiplier=3):
    #     # Supertrend = (Upperband / Lowerband)
    #     atr = VolatilityIndicators.average_true_range(self, period=period)
    #     hl2 = (self.data['high'] + self.data['low']) / 2
    #     upper_band = hl2 + (multiplier * atr)
    #     lower_band = hl2 - (multiplier * atr)
    #     supertrend = pd.Series(index=self.data.index)
    #     for i in range(1, len(self.data)):
    #         if self.data['close'][i] > supertrend[i-1]:
    #             supertrend[i] = upper_band[i]
    #         else:
    #             supertrend[i] = lower_band[i]
    #     return supertrend

    # @staticmethod
    # def parabolic_sar(self, af=0.02, max_af=0.2):
    #     # SAR = Prior SAR + AF (Prior EP - Prior SAR)
    #     sar = pd.Series(index=self.data.index)
    #     ep = self.data['high'][0]  # extreme point
    #     trend = 1  # 1 for uptrend, -1 for downtrend
    #     sar[0] = self.data['low'][0] if trend == 1 else self.data['high'][0]
    #     af_value = af
    #     for i in range(1, len(self.data)):
    #         sar[i] = sar[i-1] + af_value * (ep - sar[i-1])
    #         if trend == 1:
    #             if self.data['low'][i] < sar[i]:
    #                 trend = -1
    #                 sar[i] = ep
    #                 ep = self.data['low'][i]
    #                 af_value = af
    #             else:
    #                 if self.data['high'][i] > ep:
    #                     ep = self.data['high'][i]
    #                     af_value = min(af_value + af, max_af)
    #         else:
    #             if self.data['high'][i] > sar[i]:
    #                 trend = 1
    #                 sar[i] = ep
    #                 ep = self.data['high'][i]
    #                 af_value = af
    #             else:
    #                 if self.data['low'][i] < ep:
    #                     ep = self.data['low'][i]
    #                     af_value = min(af_value + af, max_af)
    #     return sar

    # @staticmethod
    # def moving_average_ribbon(self, period_list=[5, 10, 15, 20, 25, 30, 35, 40, 45, 50]):
    #     # MAR = List of moving averages for different periods
    #     ribbon = pd.DataFrame(index=self.data.index)
    #     for period in period_list:
    #         ribbon[f'SMA_{period}'] = TrendIndicators.simple_moving_average(self, period)
    #     return ribbon

    # @staticmethod
    # def zig_zag(self, percentage=5):
    #     # ZigZag = 5% threshold for trend changes
    #     zig_zag = [self.data.iloc[0]]
    #     last_extreme = self.data.iloc[0]
    #     for i in range(1, len(self.data)):
    #         change = (self.data[i] - last_extreme) / last_extreme * 100
    #         if abs(change) >= percentage:
    #             zig_zag.append(self.data[i])
    #             last_extreme = self.data[i]
    #     return pd.Series(zig_zag, index=self.data.index[:len(zig_zag)])

    # @staticmethod
    # def ichimoku_cloud(self):
    #     # Ichimoku Cloud = Conversion Line, Base Line, Leading Span A, Leading Span B, Lagging Span
    #     conversion_line = (self.data['high'].rolling(window=9).max() + self.data['low'].rolling(window=9).min()) / 2
    #     base_line = (self.data['high'].rolling(window=26).max() + self.data['low'].rolling(window=26).min()) / 2
    #     leading_span_a = ((conversion_line + base_line) / 2).shift(26)
    #     leading_span_b = ((self.data['high'].rolling(window=52).max() + self.data['low'].rolling(window=52).min()) / 2).shift(26)
    #     lagging_span = self.data['close'].shift(-26)
    #     return conversion_line, base_line, leading_span_a, leading_span_b, lagging_span


# # Trend Indicators
# class MA(Indicator):
#     # MA = Sum of Closing self.data over n periods / n
#     def calculate(self, period=20):
#         ma = self.data['Close'].rolling(window=period).mean()
#         return ma

# class EMA(Indicator):
#     # EMA = (Closing price - EMA(previous day)) * multiplier + EMA(previous day)
#     def calculate(self, period=20):
#         ema = self.data['Close'].ewm(span=period, adjust=False).mean()
#         return ema

# class DEMA(Indicator):
#     # DEMA = 2 * EMA(n) - EMA(EMA(n))
#     def calculate(self, period=20):
#         ema = self.data['Close'].ewm(span=period, adjust=False).mean()
#         dema = 2 * ema - ema.ewm(span=period, adjust=False).mean()
#         return dema

# class TEMA(Indicator):
#     # TEMA = 3 * EMA(n) - 3 * EMA(EMA(n)) + EMA(EMA(EMA(n)))
#     def calculate(self, period=20):
#         ema = self.data['Close'].ewm(span=period, adjust=False).mean()
#         ema2 = ema.ewm(span=period, adjust=False).mean()
#         ema3 = ema2.ewm(span=period, adjust=False).mean()
#         tema = 3 * ema - 3 * ema2 + ema3
#         return tema

# class SMA(Indicator):
#     # SMA = Sum of Closing self.data over n periods / n
#     def calculate(self, period=20):
#         sma = self.data['Close'].rolling(window=period).mean()
#         return sma

# class SMMA(Indicator):
#     # SMMA = (SUM(n-1) + CLOSE) / n
#     def calculate(self, period=20):
#         smma = self.data['Close'].rolling(window=period, min_periods=1).apply(lambda x: (x[:-1].sum() + x[-1]) / period, raw=False)
#         return smma

# class WMA(Indicator):
#     # WMA = (Price * Weight) / Sum of Weights
#     def calculate(self, period=20):
#         weights = np.arange(1, period + 1)
#         wma = self.data['Close'].rolling(window=period).apply(lambda self.data: np.dot(self, weights) / weights.sum(), raw=True)
#         return wma

# class HMA(Indicator):
#     # HMA = WMA(2 * WMA(n/2) - WMA(n)), sqrt(n))
#     def calculate(self, period=20):
#         half_length = int(period / 2)
#         sqrt_length = int(np.sqrt(period))
#         wma_half = self.data['Close'].rolling(window=half_length).apply(lambda self.data: np.dot(self, np.arange(1, half_length + 1)) / np.arange(1, half_length + 1).sum(), raw=True)
#         wma_full = self.data['Close'].rolling(window=period).apply(lambda self.data: np.dot(self, np.arange(1, period + 1)) / np.arange(1, period + 1).sum(), raw=True)
#         hma = 2 * wma_half - wma_full
#         hma = hma.rolling(window=sqrt_length).apply(lambda self.data: np.dot(self, np.arange(1, sqrt_length + 1)) / np.arange(1, sqrt_length + 1).sum(), raw=True)
#         return hma

# class KAMA(Indicator):
#     # KAMA = Previous KAMA + SC * (Price - Previous KAMA)
#     def calculate(self, period=10, fast=2, slow=30):
#         change = self.data['Close'].diff(period)
#         volatility = self.data['Close'].diff().abs().rolling(window=period).sum()
#         er = change / volatility
#         sc = (er * (2 / (fast + 1) - 2 / (slow + 1)) + 2 / (slow + 1)) ** 2
#         kama = self.data['Close'].copy()
#         for i in range(1, len(kama)):
#             kama.iloc[i] = kama.iloc[i - 1] + sc.iloc[i] * (self.data['Close'].iloc[i] - kama.iloc[i - 1])
#         return kama

# class AMA(Indicator):
#     # AMA = AMA(previous) + Constant * (Close - AMA(previous))
#     def calculate(self, period=10, constant=0.2):
#         ama = self.data['Close'].copy()
#         for i in range(1, len(ama)):
#             ama.iloc[i] = ama.iloc[i - 1] + constant * (self.data['Close'].iloc[i] - ama.iloc[i - 1])
#         return ama

# class FRAMA(Indicator):
#     # FRAMA = Previous FRAMA + d * (Price - Previous FRAMA)
#     def calculate(self, period=16):
#         N = 16  # Sample size for calculating fractal dimension
#         frama = self.data['Close'].copy()
#         for i in range(period, len(frama)):
#             high_max = self.data['High'][i - period + 1:i + 1].max()
#             low_min = self.data['Low'][i - period + 1:i + 1].min()
#             N1 = (high_max - low_min) / period
#             high_max_1 = self.data['High'][i - int(period / 2) + 1:i + 1].max()
#             low_min_1 = self.data['Low'][i - int(period / 2) + 1:i + 1].min()
#             N2 = (high_max_1 - low_min_1) / (period / 2)
#             high_max_2 = self.data['High'][i - period + 1:i - int(period / 2) + 1].max()
#             low_min_2 = self.data['Low'][i - period + 1:i - int(period / 2) + 1].min()
#             N3 = (high_max_2 - low_min_2) / (period / 2)
#             D = np.log((N2 + N3) / N1) / np.log(2)
#             alpha = np.exp(-4.6 * (D - 1))
#             frama.iloc[i] = frama.iloc[i - 1] + alpha * (self.data['Close'].iloc[i] - frama.iloc[i - 1])
#         return frama

# class McGinleyDynamic(Indicator):
#     # MD = MD(previous) + (Close - MD(previous)) / (Constant * (Close / MD(previous)) ^ 4)
#     def calculate(self, period=10, constant=0.6):
#         md = self.data['Close'].copy()
#         for i in range(1, len(md)):
#             md.iloc[i] = md.iloc[i - 1] + (self.data['Close'].iloc[i] - md.iloc[i - 1]) / (constant * (self.data['Close'].iloc[i] / md.iloc[i - 1]) ** 4)
#         return md

# class VIDYA(Indicator):
#     # VIDYA = Previous VIDYA + (Volatility Index) * (Close - Previous VIDYA)
#     def calculate(self, period=14, constant=0.2):
#         std_dev = self.data['Close'].rolling(window=period).std()
#         vidya = self.data['Close'].copy()
#         for i in range(1, len(vidya)):
#             vidya.iloc[i] = vidya.iloc[i - 1] + (constant / std_dev.iloc[i]) * (self.data['Close'].iloc[i] - vidya.iloc[i - 1])
#         return vidya

# class LinearRegressionLine(Indicator):
#     # LRL = a + b * x
#     def calculate(self, period=20):
#         linreg = self.data['Close'].rolling(window=period).apply(lambda x: np.polyfit(range(len(x)), x, 1)[1] + np.polyfit(range(len(x)), x, 1)[0] * (len(x) - 1), raw=False)
#         return linreg

# class LinearRegressionSlope(Indicator):
#     # Slope = b (from y = a + bx)
#     def calculate(self, period=20):
#         slope = self.data['Close'].rolling(window=period).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0], raw=False)
#         return slope

# class LinearRegressionRSquared(Indicator):
#     # R-Squared = 1 - (SSres / SStot)
#     def calculate(self, period=20):
#         def r_squared(x):
#             y = range(len(x))
#             slope, intercept = np.polyfit(y, x, 1)
#             ss_res = np.sum((x - (slope * y + intercept)) ** 2)
#             ss_tot = np.sum((x - np.mean(x)) ** 2)
#             return 1 - (ss_res / ss_tot)
#         r_squared = self.data['Close'].rolling(window=period).apply(r_squared, raw=False)
#         return r_squared

# class PolynomialRegression(Indicator):
#     # Polynomial Regression: y = a0 + a1*x + a2*x^2 + ... + an*x^n
#     def calculate(self, period=20, degree=2):
#         def poly_fit(x):
#             coeffs = np.polyfit(range(len(x)), x, degree)
#             poly = np.poly1d(coeffs)
#             return poly(len(x) - 1)
#         polyreg = self.data['Close'].rolling(window=period).apply(poly_fit, raw=False)
#         return polyreg

# class ParabolicRegression(Indicator):
#     # Parabolic Regression: y = a + bx + cx^2
#     def calculate(self, period=20):
#         def parabolic_fit(x):
#             coeffs = np.polyfit(range(len(x)), x, 2)
#             poly = np.poly1d(coeffs)
#             return poly(len(x) - 1)
#         parabreg = self.data['Close'].rolling(window=period).apply(parabolic_fit, raw=False)
#         return parabreg

# class LogarithmicRegression(Indicator):
#     # Logarithmic Regression: y = a + b * ln(x)
#     def calculate(self, period=20):
#         def log_fit(x):
#             y = np.log(range(1, len(x) + 1))
#             coeffs = np.polyfit(y, x, 1)
#             return coeffs[0] * np.log(len(x)) + coeffs[1]
#         logreg = self.data['Close'].rolling(window=period).apply(log_fit, raw=False)
#         return logreg

# class SinusoidalRegression(Indicator):
#     # Sinusoidal Regression: y = a * sin(bx + c) + d
#     def calculate(self, period=20):
#         def sinusoidal_fit(x):
#             def sin_func(x, a, b, c, d):
#                 return a * np.sin(b * x + c) + d
#             popt, _ = np.curve_fit(sin_func, np.arange(len(x)), x, p0=[np.std(x), 2*np.pi/len(x), 0, np.mean(x)])
#             return sin_func(len(x), *popt)
#         sinusoidalreg = self.data['Close'].rolling(window=period).apply(sinusoidal_fit, raw=False)
#         return sinusoidalreg

# class InverseRegression(Indicator):
#     # Inverse Regression: y = a + b / x
#     def calculate(self, period=20):
#         def inverse_fit(x):
#             y = 1 / np.arange(1, len(x) + 1)
#             coeffs = np.polyfit(y, x, 1)
#             return coeffs[0] / len(x) + coeffs[1]
#         inversereg = self.data['Close'].rolling(window=period).apply(inverse_fit, raw=False)
#         return inversereg

# class SupertrendIndicator(Indicator):
#     # Supertrend = (High + Low) / 2 + Multiplier * ATR
#     def calculate(self, period=10, multiplier=3):
#         atr = self.data['Close'].rolling(window=period).apply(lambda x: max(x.max() - x.min(), abs(x[-1] - x[0]), abs(x[-1] - x.min())), raw=True)
#         hl2 = (self.data['High'] + self.data['Low']) / 2
#         supertrend = hl2 + multiplier * atr
#         return supertrend

# class ParabolicSAR(Indicator):
#     # Parabolic SAR: SARn = SARn-1 + AF * (EP - SARn-1)
#     def calculate(self, af_start=0.02, af_increment=0.02, af_max=0.2):
#         psar = self.data['Close'].copy()
#         ep = self.data['High'][0]
#         af = af_start
#         trend = 1  # 1 for uptrend, -1 for downtrend
#         for i in range(1, len(psar)):
#             psar.iloc[i] = psar.iloc[i - 1] + af * (ep - psar.iloc[i - 1])
#             if trend == 1:
#                 if self.data['Low'].iloc[i] < psar.iloc[i]:
#                     trend = -1
#                     ep = self.data['Low'].iloc[i]
#                     af = af_start
#                     psar.iloc[i] = ep
#                 elif self.data['High'].iloc[i] > ep:
#                     ep = self.data['High'].iloc[i]
#                     af = min(af + af_increment, af_max)
#             elif trend == -1:
#                 if self.data['High'].iloc[i] > psar.iloc[i]:
#                     trend = 1
#                     ep = self.data['High'].iloc[i]
#                     af = af_start
#                     psar.iloc[i] = ep
#                 elif self.data['Low'].iloc[i] < ep:
#                     ep = self.data['Low'].iloc[i]
#                     af = min(af + af_increment, af_max)
#         return psar

# class MovingAverageRibbon(Indicator):
#     # Moving Average Ribbon = Multiple moving averages of different periods plotted together
#     def calculate(self, periods=[5, 10, 20, 50, 100, 200]):
#         ribbon = pd.DataFrame(index=self.data.index)
#         for period in periods:
#             ribbon[f'SMA_{period}'] = self.data['Close'].rolling(window=period).mean()
#         return ribbon

# class ZigZagIndicator(Indicator):
#     # Zig Zag = Minimum price change that must occur before a new line is drawn
#     def calculate(self, change=0.1):
#         zigzag = pd.Series(index=self.data.index, dtype=float)
#         direction = None
#         for i in range(1, len(self.data)):
#             if direction is None:
#                 if self.data['Close'].iloc[i] > self.data['Close'].iloc[i - 1] * (1 + change):
#                     direction = 'up'
#                     zigzag.iloc[i] = self.data['Close'].iloc[i]
#                 elif self.data['Close'].iloc[i] < self.data['Close'].iloc[i - 1] * (1 - change):
#                     direction = 'down'
#                     zigzag.iloc[i] = self.data['Close'].iloc[i]
#             elif direction == 'up':
#                 if self.data['Close'].iloc[i] < self.data['Close'].iloc[i - 1] * (1 - change):
#                     direction = 'down'
#                     zigzag.iloc[i] = self.data['Close'].iloc[i]
#                 else:
#                     zigzag.iloc[i] = zigzag.iloc[i - 1]
#             elif direction == 'down':
#                 if self.data['Close'].iloc[i] > self.data['Close'].iloc[i - 1] * (1 + change):
#                     direction = 'up'
#                     zigzag.iloc[i] = self.data['Close'].iloc[i]
#                 else:
#                     zigzag.iloc[i] = zigzag.iloc[i - 1]
#         return zigzag

# class IchimokuCloud(Indicator):
#     # Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
#     # Kijun-sen (Base Line): (26-period high + 26-period low) / 2
#     # Senkou Span A (Leading Span A): (Conversion Line + Base Line) / 2
#     # Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2
#     # Chikou Span (Lagging Span): Close plotted 26 days in the past
#     def calculate(self):
#         high_9 = self.data['High'].rolling(window=9).max()
#         low_9 = self.data['Low'].rolling(window=9).min()
#         tenkan_sen = (high_9 + low_9) / 2
        
#         high_26 = self.data['High'].rolling(window=26).max()
#         low_26 = self.data['Low'].rolling(window=26).min()
#         kijun_sen = (high_26 + low_26) / 2
        
#         senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        
#         high_52 = self.data['High'].rolling(window=52).max()
#         low_52 = self.data['Low'].rolling(window=52).min()
#         senkou_span_b = ((high_52 + low_52) / 2).shift(26)
        
#         chikou_span = self.data['Close'].shift(-26)
        
#         ichimoku_cloud = pd.DataFrame(index=self.data.index)
#         ichimoku_cloud['Tenkan-sen'] = tenkan_sen
#         ichimoku_cloud['Kijun-sen'] = kijun_sen
#         ichimoku_cloud['Senkou Span A'] = senkou_span_a
#         ichimoku_cloud['Senkou Span B'] = senkou_span_b
#         ichimoku_cloud['Chikou Span'] = chikou_span
        
#         return ichimoku_cloud

# # Example usage:
# # df = pd.read_csv('data.csv')
# # rsi = RSI(df)
# # rsi_values = rsi.calculate()
# # print(rsi_values)
