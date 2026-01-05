import pandas as pd
from typing import Dict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class TradingVisualizer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.figsize = (16, 10)
        
    def plot_strategy(self, results: Dict, strategy_name: str):
        """Visualize strategy performance"""
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=self.figsize)
        
        # Price and signals
        ax1.plot(self.df['close'], label='Price')
        self._plot_trades(ax1, results['trades'])
        ax1.set_title(f'{strategy_name} - Trading Signals')
        
        # Equity curve
        ax2.plot(results['metrics']['equity'], label='Equity')
        ax2.set_title('Portfolio Value')
        
        # Drawdown
        ax3.plot(results['metrics']['drawdown'], label='Drawdown', color='red')
        ax3.set_title('Maximum Drawdown')
        
        plt.tight_layout()
        plt.savefig(f'{strategy_name}_performance.png')
        plt.close()
        
    def _plot_trades(self, ax, trades: list):
        """Plot entry/exit markers"""
        for trade in trades:
            if 'exit_date' in trade:
                ax.plot(trade['entry_date'], trade['entry_price'], '^', 
                       markersize=10, color='g')
                ax.plot(trade['exit_date'], trade['exit_price'], 'v', 
                       markersize=10, color='r')