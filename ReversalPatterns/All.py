import torch
import numpy as np
import pandas as pd
import torch.nn as nn
from gym import Env, spaces
from yfinance import download
from stable_baselines3 import PPO, DQN
from torch.utils.data import DataLoader, TensorDataset
from stable_baselines3.common.vec_env import DummyVecEnv


# ===========================================
# ChartPatternDetector and All Pattern Detectors
# ===========================================
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


# ===========================================
# Pattern Feature Extractor
# ===========================================
class PatternFeatureExtractor:
    def __init__(self, detectors: list):
        self.detectors = detectors

    def extract(self, data: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame(index=data.index)
        for detector_cls in self.detectors:
            detector = detector_cls(data)
            detections = detector.detect()
            feature_name = detector_cls.__name__
            features[feature_name] = 0
            for result in detections:
                ts = result.get('confirm_close', None) if isinstance(result, dict) else result
                if ts in features.index:
                    features.at[ts, feature_name] = 1
        return features.fillna(0)




import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from gym import Env, spaces
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.vec_env import DummyVecEnv
import mplfinance as mpf
from yfinance import download

# =============================================
# MultiAssetTimeframeDataset
# =============================================
class MultiAssetTimeframeDataset:
    def __init__(self, multi_asset_data: dict, extractor):
        self.multi_asset_data = multi_asset_data
        self.extractor = extractor

    def build(self) -> torch.Tensor:
        asset_tensors = []
        for asset, tf_data in self.multi_asset_data.items():
            print(f"🔄 Processing {asset}...")
            combined_df = self._build_asset_df(tf_data)
            tensor = torch.tensor(combined_df.values, dtype=torch.float32)
            asset_tensors.append(tensor.unsqueeze(-1))  # [seq, feat, 1]
        combined_tensor = torch.cat(asset_tensors, dim=-1)  # [seq, feat, assets]
        return combined_tensor

    def _build_asset_df(self, tf_data):
        feature_dfs = []
        for tf, df in tf_data.items():
            pattern_features = self.extractor.extract(df)
            ohlcv = df[['open', 'high', 'low', 'close', 'volume']]
            combined = pd.concat([ohlcv, pattern_features], axis=1)
            combined.columns = [f"{tf}_{col}" for col in combined.columns]
            feature_dfs.append(combined)
        merged = pd.concat(feature_dfs, axis=1).dropna()
        return merged

# =============================================
# Transformer for Multi-Asset
# =============================================
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * -(torch.log(torch.tensor(10000.0)) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)

class MultiAssetTransformer(nn.Module):
    def __init__(self, num_features, num_assets, d_model=128, nhead=8, num_layers=3, num_classes=3, dropout=0.1):
        super(MultiAssetTransformer, self).__init__()
        self.embedding = nn.Linear(num_features * num_assets, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=512, dropout=dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        self.classifier = nn.Sequential(
            nn.Linear(d_model, 64), nn.ReLU(), nn.Dropout(dropout), nn.Linear(64, num_classes * num_assets)
        )

    def forward(self, x):
        batch_size, seq_len, feat, assets = x.shape
        x_flat = x.view(batch_size, seq_len, feat * assets)
        x_emb = self.embedding(x_flat)
        x_emb = self.pos_encoder(x_emb)
        encoded = self.transformer_encoder(x_emb)
        out = self.classifier(torch.mean(encoded, dim=1))
        return out.view(batch_size, assets, -1)  # [batch, assets, num_classes]

# =============================================
# TradingEnvironment for Multi-Asset
# =============================================
class MultiAssetTradingEnv(Env):
    def __init__(self, data_tensor, initial_balance=100000):
        super(MultiAssetTradingEnv, self).__init__()
        self.data = data_tensor.numpy()
        self.n_steps, self.n_features, self.n_assets = self.data.shape
        self.initial_balance = initial_balance
        self.action_space = spaces.MultiDiscrete([3] * self.n_assets)  # [Hold, Buy, Sell] per asset
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.n_features, self.n_assets), dtype=np.float32)
        self.reset()

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.positions = np.zeros(self.n_assets)
        self.entry_prices = np.zeros(self.n_assets)
        self.total_reward = 0
        return self.data[self.current_step]

    def step(self, actions):
        rewards = 0
        prices = self.data[self.current_step, 3, :]  # Assuming close price at index 3
        for i, action in enumerate(actions):
            if action == 1 and self.positions[i] == 0:  # Buy
                self.positions[i] = 1
                self.entry_prices[i] = prices[i]
            elif action == 2 and self.positions[i] == 0:  # Short
                self.positions[i] = -1
                self.entry_prices[i] = prices[i]
            elif action == 1 and self.positions[i] == -1:  # Cover short
                reward = self.entry_prices[i] - prices[i]
                rewards += reward
                self.balance += reward
                self.positions[i] = 0
            elif action == 2 and self.positions[i] == 1:  # Sell long
                reward = prices[i] - self.entry_prices[i]
                rewards += reward
                self.balance += reward
                self.positions[i] = 0
        self.total_reward += rewards
        self.current_step += 1
        done = self.current_step >= self.n_steps - 1
        return self.data[self.current_step], rewards, done, {}

# =============================================
# RL Agent for Multi-Asset
# =============================================
class MultiAssetRLAgent:
    def __init__(self, env, algorithm="PPO"):
        self.env = DummyVecEnv([lambda: env])
        self.model = PPO("MlpPolicy", self.env, verbose=1) if algorithm == "PPO" else DQN("MlpPolicy", self.env, verbose=1)

    def train(self, timesteps=200_000):
        self.model.learn(total_timesteps=timesteps)

    def predict(self, state):
        actions, _ = self.model.predict(state, deterministic=True)
        return actions

    def save(self, path="multi_asset_rl_agent.zip"):
        self.model.save(path)

    def load(self, path="multi_asset_rl_agent.zip"):
        self.model = PPO.load(path, env=self.env)

# =============================================
# Trainer for Multi-Asset
# =============================================
class MultiAssetTrainer:
    def __init__(self, transformer, rl_agent, dataloader, env, lr=1e-4):
        self.transformer, self.rl_agent, self.dataloader, self.env = transformer, rl_agent, dataloader, env
        self.optimizer = torch.optim.Adam(transformer.parameters(), lr=lr)
        self.criterion = nn.CrossEntropyLoss()

    def pretrain_transformer(self, epochs=5):
        print("🚀 Pretraining Transformer...")
        for epoch in range(epochs):
            total_loss = 0
            for X_batch, y_batch in self.dataloader:
                self.optimizer.zero_grad()
                outputs = self.transformer(X_batch)
                loss = self.criterion(outputs.view(-1, outputs.size(-1)), y_batch.view(-1))
                loss.backward(); self.optimizer.step()
                total_loss += loss.item()
            print(f"Epoch {epoch+1}: Loss={total_loss:.4f}")
        print("✅ Transformer pretraining complete.")

    def train_rl_agent(self, timesteps=200_000):
        print("🚀 Training RL agent...")
        self.rl_agent.train(timesteps)
        print("✅ RL agent training complete.")

    def save_models(self):
        torch.save(self.transformer.state_dict(), "multi_asset_transformer.pth")
        self.rl_agent.save("multi_asset_rl_agent.zip")
        print("💾 Models saved.")

# =============================================
# Example Usage: Load Data & Train
# =============================================
assets = ["AAPL", "TSLA", "BTC-USD"]
timeframes = ["1m", "5m", "1h"]
multi_asset_data = {}
for asset in assets:
    multi_asset_data[asset] = {}
    for tf in timeframes:
        df = download(asset, period="3mo", interval=tf).reset_index()
        multi_asset_data[asset][tf] = df

# Setup pattern detectors and extractor
detectors = [
    DoubleBottomDetector, HeadAndShouldersDetector, BullishEngulfingDetector,
    MorningStarDetector, HammerDetector, PiercingLineDetector, RoundedBottomDetector, FallingWedgeDetector, InverseHeadAndShouldersDetector, TripleBottomDetector,
    DoubleTopDetector, ShootingStarDetector, BearishEngulfingDetector, TripleTopDetector, RisingWedgeDetector, EveningStarDetector, DarkCloudCoverDetector, RoundedTopDetector,
]
extractor = PatternFeatureExtractor(detectors)

# Build dataset
dataset_builder = MultiAssetTimeframeDataset(multi_asset_data, extractor)
data_tensor = dataset_builder.build().unsqueeze(0)  # Add batch dim

# Create model & environment
num_features, num_assets = data_tensor.size(2), data_tensor.size(3)
transformer = MultiAssetTransformer(num_features, num_assets)
env = MultiAssetTradingEnv(data_tensor)
rl_agent = MultiAssetRLAgent(env)

# Prepare dataloader
dummy_labels = torch.randint(0, 3, (1, data_tensor.size(1), num_assets))
dataloader = DataLoader(TensorDataset(data_tensor, dummy_labels), batch_size=1)

# Train
trainer = MultiAssetTrainer(transformer, rl_agent, dataloader, env)
trainer.pretrain_transformer()
trainer.train_rl_agent()
trainer.save_models()




import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from gym import Env, spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import mplfinance as mpf
from yfinance import download

# =============================================
# Evaluator for Multi-Asset
# =============================================
class MultiAssetEvaluator:
    def __init__(self):
        self.logs = []

    def log_step(self, step, prices, actions, rewards):
        for i, (price, action, reward) in enumerate(zip(prices, actions, rewards)):
            self.logs.append({
                'step': step,
                'asset': i,
                'price': price,
                'action': action,
                'reward': reward
            })

    def get_df(self):
        return pd.DataFrame(self.logs)

    def summary(self):
        df = self.get_df()
        if df.empty:
            print("No data to evaluate.")
            return
        print("\n📊 Multi-Asset Performance Summary")
        for asset in df['asset'].unique():
            asset_df = df[df['asset'] == asset]
            pnl = asset_df['reward'].sum()
            returns = asset_df['reward']
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
            cum_rewards = returns.cumsum()
            drawdown = cum_rewards.cummax() - cum_rewards
            max_dd = drawdown.max()
            print(f"Asset {asset}: PNL=${pnl:.2f}, Sharpe={sharpe:.2f}, Max Drawdown=${max_dd:.2f}")
        total_pnl = df['reward'].sum()
        print(f"Total Portfolio PNL: ${total_pnl:.2f}")

# =============================================
# Plotter for Multi-Asset
# =============================================
class MultiAssetPlotter:
    def __init__(self, price_data):
        self.price_data = price_data

    def plot_signals(self, df, asset_idx):
        df_asset = df[df['asset'] == asset_idx]
        dates = self.price_data.index[:len(df_asset)]
        price_series = self.price_data.iloc[:len(df_asset), asset_idx]
        signals = df_asset['action'].values
        colors = ['gray' if a == 0 else 'green' if a == 1 else 'red' for a in signals]
        mpf.plot(pd.DataFrame({'Close': price_series}, index=dates),
                 type='candle', style='yahoo',
                 title=f"Asset {asset_idx} Signals",
                 alines=[[(dates[i], price_series.iloc[i]) for i in range(len(dates)) if signals[i] != 0]],
                 alines_colors=colors)

# =============================================
# Trader for Multi-Asset
# =============================================
class MultiAssetTrader:
    def __init__(self, transformer, rl_agent, evaluator):
        self.transformer = transformer
        self.rl_agent = rl_agent
        self.evaluator = evaluator

    def load_models(self):
        self.transformer.load_state_dict(torch.load("multi_asset_transformer.pth"))
        self.rl_agent.load("multi_asset_rl_agent.zip")
        print("✅ Models loaded for live trading.")

    def trade(self, live_tensor):
        self.transformer.eval()
        with torch.no_grad():
            signals = self.transformer(live_tensor.unsqueeze(0))
            actions = torch.argmax(signals, dim=2).squeeze(0).tolist()
        prices = live_tensor[-1, 3, :].numpy()  # Assuming close prices
        rewards = np.random.uniform(-1, 1, len(actions))  # Dummy rewards for now
        self.evaluator.log_step(len(self.evaluator.logs), prices, actions, rewards)
        print(f"📢 Actions: {actions}")

# =============================================
# System Integration (Trainer + Evaluator + Trader)
# =============================================
# Assume multi_asset_data and PatternFeatureExtractor defined earlier

# Data Preparation
data_tensor = torch.rand((1000, 10, len(["AAPL", "TSLA", "BTC-USD"])))  # Dummy tensor

# Models
transformer = MultiAssetTransformer(num_features=10, num_assets=3)
env = MultiAssetTradingEnv(data_tensor)
rl_agent = MultiAssetRLAgent(env)

# Trainer
trainer = MultiAssetTrainer(transformer, rl_agent, DataLoader(TensorDataset(data_tensor, torch.randint(0, 3, (1000, 3)))), env)
trainer.pretrain_transformer()
trainer.train_rl_agent()
trainer.save_models()

# Evaluator & Plotter
evaluator = MultiAssetEvaluator()
plotter = MultiAssetPlotter(pd.DataFrame(data_tensor[:, 3, :].numpy(), columns=['AAPL', 'TSLA', 'BTC-USD']))

# Trader
trader = MultiAssetTrader(transformer, rl_agent, evaluator)
trader.load_models()
trader.trade(data_tensor[-1])
evaluator.summary()
plotter.plot_signals(evaluator.get_df(), asset_idx=0)
