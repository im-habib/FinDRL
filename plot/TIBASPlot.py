import warnings
import pandas as pd
import pandas_ta as ta
import mplfinance as mpf
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

# Plotting
class Plotting:
    def __init__(self, data: pd.DataFrame=None,  bt_result=pd.DataFrame, indicator_name=""):
        self.df = data
        self.indicator_name = indicator_name
        self.indicator_data = data[indicator_name]

    def plot(self, zoom_margin=0.1, **plot_kwargs):
        """
        Full pipeline: Calculate indicators, generate dynamic style, and plot.
        Args:
            data (pd.DataFrame): Input DataFrame with 'close' column.
            indicators (list): List of indicators to calculate with colors.
            Example:
            rules (list): List of rules for dynamic styling.
            zoom_margin (float): Margin for Y-axis zoom (e.g., 0.1 for 10% margin).
            plot_kwargs: Additional kwargs for mplfinance.plot().
        Returns:
            None
        """        
        # Precompute strength of candles (body size compared to the average body size)
        body_sizes = abs(self.df['close'] - self.df['open'])
        avg_body_size = body_sizes.mean()
        self.df['strength'] = body_sizes / avg_body_size  # Strength as a ratio of average body size

        # Define dynamic wick and edge colors (add new columns to data for reference)
        def get_color_and_boldness(row):
            if row['close'] > row['open'] and row['strength'] > 1.5:
                return 'green', 2.5  # Strong buyer: green with bold
            elif row['close'] < row['open'] and row['strength'] > 1.5:
                return 'red', 2.5  # Strong seller: red with bold
            return 'gray', 1.0  # Neutral

    # Apply the function
        wick_colors_and_widths = self.df.apply(get_color_and_boldness, axis=1)
        self.df['wick_color'] = [item[0] for item in wick_colors_and_widths]
        self.df['wick_width'] = [item[1] for item in wick_colors_and_widths]
        self.df['edge_color'] = self.df['wick_color']  # Same logic for edge color
        self.df['edge_width'] = self.df['wick_width']  # Same logic for edge width

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
        legend_texts = []  

        if self.indicator_name.lower().startswith(self.indicator_name):
            add_plots.append(mpf.make_addplot(self.indicator_data, color=color))
            legend_texts.append((self.indicator_name, color))  # Append indicator name and color for legend

        # Determine Y-axis limits for zooming
        price_min = self.df[['low']].min().min()  # Minimum low price
        price_max = self.df[['high']].max().max()  # Maximum high price
        y_min = price_min - (price_max - price_min) * zoom_margin  # Add margin below
        y_max = price_max + (price_max - price_min) * zoom_margin  # Add margin above
        
        title=f"Candlestick Chart with Indicators: ( {", ".join(ind_names)} )"
        
        plot_kwargs = {"title": title, **plot_kwargs}
        
        # Plot using mplfinance with adjusted figure and panel ratios
        fig, axlist = mpf.plot(
            self.df,
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



        # self.calc_field = field
        # Calculate indicators
        # data = self.__calculate_indicators(field)
        # tickers = data['Ticker'].unique()

        # for ticker in tickers:
            # Filter and process data for the given ticker
            # ticker_data = data[data['Ticker'] == ticker]
            # if ticker_data.empty:
            #     print(f"No data available for ticker: {ticker}")
            #     return
            # ticker_data = self.__filter_data(ticker_data, start_date, days)
        
        # self.df['wick_color'], self.df['wick_width'] = zip(*self.df.apply(get_color_and_boldness, axis=1))
        # self.df['edge_color'], self.df['edge_width'] = zip(*self.df.apply(get_color_and_boldness, axis=1))
        # To store indicator names and colors for legend
        # indicators = self.indicators
        # for indicator in indicators:
        #     name = indicator.get('name'.lower(), 'rsi')
        #     color = indicator.get('color', 'black')  # Default to black if no color is provided
        #     ind_names.append(name.upper())
        #     for col in self.df.columns:
        # self.calc_field = None
        # self.calc_df: pd.DataFrame = None
    # def __calculate_indicators(self, field="close"):
    #     """
    #     Dynamically calculate specified indicators and update the DataFrame.
    #     Args:
    #         data (pd.DataFrame): Input DataFrame with 'close' column.
    #         indicators (list): List of dictionaries specifying indicators.
    #         Example:
    #         [{'name': 'rsi', 'params': {'length': 14}, 'color': 'orange'},
    #         {'name': 'ema', 'params': {'length': 20}, 'color': 'blue'}]
    #     Returns:
    #         pd.DataFrame: Updated DataFrame with calculated indicators.
    #     """
    #     data = self.df.copy()
    #     indicators = self.indicators

    #     for indicator in indicators:
    #         name = indicator['name'].lower()
    #         params = indicator.get('params', {})

    #         # Check if the indicator exists in pandas-ta
    #         if hasattr(ta, name):
    #             try:
    #                 func = getattr(ta, name)
    #                 result = func(data[field], **params)

    #                 # Handle multi-output indicators
    #                 if isinstance(result, pd.DataFrame):
    #                     for col in result.columns:
    #                         col_name = f"{name.upper()}_{col}"
    #                         data[col_name] = result[col]
    #                 elif isinstance(result, pd.Series):
    #                     col_name = f"{name.upper()}_{'_'.join(map(str, params.values()))}"
    #                     data[col_name] = result
    #                 else:
    #                     print(f"Unexpected output format for indicator '{name}'.")
    #             except Exception as e:
    #                 print(f"Error calculating indicator '{name}': {e}")
    #         else:
    #             print(f"Indicator '{name}' not found in pandas-ta.")
        
    #     self.calc_df = data        
    #     return data

    # def __filter_data(self, ticker_data=None, start_date=None, days=5):
    #     """
    #     Filter the data to include rows starting from a specific date.
    #     Handles timezone-aware and timezone-naive datetime objects.

    #     Args:
    #         ticker_data (pd.DataFrame): The DataFrame to filter. Defaults to `self.df`.
    #         start_date (str or pd.Timestamp): Start date for filtering. Defaults to today.
    #         days (int): Number of days to include in the filtered data. Defaults to 5.

    #     Returns:
    #         pd.DataFrame: The filtered DataFrame.
    #     """
    #     if ticker_data is None:
    #         ticker_data = self.calc_df
        
    #     ticker_data = ticker_data.copy()  # Ensure it's a standalone DataFrame

    #     if not isinstance(ticker_data, pd.DataFrame):
    #         raise ValueError("Ticker data must be a pandas DataFrame.")

    #     # Ensure the index is in datetime format
    #     if not pd.api.types.is_datetime64_any_dtype(ticker_data.index):
    #         ticker_data.index = pd.to_datetime(ticker_data.index)

    #     # Normalize index to remove time components
    #     ticker_data.loc[:, 'Normalized_Date'] = ticker_data.index.normalize()

    #     # Handle timezone awareness
    #     if ticker_data.index.tz is not None:  # If index is timezone-aware
    #         if start_date is None:
    #             start_date = pd.Timestamp.now(tz=ticker_data.index.tz).normalize()
    #         else:
    #             start_date = pd.to_datetime(start_date).tz_localize(ticker_data.index.tz).normalize()
    #     else:  # If index is timezone-naive
    #         if start_date is None:
    #             start_date = pd.Timestamp.today().normalize()
    #         else:
    #             start_date = pd.to_datetime(start_date).normalize()

    #     # Calculate the end date
    #     end_date = start_date + pd.Timedelta(days=days)

    #     # Filter the data based on normalized dates
    #     filtered = ticker_data[
    #         (ticker_data['Normalized_Date'] >= start_date) & (ticker_data['Normalized_Date'] < end_date)
    #     ]

    #     # Drop the temporary normalized column
    #     filtered = filtered.drop(columns=['Normalized_Date'])
    #     # print(filtered)
    #     return filtered
