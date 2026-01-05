class Backtester:
    def __init__(self, data, indicator_name, params, encoder):
        self.data = data
        self.indicator_name = indicator_name
        self.params = params
        self.encoder = encoder

    def backtest_strategy(self):
        df = self.data.copy()
        indicator_func = getattr(ta, self.indicator_name)

        # Prepare function parameters
        func_params = {}
        sig = inspect.signature(indicator_func)
        for param in sig.parameters:
            if param in ['open_', 'high', 'low', 'close', 'volume', 'kwargs']:
                continue
            key = f'{self.indicator_name}_{param}'
            if key in self.params and self.params[key] is not None:
                func_params[param] = int(self.params[key])

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
        indicator_result = indicator_func(*required_inputs, **func_params)
        if isinstance(indicator_result, pd.DataFrame):
            df = df.join(indicator_result)
        else:
            df[self.indicator_name.upper()] = indicator_result

        # Generate signals
        signal_generator = SignalGenerator(df, self.indicator_name)
        df = signal_generator.generate_signals()
        if df is None:
            return None

        # Calculate performance
        df['Return'] = df['Close'].pct_change()
        df['Strategy_Return'] = df['Return'] * df['Signal'].shift(1)
        df['Cumulative_Strategy_Return'] = (1 + df['Strategy_Return']).cumprod()
        df['Cumulative_Market_Return'] = (1 + df['Return']).cumprod()
        return df
