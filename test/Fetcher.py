# Usage Example
from fetcher import YahooDataFetcher
from preprocess.PreProcessing import DataPreProcessing
from tickers.Tickers import DOW_30_TICKER


if __name__ == "__main__":
    # Initialize the downloader object with multiple tickers
    # tickers = DOW_30_TICKER  # Example tickers: Apple, Google, Microsoft
    interval = '1h'  # Can change to '1d', '1wk', '1mo', etc.
    end_date = None  # If None, it will download up to the latest available data
    start_date = None  # If None, it will download max available data or adjust based on the interval
    # tickers = ['600519.SS', '601318.SS', '000002.SZ', '0700.HK']
    # Create an instance of the StockDataDownloader
    downloader = YahooDataFetcher(country='usa', tickers=DOW_30_TICKER, start=start_date, end=end_date, interval=interval)

    # Download the stock data
    downloader.download_data()

    data = downloader.get_data()

    # print(data.head(10))

    # df = downloader.processing(data)
    df = DataPreProcessing(data)

