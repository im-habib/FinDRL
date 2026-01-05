import os
import click
import pandas as pd
from data import DataLoder
from utils.Utils import is_csv_file
from fetcher import YahooDataFetcher
from tickers.Tickers import DOW_30_TICKER
from app.backtest.Backtest import run_backtest
from indicators.Trend import TrendIndicators
from indicators.Momentum import MomentumIndicators
from utils import total_months_month_array, combine_csv_files_data, convert_to_minutes
from app.parameters.Parameters import analyze_function, generate_random_parameters, extract_parameters, extract_list_to_key_value, hoc_print

# from backtesting.test import GOOG
# from fetcher import DataAggregator
# from test.Backtest import test_run
# from backtest.RunTest import do_backtesting

# Define the main CLI group
@click.group()
def main():
    """FinDRL - A CLI app to fetch financial data"""
    pass

# Yahoo data fetch commands
@click.group()
def data_fetch():
    """Fetch data from Yahoo Finance"""
    pass

# Yahoo data fetch commands
@click.group()
def analysis():
    """Local parameters create and analyze..."""
    pass

@data_fetch.command()
@click.option('--country', default='cn', prompt='Available countries are [usa, cn, bd]', help='The providing countries data will fetching.')
@click.option('--interval', default='1h', help='Comma-separated list of interval (default: 1m, 30m,1h)')
def yahoo(country, interval):
    # Create an instance of the StockDataDownloader
    downloader = YahooDataFetcher(country, tickers=DOW_30_TICKER, interval=interval)

    # Download the stock data
    downloader.download_data()

    data = downloader.get_data()

    # print(data.head(10))

    downloader.processing(data)

# @click.option('--start_date', prompt='Start Date (YYYY-MM-DD)', help='The start date for fetching data.')
# @click.option('--end_date', prompt='End Date (YYYY-MM-DD)', help='The end date for fetching data.')
# data_fetcher = YahooDataFetcher(symbol, start_date, end_date)
# data_fetcher.fetch_data(period, interval)
# start_date = None  # If None, it will download max available data or adjust based on the interval
# end_date = None  # If None, it will download up to the latest available data
# interval = '1h'  # Can change to '1d', '1wk', '1mo', etc.
# tickers = ['600519.SS', '601318.SS', '000002.SZ', '0700.HK']


# @data_fetch.command()
# @click.option('--symbol', prompt='Stock Symbol', help='The stock symbol to fetch data for.')
# @click.option('--start_date', prompt='Start Date (YYYY-MM-dd)', help='The start date for fetching data.')
# @click.option('--end_date', prompt='End Date (YYYY-MM-dd)', help='The end date for fetching data.')
# def polygon(symbol, start_date, end_date):
#     provider = "POLYGON"
#     API_KEY = os.getenv('POLYGON_API_KEY')
#     intervals_timespans = [{'interval': 1, 'timespan': 'minute'}]
#     _, month_array = total_months_month_array(start_date, end_date)
#     aggregator = DataAggregator(api_key=API_KEY, symbol=symbol, month_array=month_array, provider=provider)
#     aggregator.run(intervals_timespans=intervals_timespans)

# Analysis commands
@click.group()
def data_analysis():
    """Analyze financial data"""
    pass

# @data_analysis.command()
# @click.option('--data_directory', prompt='data directory', help='data directory, e.g., ./data/POLYGON/minute')
# def analysis(symbol, date, data_directory):
#     print(f"symbol: {symbol}, date: {date}, data_directory: {data_directory}")
#     output_file=f"./data/{symbol}"
#     if not os.path.exists(output_file):
#         os.mkdir(output_file)
#     if not os.path.exists(data_directory) or not os.path.exists(output_file):
#         print("Something wrong!")
#         exit(0)
#     combine_csv_files_data(input_directory=data_directory, output_file=f"{output_file}/{date}.csv")

# Backtest commands
@click.group()
def backtest():
    """Run backtesting on financial data"""
    pass

# @backtest.command()
# @click.option('--file_number', default=0, help='Which number of file to use for backtesting')
# @click.option('--data_directory', prompt='data directory', help='data directory, e.g., ./data/SPY')
# @click.option('--interval', default="15min", help='Intervals for split the data (eg., 1min, 15min, 1h, 1d)')
# def run(data_directory, file_number, interval):

#     data = None

#     if not os.path.exists(data_directory):
#         print("Something wrong!")
#         exit(0)

#     try:
#         interval_minutes = convert_to_minutes(interval)
#     except ValueError as e:
#         print(f"Error: {e}")
#         exit(0)

#     if interval_minutes <= 30:
#         resampler = DataResampler(data_directory, file_number)
#         file_path = resampler.process(interval)
#         data = pd.read_csv(file_path)
#     else:
#         # Load data
#         loader = DataLoder(data_directory, file_number)
#         data = loader.load()

#     print("Run Backtest....")
#     print(data.head(5))

    # do_test = do_backtesting(data=data)
    # print(do_test)


@analysis.command()
@click.option('--country', prompt='which countries data do you want to analysis.', help='Available countries: [cn, usa, bd, uk]')
@click.option('--filename', prompt='which filename do you wan to use', help='data directory, e.g., ./data/')
def peramiters(country, filename):
    data_dir = f'./data/{country}'
    if not os.path.exists(data_dir):
        print("Data folder not exisr, something wrong!")
        exit(0)

    filename=f'{data_dir}/{filename}'
    if not is_csv_file(filename):
        print("Data file not exisr, something wrong!")
        exit(0)

    # Load data
    loader = DataLoder(filename)

    data = loader.load()

    new_values = []
    new_parameters = []

    # trend = TrendIndicators(data, "close")
    momentum = MomentumIndicators(data, "Close")

    # trend_indicators = trend.list_indicators()

    momentum_indicators = momentum.list_indicators()

    # hoc_print(trend_indicators, "Available Trend Indicators")
    hoc_print(momentum_indicators, "Available Momentum Indicators")

    for indicator_name in momentum_indicators:
        ind = momentum.get_indicator(indicator_name)
        # print(f'is callable: {callable(ind)}')
        # Analyze the function to get base parameter values
        base_values = analyze_function(ind)
        # print(f'{idx}: base_values: {base_values}')

        # Generate 200 day moving avarage sets of random parameters
        parameters = generate_random_parameters(base_values, min_value=1, max_value=201)

        # print(f'{idx}: parameters: {parameters}')

        new_parameters.append({indicator_name: parameters})

    # print(f"parameters: {new_parameters}")
    # hoc_print(len(new_parameters), "Total parameters")
    # hoc_print(new_parameters, "Parameters")

    # for ind_name in indicators:

    params = extract_parameters(new_parameters)

    # hoc_print(params, reasone='params')

    # Usage
    for name, parameters in params.items():
        # Define indicators and conditions
        indc_func = momentum.get_indicator(name)

        for idx, parameter in enumerate(list(parameters)):
            momentum.call_indicator(indc_func, **parameter)
            # temporarily_columns[f"{name}_{parameter}"] = data_back
            # hoc_print(data_back, reasone=f'Data with new feature)')

    # Concatenate all indicators columns with the original data in one step
    # temporarily_columns = momentum.temporarily_columns  # Dictionary to hold calculations temporarily

    # print(temporarily_columns)

    # new_df = pd.DataFrame(temporarily_columns, index=data.index)
    # new_data = pd.concat([data, new_df], axis=1)
    # new_filename=f"/data/{country}/new_data_features.csv"
    # new_data.to_csv(new_filename)

    # hoc_print(data, "after indicator calculation this is pd new data frame")



    # for name, parameters in list(params.items())[5:]:
        # print(f'is callable: {callable(indc)}')
        # hoc_print(f"For this Indicator total number of paramiters: {len(parameters)}", reasone=f'Indicator ( {name} )')

        # print('list(parameters.items())', list(parameters)[:5])

            # hoc_print(parameter, reasone=f'Parameter ( {idx} )')
            # new_values.append({ f'{name}_{parameter}': call_ind_value })

            # hoc_print(call_ind_value, reasone=f'Paramiters: ( {parameter} ), ( {name} ): indicator.')

            # run_backtest(idx, data, name, call_ind_value)

        
    # hoc_print(new_values, f'Calculated indictors values & total len: {len(new_values)}')

    #     for  idc_kwargs in params:

    #         print(f'{idc_kwargs}')
    #         signal = momentum.call_indicator(indc, idc_kwargs)

            # print(f'signal: {signal}')
            # Override params with kwargs
            # for key, value in idc_kwargs.items():

                # new_param=key, value

                # # setattr(new_param, key, value)

                # print(f"new_param: {new_param}")


        # for id, params in enumerate(new_parameters):
        #     # print("params", params)
        #     sig_param = params.get(ind_name, [])
        #     print(f"sig_param: {sig_param}")
        #     # for p in :


        # indc = momentum.call_indicator(indc, )
        # pass

# @backtest.command()
# @click.option('--data_directory', prompt='data directory', help='data directory, e.g., ./data/SPY')
# @click.option('--file_number', default=0, help='Which number of file to use for backtesting')
# @click.option('--interval', default="15min", help='Intervals for split the data (eg., 1min, 15min, 1h, 1d)')
# def run(data_directory, file_number, interval):

#     data = None

#     if not os.path.exists(data_directory):
#         print("Something wrong!")
#         exit(0)

#     try:
#         interval_minutes = convert_to_minutes(interval)
#     except ValueError as e:
#         print(f"Error: {e}")
#         exit(0)

#     if interval_minutes <= 30:
#         resampler = DataResampler(data_directory, file_number)
#         file_path = resampler.process(interval)
#         data = pd.read_csv(file_path)
#     else:
#         # Load data
#         loader = DataLoder(data_directory, file_number)
#         data = loader.load()

#     print("Run Backtest....")
#     print(data.head(5))

#     do_test = do_backtesting(data=GOOG)

#     print(do_test)
    

# files = [os.path.join(data_directory, f) for f in os.listdir(data_directory) if f.endswith('.csv')]
# if len(files) == 0:
#     raise FileNotFoundError(f"No CSV files found in the directory: {data_directory}")
# if file_number > len(files):
#     raise ValueError(f"Requested number of files ({file_number}) is greater than available files ({len(files)})")

# data['timestamp'] = pd.to_datetime(data['timestamp'])
# data.set_index('timestamp', inplace=True)

    # if interval <= "30min":
    #     file_path = resalmple_data.process(interval)
    # else:
    #     file_path= resalmple_data.find_csv_file(data_directory, file_number)

# @backtest.command()
# @click.option('--data_directory', prompt='data directory', help='data directory, e.g., ./data/SPY')
# @click.option('--file_number', default=0, help='Which number of file to use for backtesting')
# def test(data_directory, file_number):
#     loader = DataLoder(data_directory, file_number)
#     data = loader.load()
#     test_run(data)

# Add all command groups to the main CLI group
# main.add_command(polygon_data_fetch)
main.add_command(data_fetch)
main.add_command(analysis)
# main.add_command(backtest)
# main.add_command(test)

if __name__ == '__main__':
    main()


# @click.group()
# def main():
#     """FinDRL - A CLI app to fetch financial data"""
#     pass

# @click.group()
# def yahoo_data_fetch():
#     pass

# @click.group()
# def polygon_data_fetch():
#     pass

# @click.group()
# def analysis():
#     pass

# @click.group()
# def backtest():
#     pass

# @yahoo_data_fetch.command()
# @click.option('--symbol', prompt='Stock Symbol', help='The stock symbol to fetch data for.')
# @click.option('--start_date', prompt='Start Date (YYYY-MM-DD)', help='The start date for fetching data.')
# @click.option('--end_date', prompt='End Date (YYYY-MM-DD)', help='The end date for fetching data.')
# @click.option('--intervals', default='1m,15m,30m,1h', help='Comma-separated list of intervals (default: 1m,15m,30m,1h)')
# def yahoo_fetch(symbol, start_date, end_date, intervals):
#     intervals = intervals.split(',')
#     data_fetcher = DataFetcher(symbol, start_date, end_date, intervals)
#     data_fetcher.fetch_data()

# @polygon_data_fetch.command()
# @click.option('--symbol', prompt='Stock Symbol', help='The stock symbol to fetch data for.')
# @click.option('--start_date', prompt='Start Date (YYYY-MM-dd)', help='The start date for fetching data.')
# @click.option('--end_date', prompt='End Date (YYYY-MM-dd)', help='The end date for fetching data.')
# def fetch_polygon(symbol, start_date, end_date):
#     # intervals = intervals.split(',')
#     provider = "POLYGON"
#     API_KEY = os.getenv('POLYGON_API_KEY')
#     intervals_timespans = [{'interval': 1, 'timespan': 'minute'}]
#     _, month_array = total_months_month_array(start_date, end_date)
    
#     aggregator = DataAggregator(api_key=API_KEY, symbol=symbol, month_array=month_array, provider=provider)
#     aggregator.run(intervals_timespans=intervals_timespans)

# @analysis.command()
# # @click.option('--symbol', prompt='Stock Symbol', help='The stock symbol which you are working for.')
# # @click.option('--date', prompt='Date (YYYY-MM-dd-YYYY-MM-dd)', help='The date for create data analysing path.')
# @click.option('--data_directory', prompt='data directory', help='data directory, e.g., ./data/POLYGON/minute')
# def data_analysis(symbol, date, data_directory):
#     print(f"symbol: {symbol}, date: {date}, data_directory: {data_directory}")
#     output_file=f"./data/{symbol}"
    

#     if not os.path.exists(output_file):
#         os.mkdir(output_file)

#     if not os.path.exists(data_directory) or not os.path.exists(output_file):
#         print("Something wrong!")
#         exit(0)
    
#     combine_csv_files_data(input_directory=data_directory, output_file=f"{output_file}/{date}.csv")


# # cli.add_command(fetch)
# # cli.add_command(fetch_polygon)
# # cli.add_command(data_analysis)

# # @data_analysis.command()
# # def analyze():
# #     analysis = DataAnalysis()
# #     analysis.run_analysis()

# @backtest.command()
# @click.option('--data_directory', prompt='data directory', help='data directory, e.g., ./data/SPY')
# @click.option('--file_number', default=0, help='Number of file to use for backtesting')
# def run_backtest(data_directory, file_number):
#     files = [os.path.join(data_directory, f) for f in os.listdir(data_directory) if f.endswith('.csv')]
#     if len(files) == 0:
#         raise FileNotFoundError(f"No CSV files found in the directory: {data_directory}")
#     if file_number > len(files):
#         raise ValueError(f"Requested number of files ({file_number}) is greater than available files ({len(files)})")
    
#     data = pd.read_csv(files[file_number])
#     data['timestamp'] = pd.to_datetime(data['timestamp'])
#     data.set_index('timestamp', inplace=True)
#     # data = data.rename(columns={
#     #     'volume': 'Volume',
#     #     'open': 'Open',
#     #     'close': 'Close',
#     #     'high': 'High',
#     #     'low': 'Low'
#     # })
#     do_test = do_backtesting(data=data)

#     print(do_test)

# if __name__ == '__main__':
#     backtest()
#     analysis()
#     yahoo_data_fetch()
#     polygon_data_fetch()


# import os
# import requests
# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# # Load environment variables from .env file
# load_dotenv()

# # 
# Fetch historical data from Alpha Vantage
# def fetch_historical_data(symbol, api_key, interval):
#     url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}&outputsize=full'
#     response = requests.get(url)
#     data = response.json()

#     if f'Time Series ({interval})' not in data:
#         raise Exception("Error fetching data from Alpha Vantage")

#     timeseries = data[f'Time Series ({interval})']
#     df = pd.DataFrame.from_dict(timeseries, orient='index')
#     df.columns = ['open', 'high', 'low', 'close', 'volume']
#     df.index = pd.to_datetime(df.index)
#     df = df.sort_index()

#     return df

# # Fetch tick data from Polygon.io
# def fetch_tick_data(symbol, api_key, date):
#     url = f'https://api.polygon.io/v1/historic/quotes/{symbol}/{date}?apiKey={api_key}'
#     response = requests.get(url)
#     data = response.json()

#     if 'ticks' not in data:
#         raise Exception("Error fetching data from Polygon.io")

#     ticks = data['ticks']
#     df = pd.DataFrame(ticks)
#     df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
#     df = df.set_index('timestamp')

#     return df


# # QuantConnect API credentials
# user_id = os.getenv('LEAN_CLI_USER_ID')
# api_key = os.getenv('LEAN_CLI_API_KEY')

# # Initialize QuantConnect API
# api = Api(user_id, api_key)

# def fetch_tick_data(symbol, start_date, end_date):
#     all_data = []
#     start_date = datetime.strptime(start_date, '%Y-%m-%d')
#     end_date = datetime.strptime(end_date, '%Y-%m-%d')

#     while start_date <= end_date:
#         current_date = start_date.strftime('%Y-%m-%d')
#         print(f"Fetching tick data for {symbol} on {current_date}...")

#         data = api.get_ticks(symbol, current_date)
#         if data:
#             all_data.extend(data)
        
#         start_date += timedelta(days=1)

#     return pd.DataFrame(all_data)

# # Example usage
# symbol = 'AAPL'
# start_date = '2023-01-01'
# end_date = '2023-01-31'
# tick_data = fetch_tick_data(symbol, start_date, end_date)
# tick_data.to_csv(f"{symbol}_tick_data_{start_date}_to_{end_date}.csv", index=False)
# # 4. Run the Script Using LEAN CLI
# # Use the LEAN CLI to run the script:

# # sh
# # Copy code
# # lean research fetch_tick_data.py
# # Notes
# # The example assumes you have access to tick data through QuantConnect.
# # The api.get_ticks method is a placeholder and should be replaced with the actual method provided by QuantConnect for fetching tick data.
# # The data retrieval and handling should be adjusted based on the actual API responses and requirements.
# # This approach integrates QuantConnect's API with a Python script to fetch tick data and store it in a CSV file, ensuring you have access to high-resolution market data for analysis and verification.




