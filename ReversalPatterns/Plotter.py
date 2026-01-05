import pandas as pd
import mplfinance as mpf

class PatternPlotter:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df.index = pd.to_datetime(self.df.index)

    def plot_patterns(
        self,
        pattern_points,
        title='Pattern Detection',
        color='r',
        figsize=(18, 10),
        chart_type='candle',
        start_date=None,
        end_date=None,
        linewidth=2,
        padding=20,
        show_volume=True
    ):
        """
        Plot reversal patterns or chart patterns
        pattern_points: List of dicts, lists/tuples, or single timestamps
        """
        df = self.df
        lines, flat_indices = [], []

        for point in pattern_points:
            if isinstance(point, dict):
                dates = [pd.to_datetime(v) for v in point.values()]
            elif isinstance(point, (list, tuple)):
                dates = [pd.to_datetime(p) if not isinstance(p, int) else df.index[p] for p in point]
            elif isinstance(point, pd.Timestamp):
                dates = [point]
            else:
                continue

            line = []
            for date in dates:
                if date not in df.index:
                    nearest = df.index.get_indexer([date], method='nearest')[0]
                    date = df.index[nearest]
                idx = df.index.get_loc(date)
                flat_indices.append(idx)
                line.append((date, df['close'].iloc[idx]))
            if len(line) >= 2:
                lines.append(line)

        df_view = self._get_view_df(flat_indices, padding, start_date, end_date)

        mpf.plot(
            df_view,
            type=chart_type,
            volume=show_volume,
            style='yahoo',
            title=title,
            alines=dict(alines=lines, colors=color, linewidths=linewidth),
            warn_too_much_data=len(df_view) + 10,
            figsize=figsize,
        )

    def plot_signals(
        self,
        action_log,
        title='RL Agent Signals',
        figsize=(18, 10),
        chart_type='candle',
        show_volume=True
    ):
        """
        Plot RL Agent's Buy/Sell/Hold signals
        action_log: DataFrame with ['step', 'action', 'price']
        """
        df = self.df
        markers = []
        signal_colors = {0: 'gray', 1: 'green', 2: 'red'}
        signal_labels = {0: 'Hold', 1: 'Buy', 2: 'Sell'}

        for _, row in action_log.iterrows():
            idx = row['step']
            if idx < len(df):
                date = df.index[idx]
                price = row['price']
                action = row['action']
                markers.append(dict(x=date, y=price, marker='^' if action == 1 else 'v',
                                    color=signal_colors[action], label=signal_labels[action]))

        mpf.plot(
            df,
            type=chart_type,
            volume=show_volume,
            style='yahoo',
            title=title,
            addplot=[mpf.make_addplot([None] * len(df), scatter=markers)],
            figsize=figsize,
        )

    def _get_view_df(self, indices, padding, start_date, end_date):
        if start_date and end_date:
            return self.df.loc[start_date:end_date]
        elif indices:
            min_idx = max(min(indices) - padding, 0)
            max_idx = min(max(indices) + padding, len(self.df) - 1)
            return self.df.iloc[min_idx:max_idx + 1]
        else:
            return self.df.iloc[-300:]