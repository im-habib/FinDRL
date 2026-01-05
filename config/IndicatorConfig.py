# indicator_config.py

# Define the configuration for each indicator, including data and any specific parameters
indicators_config = {
    # Trend Indicators
    'macd': {'data': 'Close'},                         # MACD
    'adx': {'data': ('High', 'Low', 'Close'), 'timeperiod': 14},  # ADX
    'sar': {'data': ('High', 'Low'), 'acceleration': 0.02, 'maximum': 0.2},  # Parabolic SAR

    # Candlestick Patterns
    'cdldoji': {'data': ('Open', 'High', 'Low', 'Close')},         # Doji pattern
    'cdlengulfing': {'data': ('Open', 'High', 'Low', 'Close')},    # Engulfing pattern
    'cdlhammer': {'data': ('Open', 'High', 'Low', 'Close')},       # Hammer pattern
    'heikin_ashi': 'placeholder',     # Placeholder, requires a custom implementation
    'renko': 'placeholder',           # Placeholder, requires a custom implementation

    # Cycle Indicators
    'elliott_wave': 'placeholder',    # Placeholder, requires a custom implementation
    'fourier_transform': 'placeholder',  # Fourier Transform Analysis placeholder
    'seasonal_analysis': 'placeholder',  # Seasonal Analysis placeholder

    # Momentum Indicators
    'rsi': {'data': 'Close', 'timeperiod': 14},                    # RSI
    'stoch': {'data': ('High', 'Low', 'Close'), 'fastk_period': 14, 'slowk_period': 3, 'slowd_period': 3}, # Stochastic Oscillator
    'willr': {'data': ('High', 'Low', 'Close'), 'timeperiod': 14}, # Williams %R

    # Overlap Indicators
    'sma': {'data': 'Close', 'timeperiod': 50},                    # Simple Moving Average (SMA)
    'ema': {'data': 'Close', 'timeperiod': 50},                    # Exponential Moving Average (EMA)
    'bbands': {'data': 'Close', 'timeperiod': 20, 'nbdevup': 2, 'nbdevdn': 2, 'matype': 0}, # Bollinger Bands
    'ichimoku': 'placeholder',           # Placeholder, requires complex calculation setup

    # Performance Metrics
    'sharpe_ratio': 'placeholder',       # Placeholder for Sharpe Ratio calculation
    'sortino_ratio': 'placeholder',      # Placeholder for Sortino Ratio calculation
    'alpha': 'placeholder',              # Placeholder for Alpha calculation

    # Statistical Indicators
    'correlation': 'placeholder',        # Placeholder for Correlation calculation
    'beta': 'placeholder',               # Placeholder for Beta calculation
    'stddev': {'data': 'Close', 'timeperiod': 20}, # Standard Deviation

    # Utility Indicators
    'fibonacci': 'placeholder',          # Placeholder for Fibonacci Retracement
    'pivot': {'data': ('High', 'Low', 'Close')},                    # Pivot Points
    'vwap': {'data': ('High', 'Low', 'Close', 'Volume')},           # VWAP

    # Volatility Indicators
    'atr': {'data': ('High', 'Low', 'Close'), 'timeperiod': 14},    # ATR
    'vix': 'placeholder',                # Placeholder for VIX (requires external data)

    # Volume Indicators
    'obv': {'data': ('Close', 'Volume')},                           # OBV
    'pvo': {'data': 'Volume', 'fastperiod': 12, 'slowperiod': 26},  # Volume Oscillator (PVO)
    'ad': {'data': ('High', 'Low', 'Close', 'Volume')},             # Accumulation/Distribution Line
    'cmf': 'placeholder'                # Placeholder for Chaikin Money Flow calculation
}
