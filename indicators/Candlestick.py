
import numpy as np
import pandas as pd

# Candlestick and Chart Pattern Indicators
class CandlestickIndicators:
    def __init__(self, data):
        self.data = data
        
    @staticmethod
    def heikin_ashi(self):
        # Heikin-Ashi
        ha_close = (self.data['open'] + self.data['high'] + self.data['low'] + self.data['close']) / 4
        ha_open = [(self.data['open'].iloc[0] + self.data['close'].iloc[0]) / 2]
        for i in range(1, len(self)):
            ha_open.append((ha_open[-1] + ha_close.iloc[i-1]) / 2)
        ha_high = self.data[['high', 'open', 'close']].max(axis=1)
        ha_low = self.data[['low', 'open', 'close']].min(axis=1)
        return pd.DataFrame({'open': ha_open, 'high': ha_high, 'low': ha_low, 'close': ha_close}, index=self.index)

    @staticmethod
    def heikin_ashi_smoothed(self, period=14):
        # Heikin-Ashi Smoothed
        ha = CandlestickIndicators.heikin_ashi(self)
        ha_smoothed = ha.ewm(span=period, adjust=False).mean()
        return ha_smoothed

    @staticmethod
    def equivolume(self):
        # Equivolume
        equivolume = self.data['volume'] * (self.data['high'] - self.data['low'])
        return equivolume

    @staticmethod
    def candle_volume(self):
        # Candle Volume
        candle_volume = self.data['volume'] * (self.data['close'] - self.data['open'])
        return candle_volume

    @staticmethod
    def point_and_figure(self, box_size=1):
        # Point and Figure Chart
        pf = []
        column = 'X'
        for i in range(1, len(self)):
            if column == 'X':
                if self.data['close'].iloc[i] >= self.data['close'].iloc[i-1] + box_size:
                    pf.append((self.index[i], self.data['close'].iloc[i]))
                elif self.data['close'].iloc[i] <= self.data['close'].iloc[i-1] - box_size:
                    column = 'O'
                    pf.append((self.index[i], self.data['close'].iloc[i]))
            else:
                if self.data['close'].iloc[i] <= self.data['close'].iloc[i-1] - box_size:
                    pf.append((self.index[i], self.data['close'].iloc[i]))
                elif self.data['close'].iloc[i] >= self.data['close'].iloc[i-1] + box_size:
                    column = 'X'
                    pf.append((self.index[i], self.data['close'].iloc[i]))
        return pd.DataFrame(pf, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def renko(self, box_size=1):
        # Renko Chart
        renko = []
        brick = self.data['close'].iloc[0]
        for i in range(1, len(self)):
            if self.data['close'].iloc[i] >= brick + box_size:
                renko.append((self.index[i], self.data['close'].iloc[i]))
                brick = self.data['close'].iloc[i]
            elif self.data['close'].iloc[i] <= brick - box_size:
                renko.append((self.index[i], self.data['close'].iloc[i]))
                brick = self.data['close'].iloc[i]
        return pd.DataFrame(renko, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def kagi(self, reversal=3):
        # Kagi Chart
        kagi = []
        column = 'X'
        for i in range(1, len(self)):
            if column == 'X':
                if self.data['close'].iloc[i] >= self.data['close'].iloc[i-1] + reversal:
                    kagi.append((self.index[i], self.data['close'].iloc[i]))
                elif self.data['close'].iloc[i] <= self.data['close'].iloc[i-1] - reversal:
                    column = 'O'
                    kagi.append((self.index[i], self.data['close'].iloc[i]))
            else:
                if self.data['close'].iloc[i] <= self.data['close'].iloc[i-1] - reversal:
                    kagi.append((self.index[i], self.data['close'].iloc[i]))
                elif self.data['close'].iloc[i] >= self.data['close'].iloc[i-1] + reversal:
                    column = 'X'
                    kagi.append((self.index[i], self.data['close'].iloc[i]))
        return pd.DataFrame(kagi, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def line_break(self, line_number=3):
        # Line Break Chart
        line_break = []
        direction = 'up'
        for i in range(1, len(self)):
            if direction == 'up':
                if self.data['close'].iloc[i] >= max(self.data['close'].iloc[i-line_number:i]):
                    line_break.append((self.index[i], self.data['close'].iloc[i]))
                elif self.data['close'].iloc[i] <= min(self.data['close'].iloc[i-line_number:i]):
                    direction = 'down'
                    line_break.append((self.index[i], self.data['close'].iloc[i]))
            else:
                if self.data['close'].iloc[i] <= min(self.data['close'].iloc[i-line_number:i]):
                    line_break.append((self.index[i], self.data['close'].iloc[i]))
                elif self.data['close'].iloc[i] >= max(self.data['close'].iloc[i-line_number:i]):
                    direction = 'up'
                    line_break.append((self.index[i], self.data['close'].iloc[i]))
        return pd.DataFrame(line_break, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def swing(self):
        # Swing Chart
        swing = []
        direction = 'up'
        for i in range(1, len(self)):
            if direction == 'up':
                if self.data['close'].iloc[i] >= self.data['close'].iloc[i-1]:
                    swing.append((self.index[i], self.data['close'].iloc[i]))
                else:
                    direction = 'down'
                    swing.append((self.index[i], self.data['close'].iloc[i]))
            else:
                if self.data['close'].iloc[i] <= self.data['close'].iloc[i-1]:
                    swing.append((self.index[i], self.data['close'].iloc[i]))
                else:
                    direction = 'up'
                    swing.append((self.index[i], self.data['close'].iloc[i]))
        return pd.DataFrame(swing, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def swing_index(self, period=14):
        # Swing Index
        swing_index = []
        for i in range(1, len(self)):
            swing_index.append((self.index[i], self.data['close'].iloc[i] - self.data['close'].iloc[i-1]))
        return pd.DataFrame(swing_index, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def swing_points(self):
        # Swing Points
        swing_points = []
        for i in range(1, len(self)):
            swing_points.append((self.index[i], self.data['close'].iloc[i] - self.data['close'].iloc[i-1]))
        return pd.DataFrame(swing_points, columns=['Date', 'Price']).set_index('Date')

    @staticmethod
    def three_line_break(self, period=14):
        # Three Line Break Chart
        three_line_break = []
        for i in range(1, len(self)):
            three_line_break.append((self.index[i], self.data['close'].iloc[i] - self.data['close'].iloc[i-1]))
        return pd.DataFrame(three_line_break, columns=['Date', 'Price']).set_index('Date')


# import numpy as np
# import pandas as pd
# from indicators.base import Indicator

# class HeikinAshi(Indicator):
#     def calculate(self):
#         """
#         Heikin-Ashi
#         HA_Close = (Open + High + Low + Close) / 4
#         HA_Open = (Previous HA_Open + Previous HA_Close) / 2
#         HA_High = max(High, HA_Open, HA_Close)
#         HA_Low = min(Low, HA_Open, HA_Close)
#         """
#         ha_data = self.data.copy()
#         ha_data['HA_Close'] = (self.data['Open'] + self.data['High'] + self.data['Low'] + self.data['Close']) / 4
#         ha_data['HA_Open'] = (self.data['Open'].shift(1) + self.data['Close'].shift(1)) / 2
#         ha_data['HA_High'] = ha_data[['High', 'HA_Open', 'HA_Close']].max(axis=1)
#         ha_data['HA_Low'] = ha_data[['Low', 'HA_Open', 'HA_Close']].min(axis=1)
#         return ha_data

# class HeikinAshiSmoothed(Indicator):
#     def calculate(self):
#         """
#         Heikin-Ashi Smoothed
#         HA_Close = (Open + High + Low + Close) / 4
#         HA_Open = EMA(HA_Open, period)
#         HA_High = max(High, HA_Open, HA_Close)
#         HA_Low = min(Low, HA_Open, HA_Close)
#         """
#         ha_data = self.data.copy()
#         ha_data['HA_Close'] = (self.data['Open'] + self.data['High'] + self.data['Low'] + self.data['Close']) / 4
#         ha_data['HA_Open'] = ha_data['HA_Close'].ewm(span=10, adjust=False).mean()
#         ha_data['HA_High'] = ha_data[['High', 'HA_Open', 'HA_Close']].max(axis=1)
#         ha_data['HA_Low'] = ha_data[['Low', 'HA_Open', 'HA_Close']].min(axis=1)
#         return ha_data

# class Equivolume(Indicator):
#     def calculate(self):
#         """
#         Equivolume
#         Equivolume uses volume to determine the width of the candlestick.
#         """
#         equivolume_data = self.data.copy()
#         equivolume_data['BoxSize'] = (equivolume_data['High'] - equivolume_data['Low']) * equivolume_data['Volume']
#         return equivolume_data

# class CandleVolume(Indicator):
#     def calculate(self):
#         """
#         Candle Volume
#         Candle Volume combines the volume and price range into a single candlestick.
#         """
#         candle_volume_data = self.data.copy()
#         candle_volume_data['CandleVolume'] = (candle_volume_data['High'] - candle_volume_data['Low']) * candle_volume_data['Volume']
#         return candle_volume_data

# class PointAndFigureCharts(Indicator):
#     def __init__(self, data, box_size=1, reversal_amount=3):
#         super().__init__(data)
#         self.box_size = box_size
#         self.reversal_amount = reversal_amount

#     def calculate(self):
#         """
#         Point and Figure Charts
#         Uses box size and reversal amount to determine the chart.
#         """
#         pf_data = []
#         column = []
#         direction = 1  # 1 for up, -1 for down
#         previous_close = self.data['Close'][0]
#         for close in self.data['Close']:
#             if direction == 1:
#                 if close >= previous_close + self.box_size:
#                     column.append(close)
#                     previous_close = close
#                 elif close <= previous_close - (self.box_size * self.reversal_amount):
#                     pf_data.append(column)
#                     column = [close]
#                     previous_close = close
#                     direction = -1
#             else:
#                 if close <= previous_close - self.box_size:
#                     column.append(close)
#                     previous_close = close
#                 elif close >= previous_close + (self.box_size * self.reversal_amount):
#                     pf_data.append(column)
#                     column = [close]
#                     previous_close = close
#                     direction = 1
#         pf_data.append(column)
#         return pf_data

# class RenkoCharts(Indicator):
#     def __init__(self, data, brick_size=2):
#         super().__init__(data)
#         self.brick_size = brick_size

#     def calculate(self):
#         """
#         Renko Charts
#         Renko charts use fixed brick size to determine the chart.
#         """
#         renko_data = []
#         last_price = self.data['Close'][0]
#         for price in self.data['Close']:
#             while abs(price - last_price) >= self.brick_size:
#                 renko_data.append(last_price + self.brick_size if price > last_price else last_price - self.brick_size)
#                 last_price = renko_data[-1]
#         return renko_data

# class KagiCharts(Indicator):
#     def __init__(self, data, reversal_amount=4):
#         super().__init__(data)
#         self.reversal_amount = reversal_amount

#     def calculate(self):
#         """
#         Kagi Charts
#         Kagi charts use reversal amount to determine the chart.
#         """
#         kagi_data = []
#         direction = None
#         last_price = self.data['Close'][0]
#         for price in self.data['Close']:
#             if direction is None:
#                 direction = 1 if price > last_price else -1
#             if (direction == 1 and price >= last_price + self.reversal_amount) or (direction == -1 and price <= last_price - self.reversal_amount):
#                 kagi_data.append(price)
#                 last_price = price
#                 direction = -direction
#         return kagi_data

# class LineBreakCharts(Indicator):
#     def __init__(self, data, line_count=3):
#         super().__init__(data)
#         self.line_count = line_count

#     def calculate(self):
#         """
#         Line Break Charts
#         Line Break charts use line count to determine the chart.
#         """
#         lb_data = []
#         for close in self.data['Close']:
#             if len(lb_data) < self.line_count or close > max(lb_data[-self.line_count:]) or close < min(lb_data[-self.line_count:]):
#                 lb_data.append(close)
#         return lb_data

# class SwingCharts(Indicator):
#     def calculate(self):
#         """
#         Swing Charts
#         Identifies the swings (highs and lows) in the data.
#         """
#         swing_data = []
#         last_swing = self.data['Close'][0]
#         for price in self.data['Close']:
#             if (price > last_swing and price > max(self.data['Close'][:self.data['Close'].index(price)])) or \
#                (price < last_swing and price < min(self.data['Close'][:self.data['Close'].index(price)])):
#                 swing_data.append(price)
#                 last_swing = price
#         return swing_data

# class SwingIndex(Indicator):
#     def calculate(self):
#         """
#         Swing Index
#         Calculates the swing index for the data.
#         """
#         swing_index = pd.Series(index=self.data.index)
#         for i in range(1, len(self.data)):
#             R = max(self.data['High'][i] - self.data['Low'][i], abs(self.data['High'][i] - self.data['Close'][i-1]), abs(self.data['Low'][i] - self.data['Close'][i-1]))
#             swing_index[i] = (self.data['Close'][i] - self.data['Close'][i-1]) + 0.5 * (self.data['Close'][i] - self.data['Open'][i]) + 0.25 * (self.data['Close'][i-1] - self.data['Open'][i-1]) / R
#         return swing_index

# class SwingPoints(Indicator):
#     def calculate(self):
#         """
#         Swing Points
#         Identifies the swing points in the data.
#         """
#         swing_points = {'highs': [], 'lows': []}
#         for i in range(1, len(self.data)-1):
#             if self.data['High'][i] > self.data['High'][i-1] and self.data['High'][i] > self.data['High'][i+1]:
#                 swing_points['highs'].append(self.data['High'][i])
#             if self.data['Low'][i] < self.data['Low'][i-1] and self.data['Low'][i] < self.data['Low'][i+1]:
#                 swing_points['lows'].append(self.data['Low'][i])
#         return swing_points

# class ThreeLineBreak(Indicator):
#     def __init__(self, data, line_count=3):
#         super().__init__(data)
#         self.line_count = line_count

#     def calculate(self):
#         """
#         Three Line Break
#         Uses line count to determine the chart.
#         """
#         tlb_data = []
#         direction = None
#         for close in self.data['Close']:
#             if direction is None:
#                 direction = 1 if close > self.data['Close'][0] else -1
#             if len(tlb_data) < self.line_count or (direction == 1 and close > max(tlb_data[-self.line_count:])) or (direction == -1 and close < min(tlb_data[-self.line_count:])):
#                 tlb_data.append(close)
#                 direction = -direction
#         return tlb_data

# # Example Usage
# if __name__ == "__main__":
#     # Sample data
#     dates = pd.date_range(start='2020-01-01', periods=100)
#     data = pd.DataFrame(index=dates)
#     data['Open'] = np.random.randn(100).cumsum() + 100
#     data['High'] = data['Open'] + (np.random.rand(100) * 10)
#     data['Low'] = data['Open'] - (np.random.rand(100) * 10)
#     data['Close'] = data[['Open', 'High', 'Low']].mean(axis=1) + (np.random.rand(100) * 5 - 2.5)
#     data['Volume'] = np.random.randint(1, 1000, size=100)

#     # Instantiate and calculate each indicator
#     indicators = [
#         HeikinAshi(data),
#         HeikinAshiSmoothed(data),
#         Equivolume(data),
#         CandleVolume(data),
#         PointAndFigureCharts(data),
#         RenkoCharts(data),
#         KagiCharts(data),
#         LineBreakCharts(data),
#         SwingCharts(data),
#         SwingIndex(data),
#         SwingPoints(data),
#         ThreeLineBreak(data)
#     ]

#     for indicator in indicators:
#         print(f"{indicator.__class__.__name__}:")
#         print(indicator.calculate())
#         print("\n")
