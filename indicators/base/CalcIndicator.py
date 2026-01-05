import pandas as pd

# 1. Define the common interface for all indicators
class Indicator:
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        raise NotImplementedError("Each indicator must implement the 'calculate' method")
