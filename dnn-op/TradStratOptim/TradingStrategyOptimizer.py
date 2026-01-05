class TradingStrategyOptimizer:
    def __init__(self, ticker, start_date, end_date, indicator_list):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.indicator_list = indicator_list
        self.data = None
        self.parameter_combinations = None
        self.results = []
        self.X_columns = None
        self.encoder = None
        self.scaler = None
        self.model = None
        self.optimal_params = None
        self.optimal_indicator_name = None

    def run(self):
        # Step 1: Download Data
        downloader = DataDownloader(self.ticker, self.start_date, self.end_date)
        self.data = downloader.download_data()

        # Step 2: Generate Parameter Combinations
        param_generator = ParameterGenerator(self.indicator_list)
        self.parameter_combinations = param_generator.generate_combinations()

        # Step 3: Compute Indicators and Evaluate Performance
        for combination in self.parameter_combinations:
            indicator_name = combination['indicator']
            params = combination['params']

            indicator_calculator = IndicatorCalculator(self.data)
            df = indicator_calculator.compute_indicator(indicator_name, params)
            if df is None:
                continue

            signal_generator = SignalGenerator(df, indicator_name)
            df = signal_generator.generate_signals()
            if df is None:
                continue

            evaluator = PerformanceEvaluator(df)
            cumulative_return = evaluator.calculate_performance()

            # Flatten parameters for storage
            flat_params = {f'{indicator_name}_{k}': v for k, v in params.items()}
            result = {
                'Indicator': indicator_name,
                'Cumulative_Return': cumulative_return
            }
            result.update(flat_params)
            self.results.append(result)

        # Step 4: Prepare Dataset
        dataset_preparer = DatasetPreparer(self.results)
        X, y = dataset_preparer.prepare_dataset()
        self.X_columns = X.columns
        self.encoder = dataset_preparer.encoder

        X_train_scaled, X_test_scaled, y_train, y_test = dataset_preparer.split_and_scale()
        self.scaler = dataset_preparer.scaler

        # Step 5: Build and Train Neural Network
        self.model = NeuralNetworkModel(input_dim=X_train_scaled.shape[1])
        self.model.train(X_train_scaled, y_train, X_test_scaled, y_test)

        # Step 6: Optimize Parameters
        optimizer = ParameterOptimizer(
            self.model.model, self.scaler, self.encoder, self.X_columns
        )
        self.optimal_params = optimizer.find_optimal_parameters(self.parameter_combinations)
        self.optimal_indicator_name = self.encoder.inverse_transform(
            [int(self.optimal_params['Indicator'])]
        )[0]
        print("Optimal Indicator:", self.optimal_indicator_name)
        print("Optimal Parameters:")
        print(self.optimal_params)

        # Step 7: Backtest with Optimal Parameters
        backtester = Backtester(
            self.data, self.optimal_indicator_name, self.optimal_params, self.encoder
        )
        backtest_df = backtester.backtest_strategy()
        if backtest_df is not None:
            self.plot_backtest_results(backtest_df)
        else:
            print("Backtesting failed.")

    def plot_backtest_results(self, df):
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Cumulative_Strategy_Return'], label='Strategy Return')
        plt.plot(df.index, df['Cumulative_Market_Return'], label='Market Return')
        plt.legend()
        plt.xlabel('Date')
        plt.ylabel('Cumulative Return')
        plt.title(f'Backtest Results with Optimized {self.optimal_indicator_name.upper()}')
        plt.show()
