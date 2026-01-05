class PerformanceEvaluator:
    def __init__(self, df):
        self.df = df

    def calculate_performance(self):
        df = self.df.copy()
        df['Return'] = df['Close'].pct_change()
        df['Strategy_Return'] = df['Return'] * df['Signal'].shift(1)
        cumulative_return = (1 + df['Strategy_Return']).cumprod().iloc[-1]
        return cumulative_return
