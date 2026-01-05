import numpy as np
import pandas as pd
from typing import Dict
from config import TRANSACTION_COST, INITIAL_BALANCE

class TradingStrategy:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.positions = pd.DataFrame(index=df.index)
        self._initialize_metrics()
        
    def _initialize_metrics(self):
        """Initialize performance tracking metrics"""
        self.metrics = {
            'equity': [INITIAL_BALANCE],
            'drawdown': [],
            'trades': [],
            'sharpe_ratio': None
        }

    def run_strategy(self, strategy_name: str) -> Dict:
        """Execute trading strategy"""
        signal_func = getattr(self, f'_generate_{strategy_name}_signals')
        signals = signal_func()
        return self._backtest(signals, strategy_name)
        
    def _generate_macd_signals(self) -> pd.Series:
        """MACD crossover signals"""
        self.df['macd_signal'] = 0
        self.df['macd_signal'] = np.where(
            self.df['macd_line'] > self.df['signal_line'], 1, 0
        )
        return self.df['macd_signal'].diff().fillna(0)
    
    def _generate_rsi_signals(self) -> pd.Series:
        """RSI overbought/oversold signals"""
        signals = pd.Series(0, index=self.df.index)
        signals[self.df['rsi'] < 30] = 1   # Oversold buy signal
        signals[self.df['rsi'] > 70] = -1  # Overbought sell signal
        return signals

    def _backtest(self, signals: pd.Series, strategy_name: str) -> Dict:
        """Backtesting engine with transaction costs"""
        position = 0
        entry_price = 0
        trade_history = []
        
        for date, price in self.df['close'].items():
            if signals[date] == 1 and position <= 0:  # Buy signal
                position = INITIAL_BALANCE // (price + TRANSACTION_COST)
                entry_price = price
                trade_history.append({
                    'entry_date': date,
                    'entry_price': entry_price,
                    'position': position
                })
            elif signals[date] == -1 and position > 0:  # Sell signal
                exit_price = price
                pnl = position * (exit_price - entry_price) 
                pnl -= position * TRANSACTION_COST * 2  # Entry + exit fees
                self._update_metrics(pnl, date)
                position = 0
                trade_history[-1].update({
                    'exit_date': date,
                    'exit_price': exit_price,
                    'pnl': pnl
                })
                
        self._calculate_performance_metrics()
        return {
            'metrics': self.metrics,
            'trades': trade_history,
            'equity_curve': self.metrics['equity']
        }

    def _update_metrics(self, pnl: float, date: pd.Timestamp):
        """Update performance metrics"""
        self.metrics['equity'].append(self.metrics['equity'][-1] + pnl)
        peak = max(self.metrics['equity'])
        self.metrics['drawdown'].append(
            (peak - self.metrics['equity'][-1]) / peak
        )

    def _calculate_performance_metrics(self):
        """Calculate final performance metrics"""
        returns = pd.Series(self.metrics['equity']).pct_change().dropna()
        self.metrics['sharpe_ratio'] = (
            returns.mean() / returns.std() * np.sqrt(252)
        )