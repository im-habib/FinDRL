import pandas as pd
from typing import Callable

def create_buy_signal(threshold: float, signal_type: str) -> Callable[[pd.Series], bool]:
    """
    Create a dynamic buy signal function.
    Parameters:
    - threshold: The threshold value for generating the signal.
    - signal_type: The type of signal ('below' or 'cross').
    
    Returns:
    - A function that takes indicator values and returns a boolean for buy signal.
    """
    def buy_signal(indicator_values: pd.Series) -> bool:
        if signal_type == 'below':
            return indicator_values[-1] < threshold
        elif signal_type == 'cross':
            return indicator_values[-1] > threshold and indicator_values[-2] <= threshold
        else:
            raise ValueError(f"Unsupported signal type: {signal_type}")
    
    return buy_signal

def create_sell_signal(threshold: float, signal_type: str) -> Callable[[pd.Series], bool]:
    """
    Create a dynamic sell signal function.
    Parameters:
    - threshold: The threshold value for generating the signal.
    - signal_type: The type of signal ('above' or 'cross').
    
    Returns:
    - A function that takes indicator values and returns a boolean for sell signal.
    """
    def sell_signal(indicator_values: pd.Series) -> bool:
        if signal_type == 'above':
            return indicator_values[-1] > threshold
        elif signal_type == 'cross':
            return indicator_values[-1] < threshold and indicator_values[-2] >= threshold
        else:
            raise ValueError(f"Unsupported signal type: {signal_type}")
    
    return sell_signal
