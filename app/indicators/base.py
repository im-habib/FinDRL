import inspect

class Indicator:
    def __init__(self, data, check_field="close"):
        self.data = data
        self.check_field = check_field
        # print("Indicator Initialized")

        # Dynamically generate the list of available indicators
        self.available_indicators = [
            name for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name not in ['__init__', 'get_indicator', 'call_indicator', 'list_indicators']
        ]

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
