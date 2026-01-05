from typing import Any, Callable
from abc import ABC, abstractmethod

class Condition(ABC):
    @abstractmethod
    def evaluate_buy(self, indicator_values: Any):
        pass

    @abstractmethod
    def evaluate_sell(self, indicator_values: Any):
        pass

class BuyAndSellCondition(Condition):
    def __init__(self, buy_logic: Callable, sell_logic: Callable):
        self.buy_logic = buy_logic
        self.sell_logic = sell_logic
    
    def evaluate_buy(self, indicator_values):
        return self.buy_logic(indicator_values)
    
    def evaluate_sell(self, indicator_values):
        return self.sell_logic(indicator_values)
