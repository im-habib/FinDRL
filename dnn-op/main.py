if __name__ == "__main__":
    # Define parameters
    ticker = 'AAPL'
    start_date = '2015-01-01'
    end_date = '2023-10-01'
    indicator_list = ['sma', 'rsi', 'macd', 'bbands']

    # Create optimizer instance
    optimizer = TradingStrategyOptimizer(
        ticker, start_date, end_date, indicator_list
    )

    # Run optimization
    optimizer.run()
