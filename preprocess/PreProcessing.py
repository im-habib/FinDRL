import pandas as pd
# import warnings
# warnings.filterwarnings("ignore", category=FutureWarning)

class DataPreProcessing:
    def __init__(self, df):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame.")
        self.df = df
        self.REQUIRED_COLUMNS = [
            'datetime', 'open', 'high', 'low', 'close', 
            'adj close', 'volume', 'ticker'
        ]

    def validate_columns(self):
        """
        Validates that all required columns exist in the DataFrame.
        Raises:
            ValueError: If any required columns are missing.
        """
        self.df.columns = [col.lower() for col in self.df.columns]
        
        # Check if datetime is in the index, and adjust required columns
        if 'datetime' in self.df.index.names:
            self.REQUIRED_COLUMNS.remove('datetime')

        missing_columns = [
            col for col in self.REQUIRED_COLUMNS if col not in self.df.columns
        ]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

    def handle_multiindex(self):
        # print("handle_multiindex")
        # print(self.df.head(5))
        try:
            if isinstance(self.df.columns, pd.MultiIndex):
                self.df.columns = self.df.columns.droplevel('ticker')
                self.df.columns.name = None
        except Exception as e:
            print(f"An error occurred while handling MultiIndex: {e}")

    def set_datetime_index(self):
        try:
            # Strip spaces from column names
            self.df.columns = self.df.columns.str.strip()

            # Check if 'Datetime' or 'Date' or 'datetime' columns exist
            datetime_columns = ['Datetime', 'Date', 'datetime']

            # Find the first matching column for datetime
            for col in datetime_columns:
                if col in self.df.columns:
                    self.df['datetime'] = pd.to_datetime(self.df[col], errors='coerce')  # Convert to datetime
                    self.df = self.df.set_index('datetime')  # Set as index
                    self.df = self.df.sort_index()  # Sort by datetime index
                    print(f"Successfully set '{col}' as the datetime index.")
                    return

            raise KeyError("No valid 'Datetime' or 'Date' column found to set as index.")

        except Exception as e:
            print(f"Error setting datetime index: {e}")

    def drop_na(self):
        self.df = self.df.dropna()
    
    def fill_na(self, fill_value=0):
        self.df = self.df.fillna(fill_value)

    def drop_columns(self, columns):
        # Check if each column exists in the DataFrame before attempting to drop
        existing_columns = [col for col in columns if col in self.df.columns]
        if existing_columns:
            self.df = self.df.drop(columns=existing_columns, inplace=False)
            print(f"Dropped columns: {existing_columns}")
        else:
            print("No matching columns to drop.")

    def processed(self, columns=[]):
        # print("preprocess")
        # print(self.df.head(5))
        self.validate_columns()
        self.handle_multiindex()
        # If datetime is not already an index, set it
        if 'datetime' not in self.df.index.names:
            self.set_datetime_index()
        self.drop_na()
        self.fill_na()
        self.drop_columns(columns)
        return self.df
    
        # if not self.df.empty:
        #     self.df.to_csv(f"./data/{self.country}/processed.csv")
    # def load_csv(self, filename: str):
    #     """Find a CSV file in the specified folder based on the provided file number."""
    #     loader = DataLoder(filename)
    #     return loader.load()
        # df = pd.read_csv(filename, index_col=True)
        # if df.empty:
        #     raise ValueError(f"Requested file ({self.filename}) which is out of range and not available to load")
        # df.set_index('Datetime', )  # Set 'Datetime' column as index

    # def save_processed_data(self, filename):
    #     self.df.

    # def calculate_indicators(self, data: pd.DataFrame):
    #     ind = IndicatorSwitch(data)
    #     indicators = [MACD, BollingerBands, RSI, CCI, DX, SMA]
    #     ind.set_indicators(indicators)
    #     data = ind.calculate()
    #     return data
