import warnings
import pandas as pd
import pandas_ta as ta
import mplfinance as mpf
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

class Plotting:
    def __init__(self, data: pd.DataFrame=None, indicators={}):
        self.df = data
        self.calc_field = None
        self.indicators = indicators
        self.calc_df: pd.DataFrame = None

    def __calculate_indicators(self, field="Close"):
        """
        Dynamically calculate specified indicators and update the DataFrame.
        Args:
            data (pd.DataFrame): Input DataFrame with 'Close' column.
            indicators (list): List of dictionaries specifying indicators.
            Example:
            [{'name': 'rsi', 'params': {'length': 14}, 'color': 'orange'},
            {'name': 'ema', 'params': {'length': 20}, 'color': 'blue'}]
        Returns:
            pd.DataFrame: Updated DataFrame with calculated indicators.
        """
        data = self.df.copy()
        indicators = self.indicators

        for indicator in indicators:
            name = indicator['name'].lower()
            params = indicator.get('params', {})
    
            # Check if the indicator exists in pandas-ta
            if hasattr(ta, name):
                try:
                    func = getattr(ta, name)
                    result = func(data[field], **params)
    
                    # Handle multi-output indicators
                    if isinstance(result, pd.DataFrame):
                        for col in result.columns:
                            col_name = f"{name.upper()}_{col}"
                            data[col_name] = result[col]
                    elif isinstance(result, pd.Series):
                        col_name = f"{name.upper()}_{'_'.join(map(str, params.values()))}"
                        data[col_name] = result
                    else:
                        print(f"Unexpected output format for indicator '{name}'.")
                except Exception as e:
                    print(f"Error calculating indicator '{name}': {e}")
            else:
                print(f"Indicator '{name}' not found in pandas-ta.")
        
        self.calc_df = data        
        return data

    def __filter_data(self, ticker_data=None, start_date=None, days=5):
        """
        Filter the data to include rows starting from a specific date.
        Handles timezone-aware and timezone-naive datetime objects.
    
        Args:
            ticker_data (pd.DataFrame): The DataFrame to filter. Defaults to `self.df`.
            start_date (str or pd.Timestamp): Start date for filtering. Defaults to today.
            days (int): Number of days to include in the filtered data. Defaults to 5.
    
        Returns:
            pd.DataFrame: The filtered DataFrame.
        """
        if ticker_data is None:
            ticker_data = self.calc_df
        
        ticker_data = ticker_data.copy()  # Ensure it's a standalone DataFrame

        if not isinstance(ticker_data, pd.DataFrame):
            raise ValueError("Ticker data must be a pandas DataFrame.")
    
        # Ensure the index is in datetime format
        if not pd.api.types.is_datetime64_any_dtype(ticker_data.index):
            ticker_data.index = pd.to_datetime(ticker_data.index)
    
        # Normalize index to remove time components
        ticker_data.loc[:, 'Normalized_Date'] = ticker_data.index.normalize()
    
        # Handle timezone awareness
        if ticker_data.index.tz is not None:  # If index is timezone-aware
            if start_date is None:
                start_date = pd.Timestamp.now(tz=ticker_data.index.tz).normalize()
            else:
                start_date = pd.to_datetime(start_date).tz_localize(ticker_data.index.tz).normalize()
        else:  # If index is timezone-naive
            if start_date is None:
                start_date = pd.Timestamp.today().normalize()
            else:
                start_date = pd.to_datetime(start_date).normalize()

        # Calculate the end date
        end_date = start_date + pd.Timedelta(days=days)
    
        # Filter the data based on normalized dates
        filtered = ticker_data[
            (ticker_data['Normalized_Date'] >= start_date) & (ticker_data['Normalized_Date'] < end_date)
        ]
    
        # Drop the temporary normalized column
        filtered = filtered.drop(columns=['Normalized_Date'])
        # print(filtered)
        return filtered

    def plot(self, field="Close", zoom_margin=0.1, start_date=None, days=5, **plot_kwargs):
        """
        Full pipeline: Calculate indicators, generate dynamic style, and plot.
    
        Args:
            data (pd.DataFrame): Input DataFrame with 'Close' column.
            indicators (list): List of indicators to calculate with colors.
                               Example:
                               [{'name': 'rsi', 'params': {'length': 14}, 'color': 'orange'},
                                {'name': 'ema', 'params': {'length': 20}, 'color': 'blue'}]
            rules (list): List of rules for dynamic styling.
            zoom_margin (float): Margin for Y-axis zoom (e.g., 0.1 for 10% margin).
            plot_kwargs: Additional kwargs for mplfinance.plot().
    
        Returns:
            None
        """
        self.calc_field = field
        # Calculate indicators
        data = self.__calculate_indicators(field)
        tickers = data['Ticker'].unique()

        for ticker in tickers:
            # Filter and process data for the given ticker
            ticker_data = data[data['Ticker'] == ticker]
            if ticker_data.empty:
                print(f"No data available for ticker: {ticker}")
                return
            ticker_data = self.__filter_data(ticker_data, start_date, days)

            # Precompute strength of candles (body size compared to the average body size)
            body_sizes = abs(ticker_data['Close'] - ticker_data['Open'])
            avg_body_size = body_sizes.mean()
            ticker_data['strength'] = body_sizes / avg_body_size  # Strength as a ratio of average body size


            # Define dynamic wick and edge colors (add new columns to data for reference)
            def get_color_and_boldness(row):
                if row['Close'] > row['Open'] and row['strength'] > 1.5:
                    return 'green', 2.5  # Strong buyer: green with bold
                elif row['Close'] < row['Open'] and row['strength'] > 1.5:
                    return 'red', 2.5  # Strong seller: red with bold
                return 'gray', 1.0  # Neutral
            
            # ticker_data['wick_color'], ticker_data['wick_width'] = zip(*ticker_data.apply(get_color_and_boldness, axis=1))
            # ticker_data['edge_color'], ticker_data['edge_width'] = zip(*ticker_data.apply(get_color_and_boldness, axis=1))
            
        # Apply the function
            wick_colors_and_widths = ticker_data.apply(get_color_and_boldness, axis=1)
            ticker_data['wick_color'] = [item[0] for item in wick_colors_and_widths]
            ticker_data['wick_width'] = [item[1] for item in wick_colors_and_widths]
            ticker_data['edge_color'] = ticker_data['wick_color']  # Same logic for edge color
            ticker_data['edge_width'] = ticker_data['wick_width']  # Same logic for edge width

            # Create market colors with the specified palette
            market_colors = mpf.make_marketcolors(
                up='lightblue', down='navy',  # Upward and downward candlestick body colors
                wick='inherit',  # Use dynamic wick colors
                edge='inherit',  # Use dynamic edge colors
                volume={'up': 'lightblue', 'down': 'navy'}  # Volume bar colors
            )
        
            # Create a custom style
            custom_style = mpf.make_mpf_style(
                base_mpf_style='yahoo',  # Base style for clean visuals
                marketcolors=market_colors,
                gridcolor='lightgray',  # Light grid for readability
                gridstyle='--',  # Dashed grid lines
                facecolor='white'  # White background
            )
    
            # Create addplots for each indicator
            add_plots = []
            ind_names = []
            legend_texts = []  # To store indicator names and colors for legend
            indicators = self.indicators

            
            for indicator in indicators:
                name = indicator.get('name'.lower(), 'rsi')
                color = indicator.get('color', 'black')  # Default to black if no color is provided
                ind_names.append(name.upper())
                
                for col in ticker_data.columns:
                    if col.lower().startswith(name):
                        add_plots.append(mpf.make_addplot(ticker_data[col], color=color))
                        legend_texts.append((col, color))  # Append indicator name and color for legend
            

            # Determine Y-axis limits for zooming
            price_min = ticker_data[['Low']].min().min()  # Minimum low price
            price_max = ticker_data[['High']].max().max()  # Maximum high price
            y_min = price_min - (price_max - price_min) * zoom_margin  # Add margin below
            y_max = price_max + (price_max - price_min) * zoom_margin  # Add margin above
            
            title=f"Candlestick Chart with Indicators: ( {", ".join(ind_names)} )"
            
            plot_kwargs = {"title": title, **plot_kwargs}
            
            # Plot using mplfinance with adjusted figure and panel ratios
            fig, axlist = mpf.plot(
                ticker_data,
                type='candle',
                volume=True,
                style=custom_style,  # Apply the custom style
                addplot=add_plots,
                figsize=(13, 7),  # Set figure size to make the chart larger
                panel_ratios=(3, 1),  # Increase height of the candlestick panel relative to the volume panel
                ylim=(y_min, y_max),  # Apply zooming limits to Y-axis
                returnfig=True,  # Return figure and axes for customization
                **plot_kwargs
            )
    
            # Add indicator names and colors outside the plot
            for i, (text, color) in enumerate(legend_texts):
                fig.text(
                    0.95, 1 - i * 0.03,  # Position text outside the plot (adjust for spacing)
                    f"---{text}",
                    color=color,
                    fontsize=10,
                    ha='left',  # Align text to the left
                    va='top'
                )
        
            # Show the plot
            plt.show()

# class Plotting:
#     def __init__(self, data):
#         """
#         Initialize the Plotting class with data.
#         Args:
#             data (pd.DataFrame): Input DataFrame with at least 'Open', 'High', 'Low', 'Close', and 'Volume' columns.
#         """
#         assert isinstance(data, pd.DataFrame), "Data must be a pandas DataFrame."
#         assert not data.empty, "Data: pd.DataFrame can't be empty."
#         self.data = data

#     def calculate_indicators(self, indicators):
#         """
#         Dynamically calculate specified indicators and update the DataFrame.
#         Args:
#             indicators (list): List of dictionaries specifying indicators.
#             Example:
#             [{'name': 'rsi', 'params': {'length': 14}, 'color': 'orange'},
#             {'name': 'ema', 'params': {'length': 20}, 'color': 'blue'}]
#         """
#         for indicator in indicators:
#             name = indicator['name'].lower()
#             params = indicator.get('params', {})
#             if hasattr(ta, name):
#                 try:
#                     func = getattr(ta, name)
#                     result = func(self.data['Close'], **params)
#                     if isinstance(result, pd.DataFrame):  # Multi-output indicators
#                         for col in result.columns:
#                             self.data[f"{name.upper()}_{col}"] = result[col]
#                     elif isinstance(result, pd.Series):  # Single-output indicators
#                         self.data[f"{name.upper()}"] = result
#                     else:
#                         print(f"Unexpected output format for indicator '{name}'.")
#                 except Exception as e:
#                     print(f"Error calculating indicator '{name}': {e}")
#             else:
#                 print(f"Indicator '{name}' not found in pandas-ta.")

#     def add_strength_columns(self):
#         """
#         Calculate candle strength (size of the body compared to the average body size)
#         and add dynamic wick and edge color columns.
#         """
#         body_sizes = abs(self.data['Close'] - self.data['Open'])
#         avg_body_size = body_sizes.mean()
#         self.data['strength'] = body_sizes / avg_body_size

#         def get_color_and_boldness(row):
#             if row['Close'] > row['Open'] and row['strength'] > 1.5:
#                 return 'green', 2.5  # Strong buyer
#             elif row['Close'] < row['Open'] and row['strength'] > 1.5:
#                 return 'red', 2.5  # Strong seller
#             return 'gray', 1.0  # Neutral

#         self.data['wick_color'], self.data['wick_width'] = zip(*self.data.apply(get_color_and_boldness, axis=1))
#         self.data['edge_color'], self.data['edge_width'] = zip(*self.data.apply(get_color_and_boldness, axis=1))

#     def create_dynamic_style(self):
#         """
#         Create a dynamic mplfinance style with specific market colors.

#         Returns:
#             dict: A custom mplfinance style.
#         """
#         market_colors = mpf.make_marketcolors(
#             up='lightblue', down='navy',  # Body colors
#             wick='inherit',  # Dynamic wick colors
#             edge='inherit',  # Dynamic edge colors
#             volume={'up': 'lightblue', 'down': 'navy'}  # Volume bar colors
#         )
#         return mpf.make_mpf_style(
#             base_mpf_style='yahoo',
#             marketcolors=market_colors,
#             gridcolor='lightgray',
#             gridstyle='--',
#             facecolor='white'
#         )

#     def plot(self, indicators, zoom_margin=0.1, **plot_kwargs):
#         """
#         Process and plot the data with indicators and dynamic styling.

#         Args:
#             indicators (list): List of indicators to calculate with colors.
#             zoom_margin (float): Margin for Y-axis zoom (e.g., 0.1 for 10% margin).
#             plot_kwargs: Additional kwargs for mplfinance.plot().
#         """
#         # Calculate indicators
#         self.calculate_indicators(indicators)

#         # Add strength and dynamic columns
#         self.add_strength_columns()

#         # Create dynamic style
#         custom_style = self.create_dynamic_style()

#         # Create addplots for indicators
#         add_plots = []
#         legend_texts = []  # For indicator names and colors
#         for indicator in indicators:
#             name = indicator['name'].lower()
#             color = indicator.get('color', 'black')  # Default to black
#             for col in self.data.columns:
#                 if col.lower().startswith(name):
#                     add_plots.append(mpf.make_addplot(self.data[col], color=color))
#                     legend_texts.append((col, color))  # Add legend text

#         # Determine Y-axis limits for zooming
#         price_min = self.data[['Low']].min().min()
#         price_max = self.data[['High']].max().max()
#         y_min = price_min - (price_max - price_min) * zoom_margin
#         y_max = price_max + (price_max - price_min) * zoom_margin

#         # Plot using mplfinance
#         fig, axlist = mpf.plot(
#             self.data,
#             type='candle',
#             volume=True,
#             style=custom_style,
#             addplot=add_plots,
#             figsize=(14, 10),
#             panel_ratios=(3, 1),
#             ylim=(y_min, y_max),
#             returnfig=True,
#             **plot_kwargs
#         )

#         # Add legend text
#         for i, (text, color) in enumerate(legend_texts):
#             fig.text(
#                 0.88, 0.95 - i * 0.03,
#                 f"{text}",
#                 color=color,
#                 fontsize=10,
#                 ha='left',
#                 va='top'
#             )

#         # Show the plot
#         plt.show()

# # class CustomPlot:
# #     def __init__(self, data):
# #         self.df = data

# #     def stock_data_ploting(self, indicators={}, title="Candlestick Chart", start_date=None, days=None):
# #         """
# #         Plots a stock market style chart with candlesticks, indicators, and volume.
# #         Parameters:
# #             ohlc_cols (list): List of OHLC column names. Default is ['Open', 'High', 'Low', 'Close'].
# #             indicators (dict): Dictionary of indicators to plot with format {'indicator_name': column_name}.
# #             volume_col (str): Name of the volume column, if provided.
# #             title (str): Title of the plot.
# #             days (int): Number of most recent days to display. If None, show at least 6 months.
# #             start_date (str): Start date for generating data, in 'YYYY-MM-DD' format. If None, today's date will be used.
# #         """
# #         # Ensure you're working on a copy of the original DataFrame
# #         self.df = self.df.copy()
# #         # Set start_date dynamically if None
# #         if start_date is None:
# #             start_date = pd.Timestamp.today().strftime('%Y-%m-%d')
# #         # Calculate the end date based on the start date and the number of days
# #         if start_date:
# #             end_date = pd.to_datetime(start_date) + pd.DateOffset(days=days-1)  # Subtract 1 because the start date counts as the first day
# #         # Title
# #         title = f"Stock Data Plting ( {start_date} <-> {end_date.strftime('%Y-%m-%d')} )"
# #         # If 'days' is not provided, calculate it for 6 months (180 days)
# #         if days is None:
# #             days = 90  # 3 months = 180 days
# #         # If 'days' is provided, adjust the number of rows in df to match the 'days'
# #         if days > 0:
# #             self.df = self.df.tail(days)  # Only take the last 'days' rows
# #         # Generate the 'Datetime' column with the correct length based on filtered data
# #         self.df.loc[:, 'Datetime'] = pd.date_range(start=start_date, periods=len(self.df), freq='D')
# #         # Set the Datetime as the index
# #         self.df.set_index('Datetime', inplace=True)
# #         # List to hold additional plots for indicators
# #         additional_plots = []
# #         # Create additional indicators
# #         # Loop through the provided indicators and add them if they exist in the dataframe
# #         for indicator, details in indicators.items():
# #             column, color = details['column'], details['color']     
# #             if column in self.df.columns:
# #                 # Apply dynamic color logic (you can still modify this logic if needed)
# #                 # We can keep it simple or use colors based on a condition like diff().
# #                 colors = self.df[column].diff().apply(lambda x: color if x > 0 else 'red')
# #                 # Add the plot for this indicator with the provided color
# #                 additional_plots.append(mpf.make_addplot(self.df[column], panel=0, color=colors, secondary_y=False))
# #             else:
# #                 print(f"Warning: Indicator column '{column}' not found in the DataFrame.")
# #         # Define the market colors and style with ratio adjustments
# #         market_colors = mpf.make_marketcolors(up='green', down='red', inherit=True)
        
# #         # Adjusting figure ratio and size (not directly candle width)
# #         style = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=market_colors)

# #         # Set the figure size and ratio
# #         fig_size = (14, 8)  # Size in inches
# #         figratio = (10, 6)  # Ratio of the figure
        
# #         # Plot the candlestick chart with volume and indicators
# #         mpf.plot(self.df, type='candle', style=style, title=title, volume=True, addplot=additional_plots, figsize=fig_size, figratio=figratio, xlabel="Datetime", ylabel="Price")