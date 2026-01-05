import warnings
import pandas as pd
import mplfinance as mpf

warnings.filterwarnings("ignore", category=FutureWarning)

class Utils:
    def __init__(self, data):
        self.df = data

    def standardize_columns(self, to_upper=True):
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
                        for col in self.df.columns if (col.lower() if to_upper else col) in expected_columns}
        
        # Rename the columns to match the desired format
        ndf = self.df.rename(columns=rename_columns)
        
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
        
    # def stock_plot(self, style, title, columns_to_plot=[]):
    #     """
    #     Dynamically plots columns from a DataFrame using mplfinance, supporting both uppercase and lowercase OHLC columns.
    #     """
    #     # Standardize column names using the provided function
    #     ndf = self.df
        
    #     # Debug: Print the columns to verify the presence of 'Datetime' or 'datetime'
    #     print("Columns after standardization:", ndf.columns)

    #     # Ensure the standardized x_col is set as the DatetimeIndex if it’s not already
    #     x_col_standardized = 'Datetime'
        
    #     # Check if the datetime column exists; if not, create it with sequential dates
    #     if x_col_standardized not in self.df.columns:
    #         print(f"Warning: '{x_col_standardized}' column not found. Creating a default datetime column.")
    #         self.df[x_col_standardized] = pd.date_range(start='2023-01-01', periods=len(self.df), freq='D')

    #     # Convert to datetime and set as index
    #     self.df[x_col_standardized] = pd.to_datetime(self.df[x_col_standardized], errors='coerce')
    #     self.df = self.df.set_index(x_col_standardized)

    #     # Check that the index is now a DatetimeIndex
    #     if not isinstance(self.df.index, pd.DatetimeIndex):
    #         raise TypeError("The index of the DataFrame must be a DatetimeIndex for mplfinance plotting.")

    #     # Prepare additional plots for indicators in `columns_to_plot`
    #     add_plots = []
    #     for col in columns_to_plot:
    #         if col in self.df.columns:
    #             add_plots.append(
    #                 mpf.make_addplot(self.df[col], type='line', ylabel=col)
    #             )
    #         else:
    #             print(f"Warning: Column '{col}' not found in the DataFrame.")

    #     # Determine if all required OHLC columns are present for a candlestick plot
    #     ohlc_standardized = ['Open', 'High', 'Low', 'Close']
    #     plot_type = 'candle' if all(col in self.df.columns for col in ohlc_standardized) else 'line'
        
    #     plot_type = 'candle' if all(col in self.df.columns for col in ohlc_standardized) else 'line'

    #     # Plot the data using mplfinance
    #     mpf.plot(
    #         ndf,
    #         style=style,
    #         title=title,
    #         type=plot_type,
    #         volume=True,
    #         addplot=add_plots,
    #         ylabel='Price',
    #         ylabel_lower='Volume',
    #         datetime_format='%Y-%m-%d',
    #         figratio=(12, 8),
    #         warn_too_much_data=len(ndf) + 1000  # Suppress warning for large datasets
    #     )

    # def stock_data_plot(self, ohlc_cols=['Open', 'High', 'Low', 'Close'], indicators={}, volume_col='Volume', title="Stock Market Style Chart", days=None):
        """
        Plots a stock market style candlestick chart with indicators and volume using mplfinance.

        Parameters:
            df (pd.DataFrame): DataFrame containing stock data with datetime index.
            ohlc_cols (list): List of OHLC column names. Default is ['Open', 'High', 'Low', 'Close'].
            indicators (dict): Dictionary of indicators to plot with format {'indicator_name': column_name}.
            volume_col (str): Name of the volume column, if provided.
            title (str): Title of the plot.
            days (int): Number of most recent days to display. If None, show all data.
        """
        # Filter DataFrame to show only the last `days` rows if `days` is specified
        if days is not None and days > 0:
            df = df.tail(days)

        # Prepare additional plots for indicators
        add_plots = []
        for indicator_name, column in indicators.items():
            if column in df.columns:
                add_plots.append(mpf.make_addplot(df[column], panel=0, ylabel=indicator_name))
            else:
                print(f"Warning: Indicator column '{column}' not found in the DataFrame.")

        # Plot the data using mplfinance
        mpf.plot(
            df,
            type='candle',  # Candlestick chart
            style='yahoo',  # Stock market style
            title=title,
            volume=True if volume_col in df.columns else False,
            addplot=add_plots,
            ylabel='Price',
            ylabel_lower='Volume' if volume_col in df.columns else '',
            datetime_format='%Y-%m-%d',
            figratio=(50, 30)
        )
    
    def stock_data_ploting(self, indicators={}, title="Candlestick Chart", start_date=None, days=None):
        """
        Plots a stock market style chart with candlesticks, indicators, and volume.

        Parameters:
            ohlc_cols (list): List of OHLC column names. Default is ['Open', 'High', 'Low', 'Close'].
            indicators (dict): Dictionary of indicators to plot with format {'indicator_name': column_name}.
            volume_col (str): Name of the volume column, if provided.
            title (str): Title of the plot.
            days (int): Number of most recent days to display. If None, show at least 6 months.
            start_date (str): Start date for generating data, in 'YYYY-MM-DD' format. If None, today's date will be used.
        """
        # Ensure you're working on a copy of the original DataFrame
        self.df = self.df.copy()
        
        # Set start_date dynamically if None
        if start_date is None:
            start_date = pd.Timestamp.today().strftime('%Y-%m-%d')
        
        # Calculate the end date based on the start date and the number of days
        if start_date:
            end_date = pd.to_datetime(start_date) + pd.DateOffset(days=days-1)  # Subtract 1 because the start date counts as the first day

        # Title
        title = f"Stock Data Plting ( {start_date} <-> {end_date.strftime('%Y-%m-%d')} )"
        # If 'days' is not provided, calculate it for 6 months (180 days)
        if days is None:
            days = 90  # 3 months = 180 days
        
        # If 'days' is provided, adjust the number of rows in df to match the 'days'
        if days > 0:
            self.df = self.df.tail(days)  # Only take the last 'days' rows
        
        # Generate the 'Datetime' column with the correct length based on filtered data
        self.df.loc[:, 'Datetime'] = pd.date_range(start=start_date, periods=len(self.df), freq='D')

        # Set the Datetime as the index
        self.df.set_index('Datetime', inplace=True)

        # List to hold additional plots for indicators
        additional_plots = []

        # Create additional indicators
        # Loop through the provided indicators and add them if they exist in the dataframe
        for indicator, details in indicators.items():
            column, color = details['column'], details['color']
            
            if column in self.df.columns:
                # Apply dynamic color logic (you can still modify this logic if needed)
                # We can keep it simple or use colors based on a condition like diff().
                colors = self.df[column].diff().apply(lambda x: color if x > 0 else 'red')
                
                # Add the plot for this indicator with the provided color
                additional_plots.append(mpf.make_addplot(self.df[column], panel=0, color=colors, secondary_y=False))
            else:
                print(f"Warning: Indicator column '{column}' not found in the DataFrame.")


        # Define the market colors and style with ratio adjustments
        market_colors = mpf.make_marketcolors(up='green', down='red', inherit=True)
        
        # Adjusting figure ratio and size (not directly candle width)
        style = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=market_colors)

        # Set the figure size and ratio
        fig_size = (14, 8)  # Size in inches
        figratio = (10, 6)  # Ratio of the figure
        
        # Plot the candlestick chart with volume and indicators
        mpf.plot(self.df, type='candle', style=style, title=title, volume=True, addplot=additional_plots, figsize=fig_size, figratio=figratio, xlabel="Datetime", ylabel="Price")


    # def stock_data_pyplot(self, ohlc_cols=['Open', 'High', 'Low', 'Close'], indicators={}, volume_col='Volume', 
    #                       title="Candlestick Chart", days=None, start_date=None):
    #     """
    #     Plots a stock market style chart with candlesticks, indicators, and volume.

    #     Parameters:
    #         ohlc_cols (list): List of OHLC column names. Default is ['Open', 'High', 'Low', 'Close'].
    #         indicators (dict): Dictionary of indicators to plot with format {'indicator_name': column_name}.
    #         volume_col (str): Name of the volume column, if provided.
    #         title (str): Title of the plot.
    #         days (int): Number of most recent days to display. If None, show at least 6 months.
    #         start_date (str): Start date for generating data, in 'YYYY-MM-DD' format. If None, today's date will be used.
    #     """
    #     # Set start_date dynamically if None
    #     if start_date is None:
    #         start_date = pd.Timestamp.today().strftime('%Y-%m-%d')
        
    #     # If 'days' is not provided, calculate it for 6 months (180 days)
    #     if days is None:
    #         days = 180  # 6 months = 180 days
        
    #     # If 'days' is provided, adjust the number of rows in df to match the 'days'
    #     if days > 0:
    #         self.df = self.df.tail(days)  # Only take the last 'days' rows
        
    #     # Generate the 'Datetime' column with the correct length based on filtered data
    #     self.df.loc[:, 'Datetime'] = pd.date_range(start=start_date, periods=len(self.df), freq='D')

    #     # Set the Datetime as the index
    #     self.df.set_index('Datetime', inplace=True)

    #     # Create additional indicators
    #     additional_plots = []
    #     for indicator, column in indicators.items():
    #         if column in self.df.columns:
    #             additional_plots.append(mpf.make_addplot(self.df[column], panel=0, color='orange', secondary_y=False))
    #         else:
    #             print(f"Warning: Indicator column '{column}' not found in the DataFrame.")

    #     # Define the market colors and style
    #     market_colors = mpf.make_marketcolors(up='green', down='red', inherit=True)
    #     style = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=market_colors)

    #     # Plot the candlestick chart with volume and indicators
    #     mpf.plot(self.df, type='candle', style=style, title=title, ylabel='Price', volume=True,
    #              addplot=additional_plots, figsize=(14, 8)

    # def stock_data_pyplot(self, ohlc_cols=['Open', 'High', 'Low', 'Close'], indicators={}, volume_col='Volume', 
    #                       title="Candlestick Chart", start_date=None, days=None):
    #     """
    #     Plots a stock market style chart with candlesticks, indicators, and volume.

    #     Parameters:
    #         ohlc_cols (list): List of OHLC column names. Default is ['Open', 'High', 'Low', 'Close'].
    #         indicators (dict): Dictionary of indicators to plot with format {'indicator_name': column_name}.
    #         volume_col (str): Name of the volume column, if provided.
    #         title (str): Title of the plot.
    #         days (int): Number of most recent days to display. If None, show at least 6 months.
    #         start_date (str): Start date for generating data, in 'YYYY-MM-DD' format. If None, today's date will be used.
    #     """
    #     # Set start_date dynamically if None
    #     if start_date is None:
    #         start_date = pd.Timestamp.today().strftime('%Y-%m-%d')
        
    #     # If 'days' is not provided, calculate it for 6 months (180 days)
    #     if days is None:
    #         days = 180  # 6 months = 180 days
        
    #     # If 'days' is provided, adjust the number of rows in df to match the 'days'
    #     if days > 0:
    #         self.df = self.df.tail(days)  # Only take the last 'days' rows
        
    #     # Generate the 'Datetime' column with the correct length based on filtered data
    #     self.df.loc[:, 'Datetime'] = pd.date_range(start=start_date, periods=len(self.df), freq='D')

    #     # Set the Datetime as the index
    #     self.df.set_index('Datetime', inplace=True)

    #     fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    #     fig.suptitle(title, fontsize=16)
    #     ax1.set_ylabel("Price")
    #     ax2.set_ylabel("Volume")

    #     # Set grid style
    #     ax1.grid(visible=True, which='both', color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    #     ax2.grid(visible=False)  # Disable grid on volume for a cleaner look
        
    #     # Plot OHLC as candlestick
    #     for date, row in self.df.iterrows():
    #         color = 'green' if row[ohlc_cols[3]] >= row[ohlc_cols[0]] else 'red'  # Close >= Open: green; else red
    #         # Draw the candle body (open-close)
    #         ax1.add_patch(Rectangle((mdates.date2num(date) - 0.4, min(row[ohlc_cols[0]], row[ohlc_cols[3]])),
    #                                 0.8, abs(row[ohlc_cols[0]] - row[ohlc_cols[3]]), color=color, alpha=0.8))
    #         # Draw the wicks (high-low)
    #         ax1.vlines(mdates.date2num(date), row[ohlc_cols[2]], row[ohlc_cols[1]], color=color, linewidth=1)

    #     # Plot each indicator if provided
    #     for indicator, column in indicators.items():
    #         if column in self.df.columns:
    #             ax1.plot(self.df.index, self.df[column], label=indicator, linewidth=1.5)
    #         else:
    #             print(f"Warning: Indicator column '{column}' not found in the DataFrame.")
    #     ax1.legend(loc="upper left", fontsize=10, frameon=False)

    #     # Plot volume data if provided
    #     if volume_col in self.df.columns:
    #         colors = ['green' if self.df[ohlc_cols[3]].iloc[i] >= self.df[ohlc_cols[0]].iloc[i] else 'red' for i in range(len(self.df))]
    #         ax2.bar(self.df.index, self.df[volume_col], color=colors, alpha=0.4, width=0.8, align='center')
        
    #     # Set x-axis as date
    #     ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #     fig.autofmt_xdate()  # Rotate date labels for readability

    #     plt.show()

