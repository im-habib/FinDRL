import numpy as np

# Trading parameters
TRANSACTION_COST = 0.01  # $0.01 per share
INITIAL_BALANCE = 10000
RISK_FREE_RATE = 0.02  # Annual risk-free rate

# Technical indicator parameters
INDICATOR_CONFIG = {
    'macd': {'fast': 12, 'slow': 26, 'signal': 9},
    'rsi': {'period': 14},
    'bollinger': {'period': 20},
    # Add other indicator parameters
}

# Strategy parameters
STRATEGY_NAMES = [
    'macd', 'rsi', 'bollinger', 'ma_crossover', 
    'ichimoku', 'atr', 'vwma', 'momentum'
]