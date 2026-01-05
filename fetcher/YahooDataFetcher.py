import os
import warnings
import pandas as pd
import yfinance as yf
from utils.Utils import is_csv_file
from datetime import datetime, timedelta
# from tickers import DOW_30_TICKER, SSE_50_TICKER, CSI_300_TICKER, SDAX_50_TICKER

warnings.filterwarnings("ignore", category=FutureWarning)

class YahooDataFetcher:
    def __init__(self, country='bd', tickers='', start=None, end=None, interval='1d'):
        """
        Initialize the downloader with stock tickers, start date, end date, and interval.
        """
        if isinstance(tickers, str):
            self.tickers = [tickers]  # Convert single ticker to a list
        else:
            self.tickers = tickers

        self.end = end
        self.start = start
        self.country = country
        self.interval = interval
        self.data = pd.DataFrame()
        self.dir_name = f"./data/{country}"
        
        # Validate the interval
        self.validate_interval()
        # Calculate maximum available start time based on the interval
        self.calculate_max_available_start()
        self.delete_all_files(self.dir_name)
        
    def delete_all_files(self, folder_path):
        """
        Deletes all files in the specified folder.

        Parameters:
            folder_path (str): The path to the folder from which files should be deleted.
        """
        try:
            if os.path.exists(folder_path):
                # Iterate over all files in the folder
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    # Check if it's a file and delete it
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                print("All files have been deleted.")
            else:
                print(f"The folder {folder_path} does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def validate_interval(self):
        """Validates the interval to ensure it is supported by yfinance."""
        available_intervals = ['1m', '2m', '5m', '15m', '30m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        if self.interval not in available_intervals:
            raise ValueError(f"Invalid interval '{self.interval}'. Valid intervals are {available_intervals}.")

    def calculate_max_available_start(self):
        """Calculates the maximum available start date based on the provided interval."""
        if self.start is None or self.end is None:
            self.end = datetime.now()  - timedelta(days=1)# Default to current day - 1
            # Time ranges based on interval
            if self.interval in ['1m', '2m', '5m', '15m', '30m']:
                self.start = self.end - timedelta(days=30)  # Last 30 days for minute-level data
            elif self.interval == '1h':
                self.start = self.end - timedelta(days=60)  # Last 60 days for hourly data
            elif self.interval == '1d':
                self.start = self.end - timedelta(days=5 * 365)  # Last 5 years for daily data
            elif self.interval == '1wk':
                self.start = self.end - timedelta(days=10 * 365)  # Last 10 years for weekly data
            elif self.interval in ['1mo', '3mo']:
                self.start = self.end - timedelta(days=20 * 365)  # Last 20 years for monthly data
            else:
                raise ValueError(f"Unsupported interval '{self.interval}'")

    def download_data(self):
        """
        Download stock data based on the provided tickers, start date, end date, and interval.
        Replaces the existing data in `self.data` after every call.
        """
        # Reset self.data to ensure old data is cleared
        self.data = pd.DataFrame()

        # Validate the interval
        self.validate_interval()

        # Calculate maximum available start time based on the interval
        self.calculate_max_available_start()

        # Download data for each ticker and combine it into a single DataFrame
        for ticker in self.tickers:
            print(f"Downloading data for {ticker}...")

            tk = ticker

            data = yf.download(ticker, start=self.start, end=self.end, interval=self.interval, keepna=False, multi_level_index=False, )

            # Check if the initial download returned any data
            if data.empty:
                print(f"No data available for {ticker}. Trying with ^{tk}...")
                tk = f"^{ticker}"  # Modify the ticker with ^ if initial download fails
                data = yf.download(tk, start=self.start, end=self.end, interval=self.interval, keepna=False)

            # Handle case when no data is available
            if data.empty:
                print(f"No data available for the ticker '{ticker}' within the specified time frame.")
                continue

            # Ensure the index is named 'Datetime' if it's a date
            if isinstance(data.index, pd.DatetimeIndex):
                data.index.name = 'Datetime'
                data = data.reset_index()

            # Flatten the multi-level columns
            if isinstance(data.columns, pd.MultiIndex):
                print(data.columns.get_level_values(0))
                data.columns = data.columns.get_level_values(0)
            # Check if the required columns exist in the data after flattening
            required_columns = ['Date', 'open', 'high', 'low', 'close', 'volume']
            filtered_data = data[required_columns]
            missing_columns = [col for col in required_columns if col not in filtered_data]

            if missing_columns:
                print(f"Skipping {ticker}: Missing columns {missing_columns}")
                continue

            # # Filter to keep only the required columns
            # filtered_data = self.data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]

            # # Reset the index so that the dates don't conflict across different tickers
            # filtered_data = filtered_data.reset_index()

            # Add ticker as a column to distinguish which data belongs to which ticker
            filtered_data['ticker'] = ticker
            
            # Append the downloaded data to the main DataFrame
            # self.data = pd.concat([self.data, data], ignore_index=True)

            if filtered_data.empty:
                raise ValueError(f"No data available for the provided tickers within the specified time frame.")
            # Convert column names to lowercase for consistency
            # filtered_data.columns = [col.lower() for col in filtered_data.columns]
            # Concatenate the filtered data to the main DataFrame
            # self.data = pd.concat([self.data, filtered_data], ignore_index=True)

            # Convert the "Datetime" column to datetime format
            # filtered_data['Datetime'] = pd.to_datetime(filtered_data['Datetime'], errors='coerce')

            # Set "Datetime" as the index and sort the DataFrame by the index
            # filtered_data = filtered_data.set_index('Datetime').sort_index()
            filtered_data = filtered_data.reset_index()  # Reset any existing index if needed
            filtered_data = filtered_data.set_index("date").sort_index()  # Set 'Datetime' as the index
            self.save_data(filtered_data, ticker)

        print("All tickers Download complete.")
        # return self.get_data()

    def save_data(self, data: pd.DataFrame, ticker=''):
        """
        Saves the downloaded data to a CSV file.
        """
        if data.empty:
            raise ValueError("No data available to save. Please download the data first.")
        
        # Set the directory path for saving the file
        # directory = f'./data/{self.country}'
        # self.dir_name = directory
        # Create the directory if it doesn't exist
        if not os.path.exists(self.dir_name):
            os.makedirs(self.dir_name)

        # Extract only the year, month, and day for the start and end dates
        end_str = self.end.strftime('%Y-%m-%d') if self.end else 'unknown_end'
        start_str = self.start.strftime('%Y-%m-%d') if self.start else 'unknown_start'

        # Format the filename with year, month, and day, and the interval
        filename = f"{self.dir_name}/{ticker}_{start_str}_{end_str}_{self.interval}.csv"

        # Save the combined data back to the file
        data.to_csv(filename)
        print(f"Data successfully saved to {filename}")

    def get_data(self):
        """Returns the downloaded stock data."""
        # Calculate maximum available start time based on the interval
        # self.calculate_max_available_start()
       # Extract only the year, month, and day for the start and end dates
        # end_str = self.end.strftime('%Y-%m-%d') if self.end else 'unknown_end'
        # start_str = self.start.strftime('%Y-%m-%d') if self.start else 'unknown_start'
        combined_data = []

        # directory = f'./data/{self.country}'
        combined_data_file = f'{self.dir_name}/combined_output.csv'
        
        if os.path.exists(combined_data_file):
            print(f"Combined_data_file already exist: {combined_data_file}")
            os.remove(combined_data_file)
        
        if os.path.exists(f"{self.dir_name}/processed.csv"):
            print(f"processed data file already exist: {self.dir_name}/processed.csv")
            os.remove(f"{self.dir_name}/processed.csv")

        # Create the directory if it doesn't exist
        if os.path.exists(self.dir_name):
            # os.makedirs(directory)
            files = [f for f in os.listdir(self.dir_name) if os.path.isfile(os.path.join(self.dir_name, f))]
            # print("Files", files)
            for idx, file in enumerate(files):

                # Format the filename with year, month, and day, and the interval
                filename = f"{self.dir_name}/{file}"

                if(is_csv_file(filename)):
                    # print(f"{idx}: Reading data for filename: {filename}...")
                    data=pd.read_csv(filename)
                    if data.empty:
                        raise ValueError("No data downloaded yet. Please call download_data() first.")           
                    # print(data.head(5))
                    combined_data.append(data)
                else:
                    # print(f"{idx}: Reading data for filename: {filename}...")
                    print(f"This file {filename} not support...")
            # Concatenate all DataFrames in the list into a single DataFrame
            combined_df = pd.concat(combined_data,  axis=0, join="inner")
            # Ensure preprocessed_df is not None and save to CSV
            if combined_df is not None:
                # Save the combined DataFrame to a new CSV file
                combined_df.to_csv(combined_data_file)
            # combined_df.to_csv(processed_data, index=False)
            print(f"All CSV files have been combined into {combined_data_file}")
            # Preprocessing
            # data = pd.read_csv(combined_data_file)
            return combined_df

    
# Usage Example
# if __name__ == "__main__":
#     # Initialize the downloader object with multiple tickers
#     # tickers = DOW_30_TICKER  # Example tickers: Apple, Google, Microsoft
#     start_date = None  # If None, it will download max available data or adjust based on the interval
#     end_date = None  # If None, it will download up to the latest available data
#     interval = '1h'  # Can change to '1d', '1wk', '1mo', etc.
#     # tickers = ['600519.SS', '601318.SS', '000002.SZ', '0700.HK']
#     # Create an instance of the StockDataDownloader
#     downloader = YahooDataFetcher(country='usa', tickers=DOW_30_TICKER, start=start_date, end=end_date, interval=interval)

#     # Download the stock data
#     downloader.download_data()

#     data = downloader.get_data()

#     # print(data.head(10))

#     df = downloader.processing(data)

    # def processing(self, data: pd.DataFrame):
    #     process = DataPreProcessing(data)
    #     # processed_data = process.preprocess()

    #     # processed = f"{self.dir_name}/processed.csv"

    #     # processed_data.to_csv(processed)
    #     # print(f"Data pre processing done :)")

    #     # df = pd.read_csv(processed)
        
    #     # if not df.empty:
    #     #     return df, process
    #     # calculated = process.calculate_indicators(processed_data)
    #     return process
    

    # Save the combined data to a CSV file
    # downloader.save_to_csv()

    # Print the last few rows of the data
    # print(downloader.get_data().tail())


    # def __init__(self, tickers, start=None, end=None, interval='1d'):
    #     """
    #     Initialize the downloader with stock tickers, start date, end date, and interval.
    #     If no start or end is provided, it will dynamically calculate the maximum available data 
    #     depending on the interval.
    #     :param tickers: Stock ticker(s) symbol, can be a string (e.g., 'AAPL') or a list of tickers (e.g., ['AAPL', 'GOOGL'])
    #     :param start: Start date for downloading the data (optional)
    #     :param end: End date for downloading the data (optional)
    #     :param interval: Data interval (e.g., '1d', '1wk', '1mo')
    #     """
    #     if isinstance(tickers, str):
    #         self.tickers = [tickers]  # Convert single ticker to a list
    #     else:
    #         self.tickers = tickers
        
    #     self.end = end
    #     self.start = start
    #     self.interval = interval
    #     self.data = pd.DataFrame()
    #     self.available_intervals = [
    #         '1m',  # 1 minute
    #         '2m',  # 2 minutes
    #         '5m',  # 5 minutes
    #         '15m', # 15 minutes
    #         '30m', # 30 minutes
    #         '60m', # 1 hour
    #         '90m', # 90 minutes
    #         '1h',  # 1 hour
    #         '1d',  # 1 day
    #         '5d',  # 5 days
    #         '1wk', # 1 week
    #         '1mo', # 1 month
    #         '3mo'  # 3 months
    #     ]

        
        # """
        # Download stock data based on the provided tickers, append it to the same column structure, and save to CSV.
        # The resulting CSV file will have a clean structure with no repeated columns.
        # """
        # # Ensure the directory exists
        # directory = os.path.dirname(save_path)
        # if not os.path.exists(directory):
        #     os.makedirs(directory)

        # # Validate the interval
        # self.validate_interval()

        # # Calculate maximum available start time based on the interval
        # self.calculate_max_available_start()

        # # If the file already exists, load it and continue appending new data
        # if os.path.exists(save_path):
        #     combined_data = pd.read_csv(save_path, index_col=0, parse_dates=True)
        # else:
        #     combined_data = pd.DataFrame()

        # # Download data for each ticker and append to the existing DataFrame
        # for ticker in self.tickers:
        #     print(f"Downloading data for {ticker}...")
        #     data = yf.download(ticker, start=self.start, end=self.end, interval=self.interval)

        #     # Handle case when no data is available
        #     if data.empty:
        #         print(f"No data available for the ticker '{ticker}' within the specified time frame.")
        #         continue

        #     # Add 'ticker' column to distinguish which data belongs to which ticker
        #     # data['ticker'] = ticker

        #     # Reset index to avoid duplicate date indexes
        #     data = data.reset_index()

        #     # Concatenate the downloaded data to the combined DataFrame (row-wise)
        #     combined_data = pd.concat([combined_data, data], ignore_index=True)

        #     # Save after every ticker
        #     combined_data.to_csv(save_path)
        #     print(f"Data for {ticker} appended and saved to {save_path}")
        # Check if the file already exists
        # if os.path.exists(filename):
        #     # Load existing data from the file
        #     existing_data = pd.read_csv(filename, index_col=0, parse_dates=True)
        #     # Concatenate the new data with the existing data
        #     combined_data = pd.concat([existing_data, self.data])
        #     # Remove any duplicate rows (based on index)
        #     combined_data = combined_data[~combined_data.index.duplicated(keep='first')]
        # else:
        #     # If the file does not exist, simply save the current data
        #     combined_data = self.data
        # print("All tickers have been processed and saved.")

        # return pd.read_csv(save_path, index_col=0, parse_dates=True)

    # def validate_interval(self):
    #     """
    #     Validates the interval to ensure it is supported by yfinance.
    #     """
    #     if self.interval not in self.available_intervals:
    #         raise ValueError(f"Invalid interval '{self.interval}'. Valid intervals are {self.available_intervals}.")

    # def calculate_max_available_start(self):
    #     """
    #     Calculates the maximum available start date based on the provided interval.
    #     For shorter intervals like '1m', '5m', it fetches data from the last 30 days.
    #     For longer intervals like '1d', '1wk', '1mo', it fetches data from a longer time period (e.g., 5-10 years).
    #     """
    #     # If no start and end dates are provided, adjust dynamically based on the interval
    #     if self.start is None or self.end is None:
    #         self.end = datetime.now()  # Default to current date

    #         # Handle short intervals (minute-level data)
    #         if self.interval in ['1m', '2m', '5m', '15m', '30m', '1h']:
    #             # Set start date to 30 days ago for minute-level data
    #             self.start = self.end - timedelta(days=30)
    #             print(f"Using default time range: {self.start.date()} to {self.end.date()} for interval '{self.interval}'")

    #         # Handle daily intervals (set the start date to 5 years ago for daily data)
    #         elif self.interval == '1d':
    #             self.start = self.end - timedelta(days=5*365)
    #             print(f"Using default time range: {self.start.date()} to {self.end.date()} for interval '1d'")

    #         # Handle weekly intervals (set the start date to 10 years ago for weekly data)
    #         elif self.interval == '1wk':
    #             self.start = self.end - timedelta(days=10*365)
    #             print(f"Using default time range: {self.start.date()} to {self.end.date()} for interval '1wk'")

    #         # Handle monthly intervals (set the start date to 20 years ago for monthly data)
    #         elif self.interval in ['1mo', '3mo']:
    #             self.start = self.end - timedelta(days=20*365)
    #             print(f"Using default time range: {self.start.date()} to {self.end.date()} for interval '1mo'")
    #         else:
    #             raise ValueError(f"Unsupported interval '{self.interval}'")

    # def download_data(self):
    #     """
    #     Download stock data based on the provided tickers, append it to the same column structure, and save to CSV.
    #     """

    #     # Set the directory path for saving the file
    #     directory = './data/'

    #     # Ensure the directory exists
    #     directory = os.path.dirname('./data/')
    #     if not os.path.exists(directory):
    #         os.makedirs(directory)

    #     # Validate the interval
    #     self.validate_interval()

    #     # Calculate maximum available start time based on the interval
    #     self.calculate_max_available_start()

    #     # If the file already exists, load it and continue appending new data
    #     if os.path.exists(save_path):
    #         combined_data = pd.read_csv(save_path, index_col=0, parse_dates=True)
    #     else:
    #         combined_data = pd.DataFrame()

    #     # Download data for each ticker and append to the existing DataFrame
    #     for ticker in self.tickers:
    #         print(f"Downloading data for {ticker}...")
    #         data = yf.download(ticker, start=self.start, end=self.end, interval=self.interval)
            
    #         # Handle case when no data is available
    #         if data.empty:
    #             print(f"No data available for the ticker '{ticker}' within the specified time frame.")
    #             continue

    #         # Reset index and make sure columns match
    #         data = data.reset_index()

    #         # Add 'ticker' column to distinguish which data belongs to which ticker
    #         data['ticker'] = ticker

    #         # Append the downloaded data to the combined DataFrame
    #         combined_data = pd.concat([combined_data, data], ignore_index=True)

    #         # Save after every ticker
    #         combined_data.to_csv(save_path)
    #         print(f"Data for {ticker} appended and saved to {save_path}")

    #     print("All tickers have been processed and saved.")


       


    # def get_data(self):
    #     """
    #     Returns the downloaded stock data.
    #     :return: Pandas DataFrame containing the stock data.
    #     """
    #     if self.data.empty:
    #         raise ValueError("No data downloaded yet. Please call download_data() first.")
    #     return self.data

# """
# Download stock data based on the provided tickers, start date, end date, and interval.
# Dynamically calculates the time range based on the interval if no start and end dates are provided.
# """
# # Validate the interval
# self.validate_interval()

# # Calculate maximum available start time based on the interval
# self.calculate_max_available_start()

# # Initialize an empty DataFrame to store all the tickers' data
# all_data = pd.DataFrame()

# # Download data for each ticker and combine it into a single DataFrame
# for ticker in self.tickers:
#     print(f"Downloading data for {ticker}...")
#     data = yf.download(ticker, start=self.start, end=self.end, interval=self.interval)
    
#     # Handle case when no data is available
#     if data.empty:
#         print(f"No data available for the ticker '{ticker}' within the specified time frame.")
#         continue

#     # Reset the index so that the dates don't conflict across different tickers
#     data = data.reset_index()

#     # Add ticker as a column to distinguish which data belongs to which ticker
#     data['ticker'] = ticker
    
#     # Append the downloaded data to the main DataFrame
#     all_data = pd.concat([all_data, data], ignore_index=True)

# if all_data.empty:
#     raise ValueError(f"No data available for the provided tickers within the specified time frame.")

# # Convert column names to lowercase for consistency
# all_data.columns = [col.lower() for col in all_data.columns]

# # Store the combined data in self.data
# self.data = all_data

# print("Download complete.")
# return self.data

# """
# Download stock data based on the provided tickers, start date, end date, and interval.
# Dynamically calculates the time range based on the interval if no start and end dates are provided.
# """
# # Validate the interval
# self.validate_interval()

# # Calculate maximum available start time based on the interval
# self.calculate_max_available_start()

# # Download data for each ticker and combine it into a single DataFrame
# for ticker in self.tickers:
#     print(f"Downloading data for {ticker}...")
#     data = yf.download(ticker, start=self.start, end=self.end, interval=self.interval)
    
#     # Handle case when no data is available
#     if data.empty:
#         print(f"No data available for the ticker '{ticker}' within the specified time frame.")
#         continue

#     # Add ticker as a column in the data for identification
#     data['Ticker'] = ticker
    
#     # Append the data to the main DataFrame
#     self.data = pd.concat([self.data, data], axis=0)


# if self.data.empty:
#     raise ValueError(f"No data available for the provided tickers within the specified time frame.")

#     # Convert column names to lowercase
# self.data.columns = [col.lower() for col in self.data.columns]

# print("Download complete.")
# return self.data

# def __init__(self, tickers, start=None, end=None, interval='1d'):
#     """
#     Initialize the downloader with stock tickers, start date, end date, and interval.
#     If no start or end is provided, it will download the maximum available data depending on the interval.
#     :param tickers: Stock ticker(s) symbol, can be a string (e.g., 'AAPL') or a list of tickers (e.g., ['AAPL', 'GOOGL'])
#     :param start: Start date for downloading the data (optional)
#     :param end: End date for downloading the data (optional)
#     :param interval: Data interval (e.g., '1d', '1wk', '1mo')
#     """
#     if isinstance(tickers, str):
#         self.tickers = [tickers]  # Convert single ticker to a list
#     else:
#         self.tickers = tickers
    
#     self.end = end
#     self.start = start
#     self.interval = interval
#     self.data = pd.DataFrame()

# def validate_interval(self):
#     """
#     Validates the interval to ensure it is supported by yfinance.
#     """
#     valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
#     if self.interval not in valid_intervals:
#         raise ValueError(f"Invalid interval '{self.interval}'. Valid intervals are {valid_intervals}.")

# def adjust_time_range_based_on_interval(self):
#     """
#     Adjusts the time range based on the interval if no start or end date is provided.
#     For shorter intervals like '1m', '5m', it fetches data from the last month.
#     For longer intervals, it defaults to maximum available data.
#     """
#     if self.start is None and self.end is None:
#         # Handle short intervals (minute-level)
#         if self.interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']:
#             # Fetch data for the last 30 days for short intervals
#             self.end = datetime.now()
#             self.start = self.end - timedelta(days=30)
#             print(f"Using default time range: {self.start.date()} to {self.end.date()} for interval '{self.interval}'")
#         else:
#             # Use the maximum available range for daily, weekly, or monthly data
#             print(f"Using max available data for interval '{self.interval}'")

# def download_data(self):
#     """
#     Download stock data based on the provided tickers, start date, end date, and interval.
#     Adjusts the time range based on the interval if no start and end dates are provided.
#     """
#     # Validate the interval
#     self.validate_interval()

#     # Adjust the time range based on the interval if no start/end is provided
#     self.adjust_time_range_based_on_interval()

#     # Download data for each ticker and combine it into a single DataFrame
#     for ticker in self.tickers:
#         print(f"Downloading data for {ticker}...")
#         data = yf.download(ticker, start=self.start, end=self.end, interval=self.interval)
        
#         # Handle case when no data is available
#         if data.empty:
#             print(f"No data available for the ticker '{ticker}' within the specified time frame.")
#             continue

#         # Add ticker as a column in the data for identification
#         data['Ticker'] = ticker
        
#         # Append the data to the main DataFrame
#         self.data = pd.concat([self.data, data], axis=0)

#     if self.data.empty:
#         raise ValueError(f"No data available for the provided tickers within the specified time frame.")
    
#     print("Download complete.")
#     return self.data

# def save_to_csv(self, filename):
#     """
#     Saves the downloaded data to a CSV file.
#     :param filename: Name of the file where the data will be saved (e.g., 'stocks.csv').
#     """
#     if self.data.empty:
#         raise ValueError("No data available to save. Please download the data first.")
    
#     self.data.to_csv(filename)
#     print(f"Data successfully saved to {filename}")

# def get_data(self):
#     """
#     Returns the downloaded stock data.
#     :return: Pandas DataFrame containing the stock data.
#     """
#     if self.data.empty:
#         raise ValueError("No data downloaded yet. Please call download_data() first.")
#     return self.data


# def __init__(self, symbols, start_date, end_date):
#     self.symbols = symbols
#     self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
#     self.start_date = datetime.strptime(start_date, '%Y-%m-%d')

# def fetch_data(self, interval, period):
#     print(f"Fetching data for interval: {interval}")
#     data = self.fetch_interval_data(period, interval)
#     if data is not None:
#         self.save_data_to_file(data, interval, period)

# def fetch_interval_data(self, interval='1h', period='max',):
#     data_frames = []
#     current_start = self.start_date

#     if not period:
#         while current_start < self.end_date:
#             current_end = min(current_start + timedelta(days=7), self.end_date)  # Fetch in 7-day chunks

#             try:
#                 data = yf.download(
#                     tickers=self.symbols,
#                     start=current_start.strftime('%Y-%m-%d'),
#                     end=current_end.strftime('%Y-%m-%d'),
#                     period=period,
#                     interval=interval
#                 )

#                 if not data.empty:
#                     data_frames.append(data)
#                     print(f"Fetched data from {current_start} to {current_end}")

#             except Exception as e:
#                 print(f"Failed to fetch data from {current_start} to {current_end}: {e}")

#             current_start = current_end

#         if data_frames:
#             self.df = pd.concat(data_frames)
#             return self.df
#         else:
#             print(f"No data fetched for interval: {interval}")
#             return None
#     else:
#         self.df = yf.download(
#                     tickers=self.symbols,
#                     period=period,
#                     interval=interval
#                 )
        
#         return self.df
        
# def save_data_to_file(self, data, period, interval):
#     directory = './data/'
#     if not os.path.exists(directory):
#         os.makedirs(directory)

#     if not period:

#         filename = f"{directory}/{self.symbols}_{self.start_date.strftime('%Y-%m-%d')}_{self.end_date.strftime('%Y-%m-%d')}_{interval}.csv"
#     else:
#         filename = f"{directory}/{self.symbols}_{period}_{interval}.csv"

#     if os.path.exists(filename):
#         existing_data = pd.read_csv(filename, index_col=0, parse_dates=True)
#         data = pd.concat([existing_data, data])
#         data = data[~data.index.duplicated(keep='first')]
#     data.to_csv(filename)
#     print(f"Data saved to {filename}")

