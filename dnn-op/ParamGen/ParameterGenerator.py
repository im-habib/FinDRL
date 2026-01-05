class ParameterGenerator:
    def __init__(self, indicator_list):
        self.indicator_list = indicator_list
        self.parameter_ranges = {
            'length': range(5, 31, 5),
            'timeperiod': range(5, 31, 5),
            'fast': [12],
            'slow': [26],
            'signal': range(5, 15, 5),
            'std': [1, 2],
            'offset': [0],
            'k': range(5, 15, 5),
            'd': range(3, 10, 3),
            'smooth_k': [3],
        }

    def generate_combinations(self):
        param_combinations = []
        for indicator_name in self.indicator_list:
            # Get the indicator function from pandas-ta
            try:
                indicator_func = getattr(ta, indicator_name)
            except AttributeError:
                print(f"Indicator '{indicator_name}' not found in pandas-ta. Skipping.")
                continue

            # Get parameters
            sig = inspect.signature(indicator_func)
            param_names = [
                p for p in sig.parameters.keys()
                if p not in ['open_', 'high', 'low', 'close', 'volume', 'kwargs']
            ]

            # Assign default ranges
            param_values = []
            for param in param_names:
                if param in self.parameter_ranges:
                    param_values.append(self.parameter_ranges[param])
                else:
                    param_values.append([None])

            # Generate combinations
            for combination in product(*param_values):
                params = dict(zip(param_names, combination))
                param_combinations.append({
                    'indicator': indicator_name,
                    'params': params
                })

        return param_combinations
