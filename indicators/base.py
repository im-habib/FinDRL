import inspect
from utils.Utils import standardize_columns

class Indicator:
    def __init__(self, data, check_field):
        self.temporarily_columns = {}
        self.check_field = check_field
        self.data = standardize_columns(data)
        # print("Indicator Initialized")

        # Dynamically generate the list of available indicators
        self.available_indicators = [
            name for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name not in ['__init__', 'get_indicator', 'call_indicator', 'list_indicators']
        ]

                # Remove duplicate indices, if any
        if self.data.index.duplicated().any():
            print("Duplicate indices found. Removing duplicates.")
            self.data = self.data[~self.data.index.duplicated(keep='first')]
        
        # Remove duplicate columns, if any
        if self.data.columns.duplicated().any():
            print("Duplicate columns found. Removing duplicates.")
            self.data = self.data.loc[:, ~self.data.columns.duplicated()]

    def get_indicator(self, indicator_name):
        indicator_method = getattr(self, indicator_name)
        if indicator_method:
            return indicator_method
        else:
            raise ValueError(f"Indicator {indicator_name} is not implemented")
    
    def call_indicator(self, indicator, **kwargs):
        if callable(indicator):
            return indicator(**kwargs)
        else:
            raise ValueError(f"Indicator {indicator} is not implemented")

    def list_indicators(self):
        return self.available_indicators
