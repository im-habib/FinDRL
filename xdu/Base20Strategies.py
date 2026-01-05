import math
import optuna
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.simplefilter("ignore")

# Helper functions (unchanged)
def calculate_average(data):
    return sum(data) / len(data) if data else 0

def calculate_standard_deviation(data):
    if not data:
        return 0
    mean = calculate_average(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return math.sqrt(variance)

def calculate_stochastic_rsi(prices, period=14):
    if len(prices) < period:
        return 0, 0

    rsi_values = []
    for i in range(len(prices) - 1):
        change = prices[i + 1] - prices[i]
        gain = change if change > 0 else 0
        loss = -change if change < 0 else 0
        rsi_values.append((gain, loss))

    if len(rsi_values) < period:
        return 0, 0

    gains = [x[0] for x in rsi_values[-period:]]
    losses = [x[1] for x in rsi_values[-period:]]
    avg_gain = calculate_average(gains)
    avg_loss = calculate_average(losses)

    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs)) if rs != 0 else 0

    current_rsi = rsi
    rsi_high = max(rsi_values[-period:], key=lambda x: x[0])[0]
    rsi_low = min(rsi_values[-period:], key=lambda x: x[1])[1]

    k = ((current_rsi - rsi_low) / (rsi_high - rsi_low)) * 100 if rsi_high != rsi_low else 0
    d = calculate_average([k] * 3)
    return k, d

def calculate_metrics(positions, prices, initial_balance, transaction_cost=0.01):
    """Calculate trading metrics with transaction costs"""
    equity_curve = [initial_balance]
    profits = []
    losses = []
    current_equity = initial_balance
    peak = initial_balance
    max_drawdown = 0

    for i, (entry_price, exit_price, shares) in enumerate(positions):
        if entry_price and exit_price:
            # Calculate P/L including transaction costs (entry + exit)
            pl = (exit_price - entry_price) * shares - (2 * transaction_cost * shares)
            current_equity += pl
            equity_curve.append(current_equity)
            peak = max(peak, current_equity)
            drawdown = peak - current_equity
            max_drawdown = max(max_drawdown, drawdown)

            if pl > 0:
                profits.append((i, pl))
            elif pl < 0:
                losses.append((i, pl))

    total_pl = current_equity - initial_balance
    return max_drawdown, profits, losses, total_pl, equity_curve


# Project First Part: Indicators Implementation and stratigies to find the top return
class TradingStrategies:
    def __init__(self, df, initial_balance=10000):
        self.opens = df['open'].tolist()
        self.highs = df['high'].tolist()
        self.lows = df['low'].tolist()
        self.closes = df['close'].tolist()
        self.volumes = df['volume'].tolist()
        self.dates = df.index.tolist()
        self.initial_balance = initial_balance
        self.transaction_cost = 0.01  # $0.01 per share

    def run_strategy(self, signal_func):
        """Generic strategy runner with position sizing"""
        positions = []  # (entry_price, exit_price, shares)
        entry_price = None
        available_balance = self.initial_balance

        for i in range(len(self.closes)):
            signal = signal_func(i)
            if signal and not entry_price and i < len(self.closes) - 1:
                # Calculate shares based on available balance
                shares = int(available_balance / (self.opens[i + 1] + self.transaction_cost))
                if shares > 0:
                    entry_price = self.opens[i + 1]
                    positions.append((entry_price, None, shares))
            elif entry_price and not signal:
                last_pos = positions[-1]
                shares = last_pos[2]
                exit_price = self.closes[i]
                positions[-1] = (entry_price, exit_price, shares)
                entry_price = None
                # Update available balance after trade
                pl = (exit_price - last_pos[0]) * shares - (2 * self.transaction_cost * shares)
                available_balance += pl

        # Close any open position
        if entry_price and positions and positions[-1][1] is None:
            shares = positions[-1][2]
            positions[-1] = (entry_price, self.closes[-1], shares)

        max_dd, profits, losses, total_pl, equity = calculate_metrics(
            positions, self.closes, self.initial_balance, self.transaction_cost
        )

        # Prepare results
        result = {
            'Date': self.dates,
            'Equity': [self.initial_balance] + [0] * (len(self.dates) - 1)
        }
        profit_data = {f'Profit_{i}': 0 for i in range(len(self.dates))}
        loss_data = {f'Loss_{i}': 0 for i in range(len(self.dates))}

        equity_idx = 1
        for t, p in profits:
            result['Equity'][t + 1:] = [equity[equity_idx]] * (len(self.dates) - t - 1)
            profit_data[f'Profit_{t}'] = p
            equity_idx += 1
        for t, l in losses:
            result['Equity'][t + 1:] = [equity[equity_idx]] * (len(self.dates) - t - 1)
            loss_data[f'Loss_{t}'] = l
            equity_idx += 1

        result.update(profit_data)
        result.update(loss_data)
        result['Max_Drawdown'] = [max_dd] * len(self.dates)
        result['Total_PL'] = [total_pl] * len(self.dates)

        return pd.DataFrame(result)

    def gaussian_channel(self, period=20):
        def signal(i):
            if i < period:
                return False
            mean = calculate_average(self.closes[i-period:i])
            std = calculate_standard_deviation(self.closes[i-period:i])
            upper_band = mean + (2 * std)
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return self.closes[i] > upper_band and k > d
        return self.run_strategy(signal)

    def ma_crossover(self, fast_period=10, slow_period=20):
        def signal(i):
            if i < slow_period:
                return False
            fast_ma = calculate_average(self.closes[i-fast_period:i])
            slow_ma = calculate_average(self.closes[i-slow_period:i])
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            k_prev = calculate_stochastic_rsi(self.closes[:i])[0]
            return fast_ma > slow_ma and k > k_prev
        return self.run_strategy(signal)

    def bollinger_bands(self, period=20):
        def signal(i):
            if i < period:
                return False
            mean = calculate_average(self.closes[i-period:i])
            std = calculate_standard_deviation(self.closes[i-period:i])
            upper_band = mean + (2 * std)
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return self.closes[i] > upper_band and k > 20
        return self.run_strategy(signal)

    def parabolic_sar(self):
        def signal(i):
            if i < 2:
                return False
            sar = min(self.lows[:i])
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            k_prev = calculate_stochastic_rsi(self.closes[:i])[0]
            return self.closes[i] > sar and k > k_prev
        return self.run_strategy(signal)

    def ichimoku_cloud(self, period=26):
        def signal(i):
            if i < period:
                return False
            tenkan = (max(self.highs[i-9:i]) + min(self.lows[i-9:i])) / 2
            kijun = (max(self.highs[i-period:i]) + min(self.lows[i-period:i])) / 2
            senkou_a = (tenkan + kijun) / 2
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return self.closes[i] > senkou_a and k > 50
        return self.run_strategy(signal)

    def macd(self, fast=12, slow=26, signal=9):
        def signal(i):
            if i < slow:
                return False
            ema_fast = calculate_average(self.closes[i-fast:i])
            ema_slow = calculate_average(self.closes[i-slow:i])
            macd_line = ema_fast - ema_slow
            signal_line = calculate_average(self.closes[i-signal:i])
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return macd_line > signal_line and k > d
        return self.run_strategy(signal)

    def rsi(self, period=14):
        def signal(i):
            if i < period:
                return False
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            k_prev = calculate_stochastic_rsi(self.closes[:i])[0]
            rsi_val = calculate_stochastic_rsi(self.closes[:i+1])[0]
            return rsi_val < 30 and k > k_prev
        return self.run_strategy(signal)

    def adx(self, period=14):
        def signal(i):
            if i < period:
                return False
            up_moves = [self.highs[j] - self.highs[j-1] for j in range(i-period+1, i+1)]
            down_moves = [self.lows[j-1] - self.lows[j] for j in range(i-period+1, i+1)]
            adx = calculate_average([abs(u - d) for u, d in zip(up_moves, down_moves)])
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return adx > 25 and k > d
        return self.run_strategy(signal)

    def atr(self, period=14):
        def signal(i):
            if i < period:
                return False
            tr = [max(self.highs[j] - self.lows[j],
                     abs(self.highs[j] - self.closes[j-1]),
                     abs(self.lows[j] - self.closes[j-1]))
                  for j in range(i-period+1, i+1)]
            atr = calculate_average(tr)
            upper_band = self.closes[i] + atr
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            k_prev = calculate_stochastic_rsi(self.closes[:i])[0]
            return self.closes[i] > upper_band and k > k_prev
        return self.run_strategy(signal)

    def vwma(self, period=20):
        def signal(i):
            if i < period:
                return False
            price_vol = sum(p * v for p, v in zip(self.closes[i-period:i], self.volumes[i-period:i]))
            vol_sum = sum(self.volumes[i-period:i])
            vwma = price_vol / vol_sum if vol_sum != 0 else 0
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return self.closes[i] > vwma and k > d
        return self.run_strategy(signal)

    def donchian_channel(self, period=20):
        def signal(i):
            if i < period:
                return False
            upper_channel = max(self.highs[i-period:i])
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return self.closes[i] > upper_channel and k > 20
        return self.run_strategy(signal)

    def keltner_channel(self, period=20):
        def signal(i):
            if i < period:
                return False
            typical_price = [(h + l + c) / 3 for h, l, c in
                           zip(self.highs[i-period:i], self.lows[i-period:i], self.closes[i-period:i])]
            ema = calculate_average(typical_price)
            atr = calculate_average([max(h - l) for h, l in zip(self.highs[i-period:i], self.lows[i-period:i])])
            upper_band = ema + (2 * atr)
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return self.closes[i] > upper_band and k > d
        return self.run_strategy(signal)

    def supertrend(self, period=10, multiplier=3):
        def signal(i):
            if i < period:
                return False
            tr = [max(self.highs[j] - self.lows[j]) for j in range(i-period, i)]
            atr = calculate_average(tr)
            basic_upper = (max(self.highs[i-period:i]) + min(self.lows[i-period:i])) / 2 + (multiplier * atr)
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return self.closes[i] > basic_upper and k > 20
        return self.run_strategy(signal)

    def fibonacci(self, period=20):
        def signal(i):
            if i < period:
                return False
            high = max(self.highs[i-period:i])
            low = min(self.lows[i-period:i])
            fib_618 = low + (high - low) * 0.618
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return abs(self.closes[i] - fib_618) < (high - low) * 0.05 and k > d
        return self.run_strategy(signal)

    def price_action(self):
        def signal(i):
            if i < 1:
                return False
            bullish_candle = self.closes[i] > self.opens[i]
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            k_prev = calculate_stochastic_rsi(self.closes[:i])[0]
            return bullish_candle and k > k_prev
        return self.run_strategy(signal)

    def volume_spike(self, period=20):
        def signal(i):
            if i < period:
                return False
            avg_volume = calculate_average(self.volumes[i-period:i-1])
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return self.volumes[i] > (2 * avg_volume) and k > d
        return self.run_strategy(signal)

    def momentum(self, period=10):
        def signal(i):
            if i < period:
                return False
            momentum = self.closes[i] - self.closes[i-period]
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            k_prev = calculate_stochastic_rsi(self.closes[:i])[0]
            return momentum > 0 and k > k_prev
        return self.run_strategy(signal)

    def williams_r(self, period=14):
        def signal(i):
            if i < period:
                return False
            highest_high = max(self.highs[i-period:i])
            lowest_low = min(self.lows[i-period:i])
            wr = ((highest_high - self.closes[i]) / (highest_high - lowest_low)) * -100
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            k_prev = calculate_stochastic_rsi(self.closes[:i])[0]
            return wr < -80 and k > k_prev
        return self.run_strategy(signal)

    def cmf(self, period=20):
        def signal(i):
            if i < period:
                return False
            mfv = [((self.closes[j] - self.lows[j]) - (self.highs[j] - self.closes[j])) /
                   (self.highs[j] - self.lows[j]) * self.volumes[j]
                   if (self.highs[j] - self.lows[j]) != 0 else 0
                   for j in range(i-period, i)]
            cmf = sum(mfv) / sum(self.volumes[i-period:i]) if sum(self.volumes[i-period:i]) != 0 else 0
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            return cmf > 0 and k > d
        return self.run_strategy(signal)

    def obv(self):
        def signal(i):
            if i < 1:
                return False
            obv = 0
            for j in range(1, i+1):
                if self.closes[j] > self.closes[j-1]:
                    obv += self.volumes[j]
                elif self.closes[j] < self.closes[j-1]:
                    obv -= self.volumes[j]
            k, d = calculate_stochastic_rsi(self.closes[:i+1])
            k_prev = calculate_stochastic_rsi(self.closes[:i])[0]
            return obv > 0 and k > k_prev
        return self.run_strategy(signal)


# strategies = TradingStrategies(df, initial_balance=10000)
# result = strategies.gaussian_channel()
# print(result[['Date', 'Equity', 'Max_Drawdown', 'Total_PL']].head())
# print("\nSample profits/losses:")
# print(result.filter(like='Profit').sum())
# print(result.filter(like='Loss').sum())
# # path="/content/drive/MyDrive/StockStrategies/xdu-thesis/data"

# if not os.path.exists(path):
#   os.mkdir(path)

# dp = f"{path}/IXIC.csv"

# # Load or Download Data
# if os.path.exists(dp):
#     data = pd.read_csv(dp)
# # Preprocess Data
# if 'date' not in data.columns:
#     data.reset_index(inplace=True)  # Reset index to bring 'date' as a column

# # Convert column names to lowercase
# data.columns = data.columns.str.lower()

# # Ensure 'date' is the index
# data["date"] = pd.to_datetime(data["date"])  # Convert to datetime format
# data.set_index("date", inplace=True)
# # data = data.drop("unnamed: 0", axis=1)

# Second Part:  Implementation with IndicatorOptimizer Class
class IndicatorOptimizer:
    def __init__(self, df, initial_balance=5000):
        self.opens = df['open'].tolist()
        self.highs = df['high'].tolist()
        self.lows = df['low'].tolist()
        self.closes = df['close'].tolist()
        self.volumes = df['volume'].tolist()
        self.dates = df.index.tolist()
        self.initial_balance = initial_balance
        self.transaction_cost = 0.01
        self.optimized_results = {}

    def run_strategy(self, signal_func, positions=None):
        if positions is None:
            positions = []  # (entry_price, exit_price, shares)
        entry_price = None
        available_balance = self.initial_balance

        for i in range(len(self.closes)):
            try:
                signal = signal_func(i)
                if signal and not entry_price and i < len(self.closes) - 1:
                    shares = int(available_balance / (self.opens[i + 1] + self.transaction_cost))
                    if shares > 0:
                        entry_price = self.opens[i + 1]
                        positions.append((entry_price, None, shares))
                elif entry_price and not signal:
                    last_pos = positions[-1]
                    shares = last_pos[2]
                    exit_price = self.closes[i]
                    positions[-1] = (entry_price, exit_price, shares)
                    entry_price = None
                    pl = (exit_price - last_pos[0]) * shares - (2 * self.transaction_cost * shares)
                    available_balance += pl
            except Exception as e:
                print(f"Error at index {i}: {e}")
                continue

        if entry_price and positions and positions[-1][1] is None:
            shares = positions[-1][2]
            positions[-1] = (entry_price, self.closes[-1], shares)

        max_dd, profits, losses, total_pl, equity = calculate_metrics(
            positions, self.closes, self.initial_balance, self.transaction_cost
        )
        return total_pl, max_dd, positions, equity

    # Objective functions for each indicator
    def objective_gaussian_channel(self, trial):
        period = trial.suggest_int('period', 10, 50, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            mean = calculate_average(self.closes[i-period:i])
            std = calculate_standard_deviation(self.closes[i-period:i])
            upper_band = mean + (2 * std)
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return self.closes[i] > upper_band and k > d
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_ma_crossover(self, trial):
        fast_period = trial.suggest_int('fast_period', 5, 20, step=5)
        slow_period = trial.suggest_int('slow_period', 20, 50, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < slow_period: return False
            fast_ma = calculate_average(self.closes[i-fast_period:i])
            slow_ma = calculate_average(self.closes[i-slow_period:i])
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            k_prev = calculate_stochastic_rsi(self.closes[:i], rsi_period)[0]
            return fast_ma > slow_ma and k > k_prev
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_bollinger_bands(self, trial):
        period = trial.suggest_int('period', 10, 50, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            mean = calculate_average(self.closes[i-period:i])
            std = calculate_standard_deviation(self.closes[i-period:i])
            upper_band = mean + (2 * std)
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return self.closes[i] > upper_band and k > 20
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_parabolic_sar(self, trial):
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < 2: return False
            sar = min(self.lows[:i])
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            k_prev = calculate_stochastic_rsi(self.closes[:i], rsi_period)[0]
            return self.closes[i] > sar and k > k_prev
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_ichimoku_cloud(self, trial):
        period = trial.suggest_int('period', 20, 50, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            tenkan = (max(self.highs[i-9:i]) + min(self.lows[i-9:i])) / 2
            kijun = (max(self.highs[i-period:i]) + min(self.lows[i-period:i])) / 2
            senkou_a = (tenkan + kijun) / 2
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return self.closes[i] > senkou_a and k > 50
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_macd(self, trial):
        fast = trial.suggest_int('fast', 5, 20, step=5)
        slow = trial.suggest_int('slow', 20, 50, step=5)
        signal = trial.suggest_int('signal', 5, 15, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < slow: return False
            ema_fast = calculate_average(self.closes[i-fast:i])
            ema_slow = calculate_average(self.closes[i-slow:i])
            macd_line = ema_fast - ema_slow
            signal_line = calculate_average(self.closes[i-signal:i])
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return macd_line > signal_line and k > d
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_rsi(self, trial):
        period = trial.suggest_int('period', 10, 20, step=2)
        threshold = trial.suggest_int('threshold', 20, 40, step=5)
        def signal(i):
            if i < period: return False
            k, d = calculate_stochastic_rsi(self.closes[:i+1], period)
            k_prev = calculate_stochastic_rsi(self.closes[:i], period)[0]
            rsi_val = calculate_stochastic_rsi(self.closes[:i+1], period)[0]
            return rsi_val < threshold and k > k_prev
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_adx(self, trial):
        period = trial.suggest_int('period', 10, 20, step=2)
        threshold = trial.suggest_int('threshold', 20, 40, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            up_moves = [self.highs[j] - self.highs[j-1] for j in range(i-period+1, i+1)]
            down_moves = [self.lows[j-1] - self.lows[j] for j in range(i-period+1, i+1)]
            adx = calculate_average([abs(u - d) for u, d in zip(up_moves, down_moves)])
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return adx > threshold and k > d
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_atr(self, trial):
        period = trial.suggest_int('period', 10, 20, step=2)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            tr = [max(self.highs[j] - self.lows[j], abs(self.highs[j] - self.closes[j-1]), abs(self.lows[j] - self.closes[j-1]))
                  for j in range(i-period+1, i+1)]
            atr = calculate_average(tr)
            upper_band = self.closes[i] + atr
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            k_prev = calculate_stochastic_rsi(self.closes[:i], rsi_period)[0]
            return self.closes[i] > upper_band and k > k_prev
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_vwma(self, trial):
        period = trial.suggest_int('period', 10, 50, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            price_vol = sum(p * v for p, v in zip(self.closes[i-period:i], self.volumes[i-period:i]))
            vol_sum = sum(self.volumes[i-period:i])
            vwma = price_vol / vol_sum if vol_sum != 0 else 0
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return self.closes[i] > vwma and k > d
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_donchian_channel(self, trial):
        period = trial.suggest_int('period', 10, 50, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            upper_channel = max(self.highs[i-period:i])
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return self.closes[i] > upper_channel and k > 20
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_keltner_channel(self, trial):
        period = trial.suggest_int('period', 10, 50, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            typical_price = [(h + l + c) / 3 for h, l, c in zip(self.highs[i-period:i], self.lows[i-period:i], self.closes[i-period:i])]
            ema = calculate_average(typical_price)
            atr = calculate_average([max(h - l) for h, l in zip(self.highs[i-period:i], self.lows[i-period:i])])
            upper_band = ema + (2 * atr)
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return self.closes[i] > upper_band and k > d
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_supertrend(self, trial):
        period = trial.suggest_int('period', 5, 20, step=5)
        multiplier = trial.suggest_float('multiplier', 1, 5, step=0.5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            tr = [max(self.highs[j] - self.lows[j]) for j in range(i-period, i)]
            atr = calculate_average(tr)
            basic_upper = (max(self.highs[i-period:i]) + min(self.lows[i-period:i])) / 2 + (multiplier * atr)
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return self.closes[i] > basic_upper and k > 20
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_fibonacci(self, trial):
        period = trial.suggest_int('period', 10, 50, step=5)
        tolerance = trial.suggest_float('tolerance', 0.01, 0.1, step=0.01)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            high = max(self.highs[i-period:i])
            low = min(self.lows[i-period:i])
            fib_618 = low + (high - low) * 0.618
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return abs(self.closes[i] - fib_618) < (high - low) * tolerance and k > d
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_price_action(self, trial):
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < 1: return False
            bullish_candle = self.closes[i] > self.opens[i]
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            k_prev = calculate_stochastic_rsi(self.closes[:i], rsi_period)[0]
            return bullish_candle and k > k_prev
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_volume_spike(self, trial):
        period = trial.suggest_int('period', 10, 50, step=5)
        multiplier = trial.suggest_float('multiplier', 1.5, 3, step=0.1)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            avg_volume = calculate_average(self.volumes[i-period:i-1])
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return self.volumes[i] > (multiplier * avg_volume) and k > d
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_momentum(self, trial):
        period = trial.suggest_int('period', 5, 20, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            momentum = self.closes[i] - self.closes[i-period]
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            k_prev = calculate_stochastic_rsi(self.closes[:i], rsi_period)[0]
            return momentum > 0 and k > k_prev
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_williams_r(self, trial):
        period = trial.suggest_int('period', 10, 20, step=2)
        threshold = trial.suggest_int('threshold', -90, -70, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            highest_high = max(self.highs[i-period:i])
            lowest_low = min(self.lows[i-period:i])
            wr = ((highest_high - self.closes[i]) / (highest_high - lowest_low)) * -100
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            k_prev = calculate_stochastic_rsi(self.closes[:i], rsi_period)[0]
            return wr < threshold and k > k_prev
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_cmf(self, trial):
        period = trial.suggest_int('period', 10, 50, step=5)
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < period: return False
            mfv = [((self.closes[j] - self.lows[j]) - (self.highs[j] - self.closes[j])) /
                   (self.highs[j] - self.lows[j]) * self.volumes[j]
                   if (self.highs[j] - self.lows[j]) != 0 else 0
                   for j in range(i-period, i)]
            cmf = sum(mfv) / sum(self.volumes[i-period:i]) if sum(self.volumes[i-period:i]) != 0 else 0
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            return cmf > 0 and k > d
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def objective_obv(self, trial):
        rsi_period = trial.suggest_int('rsi_period', 10, 20, step=2)
        def signal(i):
            if i < 1: return False
            obv = 0
            for j in range(1, i+1):
                if self.closes[j] > self.closes[j-1]:
                    obv += self.volumes[j]
                elif self.closes[j] < self.closes[j-1]:
                    obv -= self.volumes[j]
            k, d = calculate_stochastic_rsi(self.closes[:i+1], rsi_period)
            k_prev = calculate_stochastic_rsi(self.closes[:i], rsi_period)[0]
            return obv > 0 and k > k_prev
        total_pl, max_dd, _, _ = self.run_strategy(signal)
        return max_dd * -1 + total_pl

    def optimize_all_indicators(self, n_trials=50):
        indicators = [
            'gaussian_channel', 'ma_crossover', 'bollinger_bands', 'parabolic_sar',
            'ichimoku_cloud', 'macd', 'rsi', 'adx', 'atr', 'vwma', 'donchian_channel',
            'keltner_channel', 'supertrend', 'fibonacci', 'price_action', 'volume_spike',
            'momentum', 'williams_r', 'cmf', 'obv'
        ]
        self.optimized_results = {}

        for indicator in indicators:
            print(f"Optimizing {indicator}...")
            study = optuna.create_study(direction='maximize', pruner=optuna.pruners.MedianPruner())
            objective_func = getattr(self, f'objective_{indicator}')
            try:
                study.optimize(objective_func, n_trials=n_trials, n_jobs=-1)  # Parallelize
                best_params = study.best_params
                # Construct signal function with best parameters
                if indicator == 'gaussian_channel':
                    signal = lambda i: i >= best_params['period'] and self.closes[i] > calculate_average(self.closes[i-best_params['period']:i]) + 2*calculate_standard_deviation(self.closes[i-best_params['period']:i]) and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[1]
                elif indicator == 'ma_crossover':
                    signal = lambda i: i >= best_params['slow_period'] and calculate_average(self.closes[i-best_params['fast_period']:i]) > calculate_average(self.closes[i-best_params['slow_period']:i]) and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i], best_params['rsi_period'])[0]
                elif indicator == 'bollinger_bands':
                    signal = lambda i: i >= best_params['period'] and self.closes[i] > calculate_average(self.closes[i-best_params['period']:i]) + 2*calculate_standard_deviation(self.closes[i-best_params['period']:i]) and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > 20
                elif indicator == 'parabolic_sar':
                    signal = lambda i: i >= 2 and self.closes[i] > min(self.lows[:i]) and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i], best_params['rsi_period'])[0]
                elif indicator == 'ichimoku_cloud':
                    signal = lambda i: i >= best_params['period'] and self.closes[i] > ((max(self.highs[i-9:i]) + min(self.lows[i-9:i])) / 2 + (max(self.highs[i-best_params['period']:i]) + min(self.lows[i-best_params['period']:i])) / 2) / 2 and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > 50
                elif indicator == 'macd':
                    signal = lambda i: i >= best_params['slow'] and (calculate_average(self.closes[i-best_params['fast']:i]) - calculate_average(self.closes[i-best_params['slow']:i])) > calculate_average(self.closes[i-best_params['signal']:i]) and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[1]
                elif indicator == 'rsi':
                    signal = lambda i: i >= best_params['period'] and calculate_stochastic_rsi(self.closes[:i+1], best_params['period'])[0] < best_params['threshold'] and calculate_stochastic_rsi(self.closes[:i+1], best_params['period'])[0] > calculate_stochastic_rsi(self.closes[:i], best_params['period'])[0]
                elif indicator == 'adx':
                    signal = lambda i: i >= best_params['period'] and calculate_average([abs(self.highs[j] - self.highs[j-1] - (self.lows[j-1] - self.lows[j])) for j in range(i-best_params['period']+1, i+1)]) > best_params['threshold'] and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[1]
                elif indicator == 'atr':
                    signal = lambda i: i >= best_params['period'] and self.closes[i] > self.closes[i] + calculate_average([max(self.highs[j] - self.lows[j], abs(self.highs[j] - self.closes[j-1]), abs(self.lows[j] - self.closes[j-1])) for j in range(i-best_params['period']+1, i+1)]) and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i], best_params['rsi_period'])[0]
                elif indicator == 'vwma':
                    signal = lambda i: i >= best_params['period'] and self.closes[i] > sum(p * v for p, v in zip(self.closes[i-best_params['period']:i], self.volumes[i-best_params['period']:i])) / sum(self.volumes[i-best_params['period']:i]) and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[1]
                elif indicator == 'donchian_channel':
                    signal = lambda i: i >= best_params['period'] and self.closes[i] > max(self.highs[i-best_params['period']:i]) and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > 20
                elif indicator == 'keltner_channel':
                    signal = lambda i: i >= best_params['period'] and self.closes[i] > calculate_average([(h + l + c) / 3 for h, l, c in zip(self.highs[i-best_params['period']:i], self.lows[i-best_params['period']:i], self.closes[i-best_params['period']:i])]) + 2 * calculate_average([max(h - l) for h, l in zip(self.highs[i-best_params['period']:i], self.lows[i-best_params['period']:i])]) and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[1]
                elif indicator == 'supertrend':
                    signal = lambda i: i >= best_params['period'] and self.closes[i] > ((max(self.highs[i-best_params['period']:i]) + min(self.lows[i-best_params['period']:i])) / 2 + (best_params['multiplier'] * calculate_average([max(self.highs[j] - self.lows[j]) for j in range(i-best_params['period'], i)]))) and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > 20
                elif indicator == 'fibonacci':
                    signal = lambda i: i >= best_params['period'] and abs(self.closes[i] - (min(self.lows[i-best_params['period']:i]) + (max(self.highs[i-best_params['period']:i]) - min(self.lows[i-best_params['period']:i])) * 0.618)) < (max(self.highs[i-best_params['period']:i]) - min(self.lows[i-best_params['period']:i])) * best_params['tolerance'] and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[1]
                elif indicator == 'price_action':
                    signal = lambda i: i >= 1 and self.closes[i] > self.opens[i] and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i], best_params['rsi_period'])[0]
                elif indicator == 'volume_spike':
                    signal = lambda i: i >= best_params['period'] and self.volumes[i] > (best_params['multiplier'] * calculate_average(self.volumes[i-best_params['period']:i-1])) and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[1]
                elif indicator == 'momentum':
                    signal = lambda i: i >= best_params['period'] and self.closes[i] - self.closes[i-best_params['period']] > 0 and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i], best_params['rsi_period'])[0]
                elif indicator == 'williams_r':
                    signal = lambda i: i >= best_params['period'] and ((max(self.highs[i-best_params['period']:i]) - self.closes[i]) / (max(self.highs[i-best_params['period']:i]) - min(self.lows[i-best_params['period']:i]))) * -100 < best_params['threshold'] and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i], best_params['rsi_period'])[0]
                elif indicator == 'cmf':
                    signal = lambda i: i >= best_params['period'] and sum([((self.closes[j] - self.lows[j]) - (self.highs[j] - self.closes[j])) / (self.highs[j] - self.lows[j]) * self.volumes[j] if (self.highs[j] - self.lows[j]) != 0 else 0 for j in range(i-best_params['period'], i)]) / sum(self.volumes[i-best_params['period']:i]) > 0 and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[1]
                elif indicator == 'obv':
                    signal = lambda i: i >= 1 and sum([self.volumes[j] if self.closes[j] > self.closes[j-1] else -self.volumes[j] if self.closes[j] < self.closes[j-1] else 0 for j in range(1, i+1)]) > 0 and calculate_stochastic_rsi(self.closes[:i+1], best_params['rsi_period'])[0] > calculate_stochastic_rsi(self.closes[:i], best_params['rsi_period'])[0]
                else:
                    raise ValueError(f"Unknown indicator: {indicator}")

                total_pl, max_dd, positions, equity = self.run_strategy(signal)
                self.optimized_results[indicator] = {
                    'parameters': best_params,
                    'total_pl': total_pl,
                    'max_dd': max_dd,
                    'positions': positions,
                    'equity': equity
                }
                print(f"\nOptimization for {indicator} completed:")
                print(f"Best parameters: {best_params}")
                print(f"Total P&L: ${total_pl:.2f}")
                print(f"Max Drawdown: {max_dd:.2f}")
            except Exception as e:
                print(f"Error optimizing {indicator}: {e}")
                continue

        # Create dataset
        if self.optimized_results:
            results_df = pd.DataFrame.from_dict(
                {k: v for k, v in self.optimized_results.items()},
                orient='index'
            ).reset_index().rename(columns={'index': 'indicator'})
            return results_df
        else:
            raise ValueError("No successful optimizations completed.")

    def plot_results(self):
        if not self.optimized_results:
            print("No results to plot.")
            return
        results_df = self.optimized_results
        indicators = list(results_df.keys())
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 18), sharex=True)

        # Plot 1: Total P&L
        total_pl_values = [results_df[ind]['total_pl'] for ind in indicators]
        ax1.bar(indicators, total_pl_values, color='blue')
        ax1.set_title('Total P&L by Indicator')
        ax1.set_ylabel('Total P&L ($)')
        ax1.grid(True)
        for i, v in enumerate(total_pl_values):
            ax1.text(i, v, f'${v:.2f}', ha='center', va='bottom')

        # Plot 2: Max Drawdown
        max_dd_values = [results_df[ind]['max_dd'] for ind in indicators]
        ax2.bar(indicators, max_dd_values, color='red')
        ax2.set_title('Maximum Drawdown by Indicator')
        ax2.set_ylabel('Max Drawdown ($)')
        ax2.grid(True)
        for i, v in enumerate(max_dd_values):
            ax2.text(i, v, f'{v:.2f}', ha='center', va='bottom')

        # Plot 3: Equity Curve (for the best performing indicator)
        best_indicator = max(results_df, key=lambda x: results_df[x]['total_pl'])
        equity = results_df[best_indicator]['equity']
        ax3.plot(self.dates[:len(equity)], equity, label=f'{best_indicator} Equity', color='green')
        ax3.set_title(f'Equity Curve - Best Indicator ({best_indicator})')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Equity ($)')
        ax3.legend()
        ax3.grid(True)

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()