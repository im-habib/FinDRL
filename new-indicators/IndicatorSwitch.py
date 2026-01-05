import pandas as pd
from indicators import Base

class IndicatorSwitch:
    def __init__(self, data):
        # Convert to DataFrame if necessary and lowercase columns
        if not isinstance(data, pd.DataFrame):
            self.data = pd.DataFrame(data)
        else:
            self.data = data

        self.data.columns = [col.lower() for col in self.data.columns]
        self.indicators: list = []

    def set_indicators(self, indicators):
        """
        Set multiple indicators.
        :param indicators: A list of indicators, each an instance of a class implementing the Indicator interface
        """
        if isinstance(indicators, list):
            for indicator in indicators:
                if not isinstance(indicator, Base):
                    raise TypeError(f"All items in the list must be instances of the Base interface. Found {type(indicator)}")
                else:
                    self.indicators = indicators
                    print("All items in the list is instances of Base indicators")

        else:
            if not isinstance(indicators, Base):
                raise TypeError(f"Expected an instance of the Base interface. Found {type(indicators)}")
            else:
                self.indicators = [indicators]

    def calculate(self):
        """
        Use all the indicators to calculate values on the data sequentially.
        """
        for indicator in self.indicators:

            print(f"indicator: {indicator}")

            self.data = indicator.calculate(self.data)
        return self.data

# class IndicatorSwitch:
    # """
    # Set multiple indicators.
    # :param indicators: A list of indicators, each an instance of a class implementing the Indicator interface
    # """
    # if isinstance(indicators, list):
    #     self.indicators = indicators
    # else:
    #     self.indicators = [indicators]

#     def __init__(self, data):
#         # Convert to DataFrame if necessary and lowercase columns
#         if not isinstance(data, pd.DataFrame):
#             self.data = pd.DataFrame(data)
#         else:
#             self.data = data

#         self.data.columns = [col.lower() for col in self.data.columns]
#         self.indicator: Base = None

#     def set_indicator(self, indicator: Base):
#         """
#         Set the current indicator strategy dynamically.
#         :param indicator: An instance of a class implementing the Indicator interface
#         """
#         self.indicator = indicator

#     def calculate(self):
#         """
#         Use the current indicator to calculate values on the data.
#         """
#         if self.indicator is not None:
#             self.data = self.indicator.calculate(self.data)
#         else:
#             print("No indicator set")
#         return self.data