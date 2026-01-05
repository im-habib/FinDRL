from typing import Any, Callable
from backtesting import Strategy

from app.parameters.Parameters import hoc_print

class DynamicStrategy(Strategy):
    indicator_name: str = ""
    buy_signal: Callable = None
    sell_signal: Callable = None
    indicator_values: Any = None

    def init(self):
        self.indicator_values = self.indicator_values
        # self.indicator_values = self.I(lambda: self.indicator_values)
    
    def next(self):
        # hoc_print(self.buy_signal, 'self.buy_signal')
        # hoc_print(self.sell_signal, 'self.sell_signal')
        # hoc_print(self.indicator_values, 'Indicator values in DynamicStrategy')

        if self.buy_signal and self.buy_signal(self.indicator_values):
            self.buy()
        if self.sell_signal and self.sell_signal(self.indicator_values):
            self.position.close()

