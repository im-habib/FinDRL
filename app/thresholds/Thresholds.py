import numpy as np
import pandas as pd
from typing import  Tuple

def get_threshold_method(indicator_name: str) -> str:
    # Define the threshold methods for each indicator
    threshold_methods = {
        'sma': 'std_dev',
        'macd': 'z_score',
        'rsi': 'percentile',
        # Add other indicators and their methods here
    }
    return threshold_methods.get(indicator_name, 'percentile')  # Default to 'percentile'

def calculate_thresholds(indicator_values: pd.Series, method: str = 'percentile', **kwargs) -> Tuple[float, float]:
    if method == 'percentile':
        lower_percentile = kwargs.get('lower_percentile', 20)
        upper_percentile = kwargs.get('upper_percentile', 80)
        lower_threshold = np.percentile(indicator_values, lower_percentile)
        upper_threshold = np.percentile(indicator_values, upper_percentile)
    elif method == 'std_dev':
        num_std_dev = kwargs.get('num_std_dev', 1)
        mean = np.mean(indicator_values)
        std_dev = np.std(indicator_values)
        lower_threshold = mean - num_std_dev * std_dev
        upper_threshold = mean + num_std_dev * std_dev
    elif method == 'z_score':
        z_score = kwargs.get('z_score', 1)
        mean = np.mean(indicator_values)
        std_dev = np.std(indicator_values)
        lower_threshold = mean - z_score * std_dev
        upper_threshold = mean + z_score * std_dev
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    return lower_threshold, upper_threshold


