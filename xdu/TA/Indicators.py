import numpy as np

# --------------------------------------------------------------------------
# Helper Functions (very simplified placeholders for demonstration)
# --------------------------------------------------------------------------
def calculate_average(values):
    """Simple helper to compute average (mean)."""
    return np.mean(values)

def calculate_standard_deviation(values):
    """Simple helper to compute standard deviation."""
    return np.std(values, ddof=1)  # ddof=1 for sample std

def calculate_stochastic_rsi(values, period=14):
    """
    Placeholder Stochastic RSI calculation.
    Returns (k, d). 
    Replace with your actual Stochastic RSI logic as needed.
    """
    if len(values) < period:
        return (np.nan, np.nan)
    min_val = np.min(values[-period:])
    max_val = np.max(values[-period:])
    if max_val - min_val == 0:
        k_value = 50.0
    else:
        k_value = (values[-1] - min_val) / (max_val - min_val) * 100
    d_value = k_value  # For demo, just set d = k
    return (k_value, d_value)

# --------------------------------------------------------------------------
# Main Class
# --------------------------------------------------------------------------
class StockIndicators:
    def __init__(self, df):
        """
        df must have columns: 'open', 'high', 'low', 'close', 'volume'
        """
        self.df = df.copy()
        self.opens = df['open'].values
        self.highs = df['high'].values
        self.lows = df['low'].values
        self.closes = df['close'].values
        self.volumes = df['volume'].values
        self.original_columns = set(self.df.columns)

    # ----------------------------------------------------------------
    # 1) Gaussian Channel
    # ----------------------------------------------------------------
    def gaussian_channel(self, period=20):
        """
        Calculates rolling mean, std, and upper_band for the closes.
        Also calculates and stores Stoch RSI (k, d) for reference.
        """
        mean_list = []
        std_list = []
        upper_list = []
        k_list = []
        d_list = []

        for i in range(len(self.closes)):
            if i < period:
                mean_list.append(np.nan)
                std_list.append(np.nan)
                upper_list.append(np.nan)
            else:
                window = self.closes[i-period:i]
                mean_val = calculate_average(window)
                std_val = calculate_standard_deviation(window)
                upper_band = mean_val + 2 * std_val
                mean_list.append(mean_val)
                std_list.append(std_val)
                upper_list.append(upper_band)

            # Also store Stochastic RSI at each bar
            k_val, d_val = calculate_stochastic_rsi(self.closes[:i+1])
            k_list.append(k_val)
            d_list.append(d_val)

        self.df['gaussian_mean'] = mean_list
        self.df['gaussian_std'] = std_list
        self.df['gaussian_upper'] = upper_list
        self.df['stoch_k'] = k_list
        self.df['stoch_d'] = d_list

    # ----------------------------------------------------------------
    # 2) MA Crossover
    # ----------------------------------------------------------------
    def ma_crossover(self, fast_period=10, slow_period=20):
        """
        Stores a rolling fast MA and slow MA.
        """
        fast_list = []
        slow_list = []

        for i in range(len(self.closes)):
            if i < slow_period:
                fast_list.append(np.nan)
                slow_list.append(np.nan)
            else:
                fast_ma = calculate_average(self.closes[i - fast_period : i])
                slow_ma = calculate_average(self.closes[i - slow_period : i])
                fast_list.append(fast_ma)
                slow_list.append(slow_ma)

        self.df['ma_fast'] = fast_list
        self.df['ma_slow'] = slow_list

    # ----------------------------------------------------------------
    # 3) Bollinger Bands
    # ----------------------------------------------------------------
    def bollinger_bands(self, period=20):
        """
        Stores Bollinger mean, std, upper band, lower band.
        """
        means = []
        stds = []
        ups = []
        downs = []

        for i in range(len(self.closes)):
            if i < period:
                means.append(np.nan)
                stds.append(np.nan)
                ups.append(np.nan)
                downs.append(np.nan)
            else:
                window = self.closes[i - period : i]
                mean_val = calculate_average(window)
                std_val = calculate_standard_deviation(window)
                up = mean_val + (2 * std_val)
                down = mean_val - (2 * std_val)
                means.append(mean_val)
                stds.append(std_val)
                ups.append(up)
                downs.append(down)

        self.df['boll_mean'] = means
        self.df['boll_std'] = stds
        self.df['boll_up'] = ups
        self.df['boll_down'] = downs

    # ----------------------------------------------------------------
    # 4) Parabolic SAR (very simplified, per snippet)
    # ----------------------------------------------------------------
    def parabolic_sar(self):
        """
        Example from snippet:
          parabolic SAR = min of all lows up to that point (if i>=2), else NaN.
        This is NOT the standard SAR formula, just a demonstration to match snippet.
        """
        sar_list = []
        for i in range(len(self.lows)):
            if i < 2:
                sar_list.append(np.nan)
            else:
                # the snippet does: sar = min(self.lows[:i])
                # We'll store that for each row
                sar_val = np.min(self.lows[:i])
                sar_list.append(sar_val)

        self.df['parabolic_sar'] = sar_list

    # ----------------------------------------------------------------
    # 5) Ichimoku Cloud (tenkan, kijun, senkou_a)
    # ----------------------------------------------------------------
    def ichimoku_cloud(self, period=26):
        tenkan_list = []
        kijun_list = []
        senkou_a_list = []

        for i in range(len(self.closes)):
            if i < period:
                tenkan_list.append(np.nan)
                kijun_list.append(np.nan)
                senkou_a_list.append(np.nan)
            else:
                # tenkan uses 9 bars
                tenkan_val = (np.max(self.highs[i-9:i]) + np.min(self.lows[i-9:i])) / 2
                kijun_val = (np.max(self.highs[i-period:i]) + np.min(self.lows[i-period:i])) / 2
                senkou_a_val = (tenkan_val + kijun_val) / 2
                tenkan_list.append(tenkan_val)
                kijun_list.append(kijun_val)
                senkou_a_list.append(senkou_a_val)

        self.df['ichimoku_tenkan'] = tenkan_list
        self.df['ichimoku_kijun'] = kijun_list
        self.df['ichimoku_senkou_a'] = senkou_a_list

    # ----------------------------------------------------------------
    # 6) MACD
    # ----------------------------------------------------------------
    def macd(self, fast=12, slow=26, signal=9):
        """
        We'll store macd_line and macd_signal as rolling averages 
        (again, simplified approach).
        """
        macd_line_list = []
        signal_line_list = []

        for i in range(len(self.closes)):
            if i < slow:
                macd_line_list.append(np.nan)
                signal_line_list.append(np.nan)
            else:
                ema_fast = calculate_average(self.closes[i - fast : i])
                ema_slow = calculate_average(self.closes[i - slow : i])
                macd_val = ema_fast - ema_slow
                
                # For the signal line, we'll just do a (signal)-period average of closes 
                # per the snippet logic
                if i < signal:
                    sig_val = np.nan
                else:
                    sig_val = calculate_average(self.closes[i - signal : i])
                
                macd_line_list.append(macd_val)
                signal_line_list.append(sig_val)

        self.df['macd_line'] = macd_line_list
        self.df['macd_signal'] = signal_line_list

    # ----------------------------------------------------------------
    # 7) RSI (based on snippet: using stoch RSI again)
    # ----------------------------------------------------------------
    def rsi(self, period=14):
        """
        We'll store a 'rsi_value' column, using the snippet's approach 
        (which actually uses the K from Stochastic RSI).
        """
        rsi_vals = []
        for i in range(len(self.closes)):
            # Calculate stoch RSI
            k_val, _ = calculate_stochastic_rsi(self.closes[:i+1], period=period)
            rsi_vals.append(k_val)

        self.df['rsi_value'] = rsi_vals

    # ----------------------------------------------------------------
    # 8) ADX (based on snippet approach)
    # ----------------------------------------------------------------
    def adx(self, period=14):
        """
        Very simplified snippet-based ADX:
          up_moves = [high[j] - high[j-1]]
          down_moves = [low[j-1] - low[j]]
          adx = average of abs(up_moves - down_moves)
        for the last 'period' bars.
        """
        adx_list = []
        for i in range(len(self.closes)):
            if i < period:
                adx_list.append(np.nan)
            else:
                up_moves = []
                down_moves = []
                for j in range(i-period+1, i+1):
                    up_moves.append(self.highs[j] - self.highs[j-1])
                    down_moves.append(self.lows[j-1] - self.lows[j])
                # Pairwise difference
                diffs = [abs(u - d) for u, d in zip(up_moves, down_moves)]
                adx_val = calculate_average(diffs)
                adx_list.append(adx_val)

        self.df['adx_value'] = adx_list

    # ----------------------------------------------------------------
    # 9) ATR
    # ----------------------------------------------------------------
    def atr(self, period=14):
        """
        ATR per snippet:
          tr = max(high-low, abs(high-prev_close), abs(low-prev_close))
          atr = average(tr over period).
        """
        atr_list = []
        for i in range(len(self.closes)):
            if i < period:
                atr_list.append(np.nan)
            else:
                tr_values = []
                for j in range(i-period+1, i+1):
                    high_low = self.highs[j] - self.lows[j]
                    high_close = abs(self.highs[j] - self.closes[j-1])
                    low_close = abs(self.lows[j] - self.closes[j-1])
                    tr_values.append(max(high_low, high_close, low_close))
                atr_val = calculate_average(tr_values)
                atr_list.append(atr_val)

        self.df['atr_value'] = atr_list

    # ----------------------------------------------------------------
    # 10) VWMA
    # ----------------------------------------------------------------
    def vwma(self, period=20):
        """
        Volume Weighted Moving Average:
          price_vol = sum(closes * volume)
          vol_sum = sum(volume)
          vwma = price_vol / vol_sum
        """
        vwma_list = []
        for i in range(len(self.closes)):
            if i < period:
                vwma_list.append(np.nan)
            else:
                window_close = self.closes[i - period : i]
                window_vol = self.volumes[i - period : i]
                price_vol = np.sum(window_close * window_vol)
                vol_sum = np.sum(window_vol)
                if vol_sum == 0:
                    vwma_val = np.nan
                else:
                    vwma_val = price_vol / vol_sum
                vwma_list.append(vwma_val)

        self.df['vwma_value'] = vwma_list

    # ----------------------------------------------------------------
    # 11) Donchian Channel
    # ----------------------------------------------------------------
    def donchian_channel(self, period=20):
        """
        We'll just store the upper channel from the snippet.
        """
        upper_list = []
        for i in range(len(self.closes)):
            if i < period:
                upper_list.append(np.nan)
            else:
                upper_channel = np.max(self.highs[i - period : i])
                upper_list.append(upper_channel)

        self.df['donchian_upper'] = upper_list

    # ----------------------------------------------------------------
    # 12) Keltner Channel
    # ----------------------------------------------------------------
    def keltner_channel(self, period=20):
        """
        Snippet version:
          typical_price = (h + l + c)/3
          ema = average(typical_price)
          atr = average([h-l])
          upper_band = ema + 2*atr
        We'll store 'keltner_ema', 'keltner_atr', 'keltner_upper'.
        """
        ema_list = []
        atr_list = []
        upper_list = []

        for i in range(len(self.closes)):
            if i < period:
                ema_list.append(np.nan)
                atr_list.append(np.nan)
                upper_list.append(np.nan)
            else:
                tp_window = []
                hl_diff = []
                for j in range(i - period, i):
                    tp_window.append((self.highs[j] + self.lows[j] + self.closes[j]) / 3)
                    hl_diff.append(self.highs[j] - self.lows[j])

                ema_val = calculate_average(tp_window)
                atr_val = calculate_average(hl_diff)
                upper_band = ema_val + (2 * atr_val)

                ema_list.append(ema_val)
                atr_list.append(atr_val)
                upper_list.append(upper_band)

        self.df['keltner_ema'] = ema_list
        self.df['keltner_atr'] = atr_list
        self.df['keltner_upper'] = upper_list

    # ----------------------------------------------------------------
    # 13) Supertrend
    # ----------------------------------------------------------------
    def supertrend(self, period=10, multiplier=3):
        """
        Snippet logic:
          tr = [high - low for j in range(i-period, i)]
          atr = average(tr)
          basic_upper = (max(high[i-period:i]) + min(low[i-period:i]))/2 + (multiplier*atr)
        We'll store 'supertrend_basic_upper'.
        """
        st_upper_list = []
        for i in range(len(self.closes)):
            if i < period:
                st_upper_list.append(np.nan)
            else:
                tr_list = []
                for j in range(i - period, i):
                    tr_list.append(self.highs[j] - self.lows[j])
                atr_val = calculate_average(tr_list)
                highest = np.max(self.highs[i - period : i])
                lowest = np.min(self.lows[i - period : i])
                basic_upper = (highest + lowest) / 2 + (multiplier * atr_val)
                st_upper_list.append(basic_upper)

        self.df['supertrend_basic_upper'] = st_upper_list

    # ----------------------------------------------------------------
    # 14) Fibonacci
    # ----------------------------------------------------------------
    def fibonacci(self, period=20):
        """
        Snippet logic:
          high = max(self.highs[i-period:i])
          low = min(self.lows[i-period:i])
          fib_618 = low + (high - low)*0.618
        We'll store fib_618 in 'fib_618_value'.
        """
        fib_list = []
        for i in range(len(self.closes)):
            if i < period:
                fib_list.append(np.nan)
            else:
                highest = np.max(self.highs[i - period : i])
                lowest = np.min(self.lows[i - period : i])
                fib_618 = lowest + (highest - lowest)*0.618
                fib_list.append(fib_618)

        self.df['fib_618_value'] = fib_list

    # ----------------------------------------------------------------
    # 15) Price Action
    # ----------------------------------------------------------------
    def price_action(self):
        """
        Snippet logic:
          bullish_candle = closes[i] > opens[i].
        We'll store a boolean for each row: True/False if bullish.
        """
        bullish_list = (self.df['Close'] > self.df['Open']).tolist()
        self.df['priceaction_bullish'] = bullish_list

    # ----------------------------------------------------------------
    # 16) Volume Spike
    # ----------------------------------------------------------------
    def volume_spike(self, period=20):
        """
        Snippet logic:
          avg_volume (last period) = average(self.volumes[i-period : i-1])
          If self.volumes[i] > (2 * avg_volume) => spike.
        We'll store 'vol_spike_avg' and a boolean 'vol_spike'.
        """
        vol_avg_list = []
        vol_spike_list = []
        for i in range(len(self.volumes)):
            if i < period:
                vol_avg_list.append(np.nan)
                vol_spike_list.append(False)
            else:
                avg_vol = calculate_average(self.volumes[i - period : i])
                vol_avg_list.append(avg_vol)
                if self.volumes[i] > 2 * avg_vol:
                    vol_spike_list.append(True)
                else:
                    vol_spike_list.append(False)

        self.df['vol_spike_avg'] = vol_avg_list
        self.df['vol_spike'] = vol_spike_list

    # ----------------------------------------------------------------
    # 17) Momentum
    # ----------------------------------------------------------------
    def momentum(self, period=10):
        """
        Snippet logic:
          momentum = closes[i] - closes[i-period].
        We'll store 'momentum_value'.
        """
        mom_list = []
        for i in range(len(self.closes)):
            if i < period:
                mom_list.append(np.nan)
            else:
                mom_val = self.closes[i] - self.closes[i - period]
                mom_list.append(mom_val)

        self.df['momentum_value'] = mom_list

    # ----------------------------------------------------------------
    # 18) Williams %R
    # ----------------------------------------------------------------
    def williams_r(self, period=14):
        """
        Snippet logic:
          highest_high = max(self.highs[i-period:i])
          lowest_low = min(self.lows[i-period:i])
          wr = ((highest_high - close[i]) / (highest_high - lowest_low)) * -100
        We'll store 'williams_r_value'.
        """
        wr_list = []
        for i in range(len(self.closes)):
            if i < period:
                wr_list.append(np.nan)
            else:
                hh = np.max(self.highs[i - period : i])
                ll = np.min(self.lows[i - period : i])
                denom = (hh - ll)
                if denom == 0:
                    wr = np.nan
                else:
                    wr = ((hh - self.closes[i]) / denom) * -100
                wr_list.append(wr)

        self.df['williams_r_value'] = wr_list

    # ----------------------------------------------------------------
    # 19) CMF
    # ----------------------------------------------------------------
    def cmf(self, period=20):
        """
        Snippet logic:
          mfv[j] = (((close - low) - (high - close)) / (high - low)) * volume[j]
          cmf = sum(mfv) / sum(volumes) for the last 'period' bars.
        We'll store 'cmf_value'.
        """
        cmf_list = []
        for i in range(len(self.closes)):
            if i < period:
                cmf_list.append(np.nan)
            else:
                mfv_vals = []
                vol_vals = []
                for j in range(i - period, i):
                    high_low = self.highs[j] - self.lows[j]
                    if high_low == 0:
                        mfv = 0
                    else:
                        mfv = (((self.closes[j] - self.lows[j]) - (self.highs[j] - self.closes[j])) 
                               / high_low) * self.volumes[j]
                    mfv_vals.append(mfv)
                    vol_vals.append(self.volumes[j])
                total_vol = np.sum(vol_vals)
                if total_vol == 0:
                    cmf_val = np.nan
                else:
                    cmf_val = np.sum(mfv_vals) / total_vol
                cmf_list.append(cmf_val)

        self.df['cmf_value'] = cmf_list

    # ----------------------------------------------------------------
    # 20) OBV
    # ----------------------------------------------------------------
    def obv(self):
        """
        Snippet logic:
          obv starts at 0, then for each j from 1..i:
            if close[j] > close[j-1]: obv += volume[j]
            elif close[j] < close[j-1]: obv -= volume[j]
        We'll store 'obv_value' for each row.
        """
        obv_values = []
        for i in range(len(self.closes)):
            if i == 0:
                obv_values.append(0)
            else:
                # compute OBV up to i
                obv_val = 0
                for j in range(1, i+1):
                    if self.closes[j] > self.closes[j-1]:
                        obv_val += self.volumes[j]
                    elif self.closes[j] < self.closes[j-1]:
                        obv_val -= self.volumes[j]
                obv_values.append(obv_val)
        self.df['obv_value'] = obv_values

    # ----------------------------------------------------------------
    # Method: run_all_indicators
    #   Dynamically calls every indicator method so you don't have to 
    #   manually call them one by one.
    # ----------------------------------------------------------------
    def run_all_indicators(self):
        """
        Dynamically finds and calls all indicator methods (those that 
        don't start with underscore or appear in the skip set).
        """
        skip_methods = {
            'run_all_indicators', 'clean_data', '__init__',
            '__module__', '__doc__', '__dict__', '__weakref__'
        }
        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue
            if attr_name in skip_methods:
                continue

            attr = getattr(self, attr_name)
            if callable(attr):
                print(f"Running: {attr_name}")
                attr()  # call the indicator method
        return self

    def get_new_indicator_columns(self):
        """
        Returns a list of columns that were added after the class 
        was initialized—i.e. newly created indicator columns.
        """
        current_columns = set(self.df.columns)
        # The newly added columns are the difference
        new_columns = current_columns - self.original_columns
        return list(new_columns)
    
    # ----------------------------------------------------------------
    # Method: clean_data
    #   Example cleanup: drop rows with NaN in newly created columns.
    #   Also, optionally remove rows with zeros if needed.
    # ----------------------------------------------------------------
    def clean_data(self):
        """
        Drop rows that contain NaN in any newly created indicator columns.
        """
        # Original columns in your dataset:
        original_cols = {'open', 'high', 'low', 'close', 'volume'}
        new_cols = [c for c in self.df.columns if c not in original_cols]

        # Drop rows where any of these new columns has NaN:
        self.df.dropna(subset=new_cols, inplace=True)

        # Optionally drop rows with zeros in these columns:
        # mask = (self.df[new_cols] == 0).any(axis=1)
        # self.df = self.df[~mask]

        return self.df