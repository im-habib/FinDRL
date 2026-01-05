import os
import pandas as pd
from datetime import datetime
from investpy import get_stock_historical_data, stocks

class InvestpyDataFetcher:
    def __init__(self, output_dir='./data/'):
        """
        Initialize the stock data fetcher.
        :param time_frame: Time frame for the stock data (e.g., 'daily', 'weekly', 'monthly').
        :param output_dir: Directory where the stock data will be saved.
        """
        self.time_frame = None
        self.output_dir = output_dir
        self.available_countries = stocks.get_stock_countries()
        
        # Ensure the output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_available_tickers(self, country):
        """
        Fetch the list of available stock tickers for the initialized country.
        :return: A list of stock tickers.
        """
        # print(f"Fetching available tickers for {country}...")
        try:
            country_stocks = stocks.get_stocks(country=country)
            tickers = country_stocks['symbol'].tolist()
            print(f"Found {len(tickers)} tickers for {country}.")
            return tickers
        except Exception as e:
            print(f"Error fetching tickers for {country}: {e}")
            return []
        
    def get_available_time_frames(self):
        """
        Return the available time frames for fetching stock data in investpy.
        """
        return ['daily', 'weekly', 'monthly']

    def download_data(self, country, interval):
        """
        Downloads maximum available data for all stock symbols from the given country and saves them into a single file.
        """
        tickers = self.get_available_tickers(country)

        # Initialize an empty DataFrame to store the combined data for all tickers
        combined_data = pd.DataFrame()

        for stock in tickers:
            print(f"Fetching data for stock: {stock} from {country}")
            
            try:
                # Get the maximum available historical data for the stock
                stock_data = get_stock_historical_data(stock=stock,
                                                                country=country,
                                                                from_date='01/01/1900',  # Maximum available data
                                                                to_date=datetime.now().strftime('%d/%m/%Y'),
                                                                interval=interval)
                # Add a 'ticker' column to identify which stock the data belongs to
                stock_data['ticker'] = stock

                # Append this stock's data to the combined DataFrame
                combined_data = pd.concat([combined_data, stock_data], ignore_index=True)

            except Exception as e:
                print(f"Error fetching data for stock {stock} in {country}: {e}")
                continue

        # Save the combined data to a CSV file
        combined_file = f"{self.output_dir}/{country}_all_tickers_{interval}.csv"
        combined_data.to_csv(combined_file)
        print(f"All data for {country} saved to {combined_file}")


# Example Usage
if __name__ == "__main__":
    # Get the available countries using the static method
    stock = InvestpyDataFetcher()

    print("Available countries for stock data:")
    countries = stock.available_countries
    intervals = stock.get_available_time_frames()
    # print(f'countries: {stock.available_countries}')
    for idx, country in enumerate(countries):
        # print(country)
        if country == 'china':
            cn_tickers = stock.get_available_tickers(country)
            # print(f'{idx}: {country} - tickers: {stock.get_available_tickers(country)}')
            stock.download_data(country, intervals[0])

    # Initialize with a country, stock symbols, and time frame
    # country = 'United States'  # Example country
    # symbols = ['AAPL', 'MSFT']  # Example stock symbols
    # time_frame = 'daily'  # Example time frame ('daily', 'weekly', 'monthly')

    # # Create an instance of the StockDataFetcher
    # fetcher = StockDataFetcher(country, symbols, time_frame)

    # # Download the stock data
    # fetcher.download_max_data()
