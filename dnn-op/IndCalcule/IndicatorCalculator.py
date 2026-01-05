class IndicatorCalculator:
    def __init__(self, data):
        self.data = data

    def compute_indicator(self, indicator_name, params):
        df = self.data.copy()
        indicator_func = getattr(ta, indicator_name)

        # Prepare function parameters
        func_params = {}
        sig = inspect.signature(indicator_func)
        for param in sig.parameters:
            if param in ['open_', 'high', 'low', 'close', 'volume', 'kwargs']:
                continue
            if params.get(param) is not None:
                func_params[param] = params[param]

        # Determine required inputs
        required_inputs = []
        for param in sig.parameters:
            if param == 'close':
                required_inputs.append(df['Close'])
            elif param == 'open_':
                required_inputs.append(df['Open'])
            elif param == 'high':
                required_inputs.append(df['High'])
            elif param == 'low':
                required_inputs.append(df['Low'])
            elif param == 'volume':
                required_inputs.append(df['Volume'])

        # Compute indicator
        try:
            indicator_result = indicator_func(*required_inputs, **func_params)
            if isinstance(indicator_result, pd.DataFrame):
                df = df.join(indicator_result)
            else:
                df[indicator_name.upper()] = indicator_result
            return df
        except Exception as e:
            print(f"Error computing {indicator_name} with params {func_params}: {e}")
            return None
