import os
import pandas as pd
import yfinance as yf
from typing import List



class YahooDataFetcher:
    def __init__(self, tickers: List = [], intervals: List = ['1min', '5min', '15min', '30min', '1h', '1d'], 
                 start_date: str = None, end_date: str = None):
        """
        Initialize the YahooDataFetcher with tickers, intervals, and optional date range.
        
        Parameters:
        - tickers: List of stock ticker symbols (e.g., ['AAPL', 'GOOGL']) or a single string
        - intervals: List of time intervals (e.g., ['1min', '1h', '1d'])
        - start_date: Start date for data (e.g., '2020-01-01'), defaults to None (max period)
        - end_date: End date for data (e.g., '2022-01-01'), defaults to None (today)
        """
        if isinstance(tickers, str):
            self.tickers = [tickers]
        else:
            self.tickers = tickers
        
        self.intervals = intervals
        self.start_date = pd.to_datetime(start_date) if start_date else None
        self.end_date = pd.to_datetime(end_date) if end_date else None
        self.data = pd.DataFrame()
        self.dir_name = "./data/yahoo-data"
        
        # Ensure directory is clean on initialization
        self.delete_all_files(self.dir_name)

    def delete_all_files(self, folder_path: str):
        """
        Deletes all files in the specified folder.
        """
        try:
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                print(f"All files deleted in {folder_path}")
            else:
                os.makedirs(folder_path)  # Create directory if it doesn’t exist
                print(f"Created directory: {folder_path}")
        except Exception as e:
            print(f"Error deleting files in {folder_path}: {e}")

    def download_data(self):
        """
        Download stock data for all tickers and intervals using yfinance.
        Saves data to individual CSV files and stores in self.data.
        """
        self.data = pd.DataFrame()  # Reset data
        
        for interval in self.intervals:
            for ticker in self.tickers:
                print(f"Downloading data for {ticker} at interval {interval}...")
                
                # Download data
                if self.start_date and self.end_date:
                    data = yf.download(ticker, period="max", interval=interval, keepna=False, multi_level_index=False)
                else:
                    data = yf.download(ticker, period="max", interval=interval, keepna=False, multi_level_index=False)
                
                # Fallback for indices (e.g., ^GSPC for S&P 500)
                if data.empty and not ticker.startswith('^'):
                    alt_ticker = f"^{ticker}"
                    print(f"No data for {ticker}. Trying {alt_ticker}...")
                    if self.start_date and self.end_date:
                        data = yf.download(alt_ticker, period="max", interval=interval, keepna=False, multi_level_index=False)
                    else:
                        data = yf.download(alt_ticker, period="max", interval=interval, keepna=False, multi_level_index=False)
                
                if data.empty:
                    print(f"No data available for {ticker} at interval {interval}")
                    continue
                
                # Convert column names to lowercase
                data.columns = [col.lower() for col in data.columns]
                
                # Select required OHLCV columns
                required_columns = ['open', 'high', 'low', 'close', 'volume']
                if not all(col in data.columns for col in required_columns):
                    print(f"Skipping {ticker}: Missing required columns")
                    continue
                
                filtered_data = data[required_columns].copy()
                filtered_data['ticker'] = ticker
                filtered_data['interval'] = interval
                
                # Reset index to include datetime as a column
                filtered_data = filtered_data.reset_index().rename(columns={'Datetime': 'datetime', 'Date': 'date'})
                
                # Save to CSV
                self.save_data(filtered_data, ticker, interval)
                
                # Append to in-memory DataFrame
                self.data = pd.concat([self.data, filtered_data], ignore_index=True)
        
        if self.data.empty:
            raise ValueError("No data downloaded for any ticker or interval")
        print("Download complete.")

    def save_data(self, data: pd.DataFrame, ticker: str, interval: str):
        """
        Save the downloaded data to a CSV file.
        """
        if data.empty:
            print(f"No data to save for {ticker} at {interval}")
            return
        
        if not os.path.exists(self.dir_name):
            os.makedirs(self.dir_name)
        
        filename = f"{self.dir_name}/{ticker}.csv"
        data.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def get_data(self):
        """
        Return the combined downloaded data from memory or load from saved CSVs if not in memory.
        
        Returns:
        - DataFrame with all downloaded data
        """
        if not self.data.empty:
            return self.data
        
        # Load from CSV files if data is not in memory
        combined_data = []
        if os.path.exists(self.dir_name):
            for filename in os.listdir(self.dir_name):
                file_path = os.path.join(self.dir_name, filename)
                if os.path.isfile(file_path) and file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    if not df.empty:
                        combined_data.append(df)
        
        if not combined_data:
            raise ValueError("No data available. Please call download_data() first.")
        
        self.data = pd.concat(combined_data, ignore_index=True)
        return self.data

# Example usage
if __name__ == "__main__":
    intervals = ['1min', '5min', '15min', '30min', '1h', '1d']
    tickers = ['N225', 'HSI', 'GSPC', 'DJI', 'IXIC', 'TYX', 'GDAXI', 'OEX', 'FCHI', 'STI', 'TWII', 'NYA', 'XAX', 'BUK100P', 'RUT', 'VIX', 'STOXX50E', 'N100', 'BFX', 'AXJO', 'AORD', 'BSESN', 'JKSE', 'KLSE', 'NZ50', 'KS11', 'GSPTSE', 'BVSP', 'MXX', 'IPSA', 'MERV', 'TA125.TA', 'CASE30', 'JN0U.JO']
    fetcher = YahooDataFetcher(tickers=tickers, intervals=intervals)
    fetcher.download_data()
    data = fetcher.get_data()
    
    # print(f"Data shape: {data.shape}")
    # print(data.head())
    # print(data.groupby(['ticker', 'interval']).size())