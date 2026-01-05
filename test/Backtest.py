import pandas as pd

if __name__ == '__main__':
    excluded_columns = ['date', 'open', 'high', 'low', 'close', 'adj close', 'volume', 'ticker']
    # backtester = IndicatorBacktester(mom_new_data, excluded_columns=excluded_columns)
    # backtester.prepare_data()

    # # Backtest all indicators with thresholds
    # results = backtester.backtest_all_indicators_with_thresholds(low_range=0, high_range=100, step=10)




# # Load your historical stock data
# from app.DynamicBacktest.Backtest import Backtest


# data = pd.read_csv('./data/cn/combined_output.csv')

# print(data.head(10))

# # # Initialize the backtesting class
# backtest = Backtest(data)

# # Add RSI indicator with a custom period
# backtest.add_indicator('rsi', length=14)

# # Generate buy/sell signals for RSI (e.g., buy below 30, sell above 70)
# backtest.generate_signals('RSI_14', buy_condition=lambda x: x < 30, sell_condition=lambda x: x > 70)

# # Run the backtest and plot the results
# results = backtest.backtest()
# backtest.plot_results()

# import pandas as pd
# from backtesting import Backtest, Strategy

# class MomentumSRMStrategy(Strategy):
#     def init(self):
#         self.stoch_k = self.data.stoch_k
#         self.stoch_d = self.data.stoch_d
#         self.rsi = self.data.rsi
#         self.macd = self.data.macd
#         self.macd_signal = self.data.macd_signal

#     def next(self):
#         # Define buy signal conditions
#         stoch_oversold = self.stoch_k[-1] < 20 and self.stoch_d[-1] < 20
#         rsi_uptrend = self.rsi[-1] > 50
#         macd_bullish = self.macd[-1] > self.macd_signal[-1]
#         stoch_not_overbought = self.stoch_k[-1] < 80 and self.stoch_d[-1] < 80

#         if stoch_oversold and rsi_uptrend and macd_bullish and stoch_not_overbought:
#             self.buy()

# # Example usage
# def run_backtest(data):
#     bt = Backtest(data, MomentumSRMStrategy, cash=10000, commission=.002)
#     stats = bt.run()
#     bt.plot()
#     return stats


# def test_run(data):
#     # Assuming you have your data in a DataFrame named `data`
#     # data = pd.read_csv(data_path, parse_dates=True, index_col='Date')
#     # Calculate indicators
#     data['stoch_k'] = ta.momentum.stoch(data['High'], data['Low'], data['Close'], window=14, smooth_window=3)
#     data['stoch_d'] = ta.momentum.stoch_signal(data['High'], data['Low'], data['Close'], window=14, smooth_window=3)
#     data['rsi'] = ta.momentum.rsi(data['Close'], window=14)
#     macd = ta.trend.MACD(data['Close'], window_slow=26, window_fast=12, window_sign=9)
#     data['macd'] = macd.macd()
#     data['macd_signal'] = macd.macd_signal()

#     # Run the backtest
#     stats = run_backtest(data)
#     print(stats)
