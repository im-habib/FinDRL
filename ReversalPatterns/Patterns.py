import pandas as pd
from abc import ABC, abstractmethod

class ChartPatternDetector(ABC):
    DATE_COLUMNS = ['date', 'datetime', 'timestamp']
    REQUIRED_COLUMNS = ['open', 'high', 'low', 'close', 'volume']

    def __init__(self, data: pd.DataFrame):
        # Normalize all column names to lowercase
        data.columns = [col.lower() for col in data.columns]

        # Check for OHLCV columns
        for col in self.REQUIRED_COLUMNS:
            if col not in data.columns:
                raise ValueError(f"Missing required column: '{col}'")

        # Check and set datetime index
        date_col = next((col for col in self.DATE_COLUMNS if col in data.columns), None)
        if date_col is None:
            raise ValueError("Data must include one of the following time columns: 'date', 'datetime', or 'timestamp'")

        # Convert to datetime and set as index
        data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
        data = data.set_index(date_col).sort_index()

        # Drop rows with invalid datetime
        data = data[~data.index.isna()]

        self.data = data

    def _find_troughs(self, series: pd.Series, window: int = 5):
        return [
            i for i in range(window, len(series) - window)
            if series.iloc[i] == min(series.iloc[i - window:i + window + 1])
        ]

    def _find_peaks(self, series: pd.Series, window: int = 5):
        return [
            i for i in range(window, len(series) - window)
            if series.iloc[i] == max(series.iloc[i - window:i + window + 1])
        ]

    @abstractmethod
    def detect(self):
        pass

# All of the Stock Bullish Reversal Patterns

class DoubleBottomDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        lows = self.data['low']
        closes = self.data['close']
        dates = self.data.index

        trough_indices = self._find_troughs(lows, window=5)
        tolerance = 0.02
        min_gap = 3
        max_gap = 10

        for i in range(len(trough_indices) - 1):
            i1, i2 = trough_indices[i], trough_indices[i + 1]
            if not (min_gap <= i2 - i1 <= max_gap):
                continue

            l1, l2 = lows.iloc[i1], lows.iloc[i2]
            avg_low = (l1 + l2) / 2

            if abs(l1 - l2) / avg_low <= tolerance:
                # Check for breakout after second bottom
                post_close = closes.iloc[i2 + 1:i2 + 5]
                if post_close.empty or post_close.max() < max(closes.iloc[[i1, i2]]):
                    continue

                detected.append({
                    'first': dates[i1],
                    'second': dates[i2],
                    'confirm_close': post_close.idxmax()
                })

        return detected

class TripleBottomDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        lows = self.data['low']
        closes = self.data['close']
        dates = self.data.index

        trough_indices = self._find_troughs(lows, window=5)
        tolerance = 0.02
        min_gap = 3
        max_gap = 10

        for i in range(len(trough_indices) - 2):
            i1, i2, i3 = trough_indices[i], trough_indices[i + 1], trough_indices[i + 2]
            if not (min_gap <= i2 - i1 <= max_gap and min_gap <= i3 - i2 <= max_gap):
                continue

            l1, l2, l3 = lows.iloc[i1], lows.iloc[i2], lows.iloc[i3]
            avg_low = (l1 + l2 + l3) / 3

            if all(abs(low - avg_low) / avg_low <= tolerance for low in (l1, l2, l3)):
                post_closes = closes.iloc[i3 + 1:i3 + 5]
                if post_closes.empty or post_closes.max() < max(closes.iloc[[i1, i2, i3]]):
                    continue

                detected.append({
                    'first': dates[i1],
                    'second': dates[i2],
                    'third': dates[i3],
                    'confirm_close': post_closes.idxmax()
                })

        return detected

class InverseHeadAndShouldersDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        lows = self.data['low']
        highs = self.data['high']
        closes = self.data['close']
        dates = self.data.index

        troughs = self._find_troughs(lows, window=5)
        tolerance = 0.03  # 3% price tolerance
        min_gap = 3
        max_gap = 15

        for i in range(len(troughs) - 2):
            ls_i, h_i, rs_i = troughs[i], troughs[i + 1], troughs[i + 2]
            if not (min_gap <= h_i - ls_i <= max_gap and min_gap <= rs_i - h_i <= max_gap):
                continue

            ls = lows.iloc[ls_i]
            head = lows.iloc[h_i]
            rs = lows.iloc[rs_i]

            # Check head is lower than both shoulders
            if not (head < ls and head < rs):
                continue

            # Check shoulders are within tolerance
            avg_shoulder = (ls + rs) / 2
            if abs(ls - rs) / avg_shoulder > tolerance:
                continue

            # Neckline is max high between LS–Head and Head–RS
            neckline_left = highs.iloc[ls_i:h_i].max()
            neckline_right = highs.iloc[h_i:rs_i].max()
            neckline = min(neckline_left, neckline_right)  # conservative

            # Confirmation: breakout above neckline
            confirm_range = closes.iloc[rs_i + 1:rs_i + 6]
            if confirm_range.empty or confirm_range.max() < neckline:
                continue

            detected.append({
                'left_shoulder': dates[ls_i],
                'head': dates[h_i],
                'right_shoulder': dates[rs_i],
                'neckline': neckline,
                'confirm_close': confirm_range.idxmax()
            })

        return detected

class FallingWedgeDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        highs = self.data['high']
        lows = self.data['low']
        closes = self.data['close']
        dates = self.data.index

        peaks = self._find_peaks(highs, window=3)
        troughs = self._find_troughs(lows, window=3)

        min_wedge_len = 5
        max_wedge_len = 20

        for i in range(len(peaks) - min_wedge_len):
            for j in range(i + min_wedge_len, min(i + max_wedge_len, len(peaks))):
                high_slice = [highs.iloc[k] for k in peaks[i:j]]
                low_slice = [lows.iloc[k] for k in troughs if peaks[i] <= k <= peaks[j - 1]]

                if len(low_slice) < 2:
                    continue

                # Check trend: lower highs and lower lows
                if high_slice[0] > high_slice[-1] and low_slice[0] > low_slice[-1]:
                    # Optional: confirm converging
                    if abs(high_slice[0] - low_slice[0]) > abs(high_slice[-1] - low_slice[-1]):
                        # Confirm breakout (next few closes > last peak)
                        breakout_range = closes.iloc[peaks[j - 1] + 1:peaks[j - 1] + 5]
                        if not breakout_range.empty and breakout_range.max() > high_slice[-1]:
                            detected.append({
                                'start': dates[peaks[i]],
                                'end': dates[peaks[j - 1]],
                                'confirm_close': breakout_range.idxmax()
                            })
        return detected

class BullishEngulfingDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        data = self.data

        for i in range(1, len(data)):
            prev = data.iloc[i - 1]
            curr = data.iloc[i]

            # Check if previous candle is bearish
            if prev['close'] >= prev['open']:
                continue

            # Check if current candle is bullish
            if curr['close'] <= curr['open']:
                continue

            # Check if current candle body engulfs previous candle body
            prev_body_low = min(prev['open'], prev['close'])
            prev_body_high = max(prev['open'], prev['close'])

            curr_body_low = min(curr['open'], curr['close'])
            curr_body_high = max(curr['open'], curr['close'])

            if curr_body_low <= prev_body_low and curr_body_high >= prev_body_high:
                detected.append(self.data.index[i])

        return detected

class MorningStarDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        data = self.data

        for i in range(2, len(data)):
            c1, c2, c3 = data.iloc[i-2], data.iloc[i-1], data.iloc[i]

            # 1st candle: long bearish
            c1_body = abs(c1['close'] - c1['open'])
            c1_bear = c1['close'] < c1['open']
            if not c1_bear or c1_body < (c1['high'] - c1['low']) * 0.6:
                continue

            # 2nd candle: small body, gap down
            c2_body = abs(c2['close'] - c2['open'])
            gap_down = c2['high'] < c1['low']
            if c2_body > c1_body * 0.5 or not gap_down:
                continue

            # 3rd candle: long bullish closing into 1st candle body
            c3_bull = c3['close'] > c3['open']
            c3_body = abs(c3['close'] - c3['open'])
            if not c3_bull or c3_body < c1_body * 0.6:
                continue

            if c3['close'] > c1['open']:
                detected.append(self.data.index[i])

        return detected

class HammerDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        data = self.data

        for i in range(1, len(data)):
            c = data.iloc[i]
            body = abs(c['close'] - c['open'])
            lower_shadow = min(c['open'], c['close']) - c['low']
            upper_shadow = c['high'] - max(c['open'], c['close'])

            if body == 0:  # avoid division by zero
                continue

            if lower_shadow >= 2 * body and upper_shadow <= 0.25 * body:
                # Optional: check prior trend down
                detected.append(self.data.index[i])

        return detected

class PiercingLineDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        data = self.data

        for i in range(1, len(data)):
            c1, c2 = data.iloc[i - 1], data.iloc[i]

            c1_bear = c1['close'] < c1['open']
            c2_bull = c2['close'] > c2['open']

            if not (c1_bear and c2_bull):
                continue

            if c2['open'] < c1['close'] and c2['close'] > (c1['open'] + c1['close']) / 2:
                detected.append(self.data.index[i])

        return detected

class RoundedBottomDetector(ChartPatternDetector):
    def detect(self, window=20):
        detected = []
        lows = self.data['low'].values
        dates = self.data.index

        for i in range(window, len(lows) - window):
            center = lows[i]
            left = lows[i - window:i]
            right = lows[i + 1:i + window + 1]

            # Center is minimum in the window
            if center == min(lows[i - window:i + window + 1]):
                # Confirm downtrend before and uptrend after
                if all(x > center for x in left) and all(x > center for x in right):
                    detected.append(dates[i])

        return detected


# All of the Stock Bearish Reversal Patterns

class DoubleTopDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        highs = self.data['high']
        dates = self.data.index

        peaks = self._find_peaks(highs, window=5)
        tolerance = 0.02
        min_gap = 3
        max_gap = 10

        for i in range(len(peaks) - 1):
            i1, i2 = peaks[i], peaks[i + 1]
            if not (min_gap <= i2 - i1 <= max_gap):
                continue

            h1, h2 = highs.iloc[i1], highs.iloc[i2]
            avg_high = (h1 + h2) / 2

            if abs(h1 - h2) / avg_high <= tolerance:
                detected.append({'first': dates[i1], 'second': dates[i2]})

        return detected

class TripleTopDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        highs = self.data['high']
        dates = self.data.index

        peaks = self._find_peaks(highs, window=5)
        tolerance = 0.02
        min_gap = 3
        max_gap = 10

        for i in range(len(peaks) - 2):
            i1, i2, i3 = peaks[i], peaks[i + 1], peaks[i + 2]
            if not (min_gap <= i2 - i1 <= max_gap and min_gap <= i3 - i2 <= max_gap):
                continue

            h1, h2, h3 = highs.iloc[i1], highs.iloc[i2], highs.iloc[i3]
            avg_high = (h1 + h2 + h3) / 3

            if all(abs(h - avg_high) / avg_high <= tolerance for h in (h1, h2, h3)):
                detected.append({'first': dates[i1], 'second': dates[i2], 'third': dates[i3]})

        return detected

class HeadAndShouldersDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        highs = self.data['high']
        dates = self.data.index

        peaks = self._find_peaks(highs, window=5)
        tolerance = 0.03
        min_gap = 3
        max_gap = 15

        for i in range(len(peaks) - 2):
            ls_i, h_i, rs_i = peaks[i], peaks[i + 1], peaks[i + 2]
            if not (min_gap <= h_i - ls_i <= max_gap and min_gap <= rs_i - h_i <= max_gap):
                continue

            ls, head, rs = highs.iloc[ls_i], highs.iloc[h_i], highs.iloc[rs_i]

            # Head must be higher than shoulders
            if not (head > ls and head > rs):
                continue

            # Shoulders approx equal
            avg_shoulder = (ls + rs) / 2
            if abs(ls - rs) / avg_shoulder > tolerance:
                continue

            # Neckline resistance
            neckline_left = self.data['low'].iloc[ls_i:h_i].min()
            neckline_right = self.data['low'].iloc[h_i:rs_i].min()
            neckline = max(neckline_left, neckline_right)

            # Confirmation: close below neckline after right shoulder
            confirm_range = self.data['close'].iloc[rs_i + 1:rs_i + 6]
            if confirm_range.empty or confirm_range.min() > neckline:
                continue

            detected.append({
                'left_shoulder': dates[ls_i],
                'head': dates[h_i],
                'right_shoulder': dates[rs_i],
                'neckline': neckline,
                'confirm_close': confirm_range.idxmin()
            })

        return detected

class RisingWedgeDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        highs = self.data['high']
        lows = self.data['low']
        closes = self.data['close']
        dates = self.data.index

        peaks = self._find_peaks(highs, window=3)
        troughs = self._find_troughs(lows, window=3)

        min_len = 5
        max_len = 20

        for i in range(len(peaks) - min_len):
            for j in range(i + min_len, min(i + max_len, len(peaks))):
                high_slice = [highs.iloc[k] for k in peaks[i:j]]
                low_slice = [lows.iloc[k] for k in troughs if peaks[i] <= k <= peaks[j - 1]]

                if len(low_slice) < 2:
                    continue

                # Check trend: higher highs and higher lows
                if high_slice[0] < high_slice[-1] and low_slice[0] < low_slice[-1]:
                    # Check converging wedge (range narrowing)
                    if abs(high_slice[0] - low_slice[0]) > abs(high_slice[-1] - low_slice[-1]):
                        # Confirm breakout down (close below last low)
                        breakout_range = closes.iloc[peaks[j - 1] + 1:peaks[j - 1] + 5]
                        if not breakout_range.empty and breakout_range.min() < low_slice[-1]:
                            detected.append({
                                'start': dates[peaks[i]],
                                'end': dates[peaks[j - 1]],
                                'confirm_close': breakout_range.idxmin()
                            })
        return detected

class BearishEngulfingDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        data = self.data

        for i in range(1, len(data)):
            prev = data.iloc[i - 1]
            curr = data.iloc[i]

            # Previous candle bullish
            if prev['close'] <= prev['open']:
                continue

            # Current candle bearish
            if curr['close'] >= curr['open']:
                continue

            prev_body_low = min(prev['open'], prev['close'])
            prev_body_high = max(prev['open'], prev['close'])

            curr_body_low = min(curr['open'], curr['close'])
            curr_body_high = max(curr['open'], curr['close'])

            if curr_body_low <= prev_body_low and curr_body_high >= prev_body_high:
                detected.append(self.data.index[i])

        return detected

class EveningStarDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        data = self.data

        for i in range(2, len(data)):
            c1, c2, c3 = data.iloc[i - 2], data.iloc[i - 1], data.iloc[i]

            c1_bull = c1['close'] > c1['open']
            c1_body = abs(c1['close'] - c1['open'])
            if not c1_bull or c1_body < (c1['high'] - c1['low']) * 0.6:
                continue

            c2_body = abs(c2['close'] - c2['open'])
            gap_up = c2['low'] > c1['high']
            if c2_body > c1_body * 0.5 or not gap_up:
                continue

            c3_bear = c3['close'] < c3['open']
            c3_body = abs(c3['close'] - c3['open'])
            if not c3_bear or c3_body < c1_body * 0.6:
                continue

            if c3['close'] < c1['open']:
                detected.append(self.data.index[i])

        return detected

class ShootingStarDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        data = self.data

        for i in range(1, len(data)):
            c = data.iloc[i]
            body = abs(c['close'] - c['open'])
            upper_shadow = c['high'] - max(c['close'], c['open'])
            lower_shadow = min(c['close'], c['open']) - c['low']

            if body == 0:
                continue

            if upper_shadow >= 2 * body and lower_shadow <= 0.25 * body:
                # Optional: check prior trend up
                detected.append(self.data.index[i])

        return detected

class DarkCloudCoverDetector(ChartPatternDetector):
    def detect(self):
        detected = []
        data = self.data

        for i in range(1, len(data)):
            c1, c2 = data.iloc[i - 1], data.iloc[i]

            c1_bull = c1['close'] > c1['open']
            c2_bear = c2['close'] < c2['open']

            if not (c1_bull and c2_bear):
                continue

            midpoint = (c1['open'] + c1['close']) / 2

            if c2['open'] > c1['high'] and c2['close'] < midpoint:
                detected.append(self.data.index[i])

        return detected

class RoundedTopDetector(ChartPatternDetector):
    def detect(self, window=20):
        detected = []
        highs = self.data['high'].values
        dates = self.data.index

        for i in range(window, len(highs) - window):
            center = highs[i]
            left = highs[i - window:i]
            right = highs[i + 1:i + window + 1]

            if center == max(highs[i - window:i + window + 1]):
                if all(x < center for x in left) and all(x < center for x in right):
                    detected.append(dates[i])

        return detected
