import pandas as pd
import pandas_ta as ta
import plotly.offline as pyo
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from mplfinance.original_flavor import candlestick_ohlc


pyo.init_notebook_mode(connected=True)
pd.options.plotting.backend = 'plotly'

class TIBAStockPlot:
    pass

class StockPlot:
    def __init__(self, data, indicators={}):
        """Initialize with stock data."""
        self.df = data
        self.ticker_data = None
        self.indicators = indicators
        self.tickers = self.df['ticker'].unique()

    def _filter_data(self, ticker_data, target_date=None, days=5):
        """
        Filter the data to include rows starting from a specific date (YYYY-MM-DD).
        Handles timezone-aware datetime indices.
        Args:
            ticker_data (pd.DataFrame): The data for a specific ticker.
            target_date (str or None): The target date in 'YYYY-MM-DD' format.
            If None, the latest data will be used.
            days (int): The total number of days to include in the filtered data.
        Returns:
            pd.DataFrame: Filtered data for the given date or range.
        """
        # Ensure the index is in datetime format
        if not pd.api.types.is_datetime64_any_dtype(ticker_data.index):
            ticker_data.index = pd.to_datetime(ticker_data.index)
    
        # Determine if the index is timezone-aware
        is_timezone_aware = ticker_data.index.tz is not None
    
        # Convert target_date to datetime
        if target_date:
            start_date = pd.to_datetime(target_date).normalize()
            # Make start_date timezone-aware if necessary
            if is_timezone_aware:
                start_date = start_date.tz_localize(ticker_data.index.tz)
        else:
            # Default to the latest data if target_date is not provided
            start_date = ticker_data.index.max() - pd.Timedelta(days=days)
            if is_timezone_aware and start_date.tz is None:
                start_date = start_date.tz_localize(ticker_data.index.tz)
    
        # Calculate the end date
        end_date = start_date + pd.Timedelta(days=days)
    
        # Filter the DataFrame
        filtered_df = ticker_data.loc[(ticker_data.index >= start_date) & (ticker_data.index < end_date)]
    
        if filtered_df.empty:
            print("Warning: No data available in the specified range.")
            
        return filtered_df

        
    def _add_custom_trace(self, fig, trace={}):
        """
        Add a trace to the figure in the specified subplot (row, col).
        Handles primary and secondary y-axes dynamically.
        """
        row = trace.get("row", 1)
        col = trace.get("col", 1)
        secondary_y = trace.get("secondary_y", False)
        obj = go.Scatter(
            x=self.ticker_data.index,
            y=self.ticker_data["close"],
            marker_color="green",
            name="N/A",
            # mode="line",
            # line=dict(dash="dot"),
        )
        name = trace.get("name", obj)
        
        fig.add_trace(name, row=row, col=col, secondary_y=secondary_y)
    
    def _smooth_data(self, data, method='sma', window=5):
        """
        Smooth the input data using the specified method.
        Supported methods: 'sma' (Simple Moving Average), 'ema' (Exponential Moving Average).
        Args:
            data (pd.Series): The input data to be smoothed.
            method (str): The smoothing method to use ('sma' or 'ema').
            window (int): The window size for smoothing.
        Returns:
            pd.Series: The smoothed data.
        """
        # print(data)
        if method == 'sma':  # Simple Moving Average
            return ta.sma(data, length=window)
        elif method == 'ema':  # Exponential Moving Average
            return ta.ema(data, length=window)
        else:
            raise ValueError("Unsupported smoothing method. Choose 'sma' or 'ema'.")

    def _add_indicator_traces(self, fig, ticker_data, indicators):
        """
        Add indicators dynamically to the specified figure using dictionary-based trace definitions.
        Supports both 'scatter' (lines) and 'bar' (histogram) trace types,
        and dynamically assigns traces to primary or secondary y-axis.
        """
        for indicator, details in indicators.items():
            color = details.get('color', 'green')
            column = details.get('column')
            mode = details.get('mode', 'lines')  # Default to lines
            dash = details.get('dash', None)  # Default to no dash style
            trace_type = details.get('type', 'scatter').lower()  # Default to scatter
            secondary_y = details.get('secondary_y', False)  # Default to primary y-axis
            smooth = details.get('smooth', True)  # Default to primary y-axis
            smoothing_window = details.get('smoothing_window', 5)  # Default to primary y-axis
            smoothing_method = details.get('smoothing_method', 'ema')  # Default to primary y-axis

            # Validate column
            if column not in ticker_data.columns:
                print(f"Warning: Column '{column}' for indicator '{indicator}' not found.")
                continue
                
            # Smooth data if specified
            data = (
                self._smooth_data(ticker_data[column], method=smoothing_method, window=smoothing_window) if smooth
                else ticker_data[column]
            )
            
            # Create trace dictionary
            if trace_type == 'bar':
                trace = {
                    "row": 3,
                    "col": 1,
                    "secondary_y": secondary_y,
                    "name": go.Bar(
                        x=ticker_data.index,
                        y=data,
                        marker_color=color,
                        name=indicator,
                        showlegend=True,
                    ),
                }
            elif trace_type == 'scatter':
                trace = {
                    "row": 3,
                    "col": 1,
                    "secondary_y": secondary_y,
                    "name": go.Scatter(
                        x=ticker_data.index,
                        y=data,
                        marker_color=color,
                        name=indicator,
                        mode=mode,  # Use valid mode ('lines', 'markers', etc.) line=dict(dash=dash, color=color),
                        line=dict(dash=dash, color=color) if dash else None,  # Apply dash style if specified
                    ),
                }
            else:
                print(f"Warning: Unsupported trace type '{trace_type}' for indicator '{indicator}'")
                continue
            
            # Add the trace to the second row, first column, with optional secondary y-axis
            self._add_custom_trace(fig, trace)

    def plot_data(self, plot_field="close", title="", start_date=None, days=None):
        """Plot the stock data with candlesticks and indicators for each ticker in separate plots."""
        ndf = self.df.copy()
        ndf.index.name = "datetime"

        # Loop through tickers and create plots
        for i, ticker in enumerate(self.tickers):
            ticker_data = ndf[ndf['ticker'] == ticker]
            ticker_data = ticker_data.sort_index()
            if days:
                ticker_data = self._filter_data(ticker_data, start_date, days)
                self.ticker_data = ticker_data
                # print(ticker_data.tail(5))
                
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True, 
                vertical_spacing=0.03, 
                row_heights=[0.3, 0.1, 0.6],
                specs=[
                    [{"secondary_y": False}],
                    [{"secondary_y": False}],
                    [{"secondary_y": True}]
                ]
            )

            # Create candlestick trace
            trace = {
                "row" : 1,
                "col" : 1,
                "name": go.Candlestick(
                    x=ticker_data.index, 
                    open=ticker_data['open'], 
                    high=ticker_data['high'], 
                    low=ticker_data['low'], 
                    close=ticker_data['close'], 
                    name=ticker,
                )
            }
            
            self._add_custom_trace(fig, trace=trace)

            # Add additional indicator traces (e.g., RSI, SMA)
            self._add_indicator_traces(fig, ticker_data, self.indicators)

            # Add volume traces (data["Volume"])
            volume =  {
                "row" : 2,
                "col" : 1,
                "secondary_y" : False,
                "name": go.Bar(
                    name="Volume",
                    showlegend=True,                
                    x=ticker_data.index, 
                    y=ticker_data['volume'],
                    marker=dict(color="green"),
                    
                ),
            }
                        
            self._add_custom_trace(fig, trace=volume)
            
            # Update layout for better display
            fig.update_layout(
                title=f"OHLC Candlesticks Chart - {ticker}",
                xaxis=dict(
                    tickfont_size=12,
                    titlefont_size=14,
                    # title="Date",
                    # showgrid=True,
                    # zeroline=True,
                    # showline=True,
                    # rangeslider=dict(visible=True),  # Enable range slider for navigation
                    # autorange=True,  # Automatically adjust to fit the data
                    # side="left"
                ),
                yaxis=dict(
                    side="left",
                    title="Price",
                    titlefont_size=14,
                    tickfont_size=12,
                    # showgrid=True,
                    zeroline=True,
                    # showline=True,
                    # autorange=True,  # Automatically adjust to fit the data
                ),
                yaxis2=dict(
                    side="left",
                    title="Volume", 
                    # showgrid=False
                ),
                yaxis3=dict(
                    side="left",
                    title="Indicators",
                    titlefont_size=14,
                    tickfont_size=12,
                    # showgrid=True,
                    zeroline=True,
                    # showline=True,
                    # autorange=True,  # Automatically adjust to fit the data
                ),
                height=900,
                autosize=True,
                showlegend=True,
                template="plotly_dark",
                paper_bgcolor="LightSteelBlue",
                margin=dict(l=50, r=50, t=70, b=30),
            )

            fig.update(layout_xaxis_rangeslider_visible=False)
            fig.show()


class StockPlot2:
    def __init__(self, data, indicators={}):
        self.df = data
        self.tickers = self.df['Ticker'].unique()
        self.indicators = indicators

    def _filter_data(self, ticker_data, target_date=None, days=5):
        """Filter the data to include rows starting from a specific date."""
        if not pd.api.types.is_datetime64_any_dtype(ticker_data.index):
            ticker_data.index = pd.to_datetime(ticker_data.index)
        if target_date:
            start_date = pd.to_datetime(target_date).normalize()
        else:
            start_date = ticker_data.index.max() - pd.Timedelta(days=days)
        end_date = start_date + pd.Timedelta(days=days)
        return ticker_data.loc[(ticker_data.index >= start_date) & (ticker_data.index < end_date)]

    def plot_data(self, title="", start_date=None, days=None):
        """Plot the stock data with candlestick and indicators."""
        ndf = self.df.copy()
        ndf.index.name = "Datetime"

        for ticker in self.tickers:
            ticker_data = ndf[ndf['Ticker'] == ticker].sort_index()
            if days:
                ticker_data = self._filter_data(ticker_data, start_date, days)

            # Convert date index to numerical format for candlestick
            ohlc = ticker_data.reset_index()
            ohlc['Datetime'] = mdates.date2num(ohlc['Datetime'])
            ohlc = ohlc[['Datetime', 'Open', 'High', 'Low', 'Close']]

            # Create subplots
            fig, axs = plt.subplots(
                nrows=3, ncols=1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1, 2]}
            )
            fig.suptitle(f"{ticker} - {title}", fontsize=16)

            # Plot candlestick chart
            ax1 = axs[0]
            candlestick_ohlc(ax1, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=0.8)
            ax1.set_title("Candlestick Chart")
            ax1.xaxis_date()
            ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            ax1.grid(True)

            # Plot volume
            ax2 = axs[1]
            ax2.bar(ticker_data.index, ticker_data['Volume'], color='blue', alpha=0.6)
            ax2.set_title("Volume")
            ax2.grid(True)

            # Plot indicators
            ax3 = axs[2]
            for indicator, details in self.indicators.items():
                column = details.get('column')
                color = details.get('color', 'blue')
                smooth = details.get('smooth', True)
                smoothing_method = details.get('smoothing_method', 'sma')
                smoothing_window = details.get('smoothing_window', 5)

                if column not in ticker_data.columns:
                    print(f"Warning: Column '{column}' for indicator '{indicator}' not found.")
                    continue

                # Smooth data if specified
                data = (
                    ta.sma(ticker_data[column], length=smoothing_window)
                    if smoothing_method == 'sma' else ta.ema(ticker_data[column], length=smoothing_window)
                ) if smooth else ticker_data[column]

                ax3.plot(ticker_data.index, data, label=indicator, color=color)

            ax3.set_title("Indicators")
            ax3.grid(True)
            ax3.legend()

            plt.tight_layout(rect=[0, 0, 1, 0.95])
            plt.show()
