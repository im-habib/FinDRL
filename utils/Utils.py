import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def total_months_month_array(from_date, to_date):
    start_date = datetime.strptime(from_date, "%Y-%m-%d")
    end_date = datetime.strptime(to_date, "%Y-%m-%d")

    total_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
    month_array = []
    current_date = start_date

    while current_date <= end_date:
        month_array.append(current_date.strftime("%Y-%m"))
        current_date += relativedelta(months=1)

    return total_months, month_array

def combine_csv_files_data(input_directory, output_file):

    all_files = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.endswith('.csv')]
    all_data = []

    for file in all_files:
        df = pd.read_csv(file, parse_dates=['timestamp'])
        all_data.append(df)

    combined_df = pd.concat(all_data)
    combined_df = combined_df.sort_values(by='timestamp')
    combined_df.to_csv(output_file, index=False)
    print(f"Combined data saved to {output_file} and started analyzation...")
    print(f"For backtese use this data file: {output_file}")

def correct_columns_name(self, data):
    columns = data.columns
    corrected_columns = [col[0].upper() + col[1:] for col in columns]
    data.columns = corrected_columns
    return data

def convert_to_minutes(interval):
    if interval.endswith("min"):
        return int(interval[:-3])
    elif interval.endswith("h"):
        return int(interval[:-1]) * 60
    elif interval.endswith("d"):
        return int(interval[:-1]) * 24 * 60
    else:
        raise ValueError("Unsupported interval format")

def hoc_print(data=None, reasone=''):
    print(f"-----Reasone: {reasone}------")
  
    print(data)

    print(f"\n\n")

def is_csv_file(filename: str):
    return filename.lower().endswith('.csv')

def standardize_columns(df, to_upper=True):
    """
    Standardizes column names to either uppercase or lowercase based on the `to_upper` parameter
    and sets the 'Datetime' (or 'datetime') column as the index after renaming.
    Parameters:
        df (pd.DataFrame): The DataFrame to standardize.
        to_upper (bool): If True, renames columns to uppercase; if False, renames to lowercase.
    Returns:
        pd.DataFrame: DataFrame with standardized column names and DatetimeIndex.
    Raises:
        ValueError: If required columns are missing after renaming.
    """
    if to_upper:
        # Define expected column mappings for lowercase to uppercase
        expected_columns = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume',
            'datetime': 'Datetime', 
            'adj close': 'Adj Close'
        }
        required_columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    else:
        # Define expected column mappings for uppercase to lowercase
        expected_columns = {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Datetime': 'datetime', 
            'Adj Close': 'adj close'
        }
        required_columns = ['datetime', 'open', 'high', 'low', 'close', 'adj close', 'volume']
    
    # Create a mapping for renaming based on the existing columns in df
    rename_columns = {col: expected_columns[col.lower() if to_upper else col] 
                    for col in df.columns if (col.lower() if to_upper else col) in expected_columns}
    
    # Rename the columns to match the desired format
    ndf = df.rename(columns=rename_columns)
    
    # Verify if required columns are present after renaming
    missing_columns = [col for col in required_columns if col not in ndf.columns]
    if missing_columns:
        raise ValueError(f"Data is missing required columns: {missing_columns}")
    
    # Set 'Datetime' (or 'datetime') as index if it exists in the DataFrame
    datetime_col = 'Datetime' if to_upper else 'datetime'
    if datetime_col in ndf.columns:
        ndf[datetime_col] = pd.to_datetime(ndf[datetime_col], errors='coerce')  # Convert to datetime if necessary
        ndf = ndf.set_index(datetime_col)
    else:
        raise ValueError(f"The specified datetime column '{datetime_col}' does not exist in the DataFrame.")
    
    return ndf

# interval_minutes = convert_to_minutes(interval)
# if interval_minutes <= 30:
#     file_path = resalmple_data.process(interval)
# else:
#     file_path = resalmple_data.find_csv_file(data_directory, file_number)


# if __name__ == "__main__":
#     input_directory = "./data/POLYGON/minute"  # Change this to your actual input directory
#     output_file = "data/POLYGON/minute/combined_data.csv"  # Change this to your desired output file path

#     combine_csv_files_data(input_directory, output_file)

# def create_date_range(start_date, end_date):
#     # Generate a range of dates between start_date and end_date
#     date_range = pd.date_range(start=start_date, end=end_date).tolist()
#     # Convert each Timestamp to string
#     date_range_str = [date.strftime('%Y-%m-%d') for date in date_range]
#     return date_range_str

# def create_month_range(start_month, end_month):
#     # Generate a range of months between start_month and end_month
#     month_range = pd.date_range(start=start_month, end=end_month, freq='MS').tolist()
#     # Convert each Timestamp to string in 'YYYY-MM' format
#     month_range_str = [date.strftime('%Y-%m-%d') for date in month_range]
#     return month_range_str

# import yfinance as yf

# def down():

#     msft = yf.download("MSFT")

#     # get all stock info
#     msft.info

#     # get historical market data
#     hist = msft.history(period="1mo")
