from backtesting import Backtest
from app.parameters.Parameters import hoc_print
from app.strategies.Strategies import DynamicStrategy
from app.signal.Signal import create_buy_signal, create_sell_signal
from app.thresholds.Thresholds import calculate_thresholds, get_threshold_method

def run_backtest(ind_idx, data, indicator_name, indicator_values):

    # Get the threshold calculation method for the current indicator
    threshold_method = get_threshold_method(indicator_name)
    
    # Calculate thresholds dynamically based on method and parameters
    threshold_params = {
        'z_score': {'z_score': 1},
        'std_dev': {'num_std_dev': 1},
        'percentile': {'lower_percentile': 20, 'upper_percentile': 80},
    }.get(threshold_method, {})
    
    lower_threshold, upper_threshold = calculate_thresholds(indicator_values, method=threshold_method, **threshold_params)

    hoc_print(f"{lower_threshold}, {upper_threshold}", f"lower_threshold and upper_threshold for {indicator_name}")

    # Define buy and sell signals dynamically
    buy_signal = create_buy_signal(lower_threshold, 'below')
    sell_signal = create_sell_signal(upper_threshold, 'above')

    # Set the dynamic strategy parameters
    DynamicStrategy.buy_signal = buy_signal
    DynamicStrategy.sell_signal = sell_signal
    DynamicStrategy.indicator_name = indicator_name
    DynamicStrategy.indicator_values = indicator_values

    # Run backtest
    bt = Backtest(data, DynamicStrategy, cash=10000, commission=.002)
    
    stats = bt.run()
    # bt.plot()

    # Save results to text file
    # with open(f'{indicator_name}_results.txt', 'w') as f:
    #     f.write(str(stats))
    hoc_print(stats, f'Result ( {ind_idx} )')

# Usage
# ticker = 'AAPL'
# start_date = '2020-01-01'
# end_date = '2023-01-01'

# # Define indicators and conditions
# indicators = [
#     {
#         'name': 'RSI',
#         'indicator_func': lambda data: RSIIndicator(window=14).compute(data),
#         'condition': BuyAndSellCondition(
#             buy_logic=lambda rsi: rsi[-1] < 30,
#             sell_logic=lambda rsi: rsi[-1] > 70
#         )
#     },
#     {
#         'name': 'SMA',
#         'indicator_func': lambda data: SMAIndicator(short_window=50, long_window=200).compute(data),
#         'condition': BuyAndSellCondition(
#             buy_logic=lambda sma: sma[0][-1] > sma[1][-1] and sma[0][-2] <= sma[1][-2],
#             sell_logic=lambda sma: sma[0][-1] < sma[1][-1] and sma[0][-2] >= sma[1][-2]
#         )
#     },
#     {
#         'name': 'MACD',
#         'indicator_func': lambda data: MACDIndicator(fast=12, slow=26, signal=9).compute(data),
#         'condition': BuyAndSellCondition(
#             buy_logic=lambda macd: macd[0][-1] > macd[1][-1],
#             sell_logic=lambda macd: macd[0][-1] < macd[1][-1]
#         )
#     }
# ]

# # Run backtests for each indicator
# for indicator in indicators:
#     run_backtest(
#         ticker=ticker,
#         start_date=start_date,
#         end_date=end_date,
#         indicator_func=indicator['indicator_func'],
#         condition=indicator['condition'],
#         indicator_name=indicator['name']
#     )
