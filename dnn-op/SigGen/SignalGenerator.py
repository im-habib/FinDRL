class SignalGenerator:
    def __init__(self, df, indicator_name):
        self.df = df
        self.indicator_name = indicator_name

    def generate_signals(self):
        df = self.df.copy()
        df['Signal'] = 0
        try:
            if self.indicator_name in ['sma', 'ema']:
                df['Signal'] = np.where(df['Close'] > df[self.indicator_name.upper()], 1, -1)
            elif self.indicator_name == 'rsi':
                df['Signal'] = np.where(
                    df[self.indicator_name.upper()] < 30, 1,
                    np.where(df[self.indicator_name.upper()] > 70, -1, 0)
                )
            elif self.indicator_name == 'macd':
                macd_line = df.columns[df.columns.str.contains('MACD_')][0]
                signal_line = df.columns[df.columns.str.contains('MACDs_')][0]
                df['Signal'] = np.where(df[macd_line] > df[signal_line], 1, -1)
            elif self.indicator_name == 'bbands':
                lower_band = df.columns[df.columns.str.contains('BBL')][0]
                upper_band = df.columns[df.columns.str.contains('BBU')][0]
                df['Signal'] = np.where(
                    df['Close'] < df[lower_band], 1,
                    np.where(df['Close'] > df[upper_band], -1, 0)
                )
            else:
                df['Signal'] = 0
            return df
        except Exception as e:
            print(f"Error generating signals for {self.indicator_name}: {e}")
            return None
