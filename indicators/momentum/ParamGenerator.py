import inspect
from itertools import product

import numpy as np
import pandas as pd
from typing import List, Dict


class IndParamGenerator:
    def __init__(self, indicators: List[type]):
        self.indicators = indicators

    def generate_param_ranges(self) -> Dict[str, Dict[str, List[int]]]:
        """
        Dynamically generates parameter ranges for all indicators, 
        using the range from 1 to 100 for each parameter.
        :return: Dictionary of parameter ranges for each indicator.
        """
        param_ranges = {}

        for indicator in self.indicators:
            # Get constructor signature
            init_signature = inspect.signature(indicator.__init__)
            # Extract parameter names from the constructor (excluding 'self')
            param_names = [param.name for param in init_signature.parameters.values()][1:]

            # For each indicator, create an entry in the param_ranges
            indicator_name = indicator.__name__
            param_ranges[indicator_name] = {}

            # Assign the range of 1 to 100 for each parameter
            for param in param_names:
                param_ranges[indicator_name][param] = list(range(1, 101))  # Range from 1 to 100

        return param_ranges

    def generate_unique_combinations(self, param_ranges: Dict[str, Dict[str, List[int]]]) -> Dict[str, List[Dict[str, int]]]:
        """
        Generate unique combinations of parameter values for each indicator.
        :return: Dictionary of unique combinations for each indicator.
        """
        unique_combinations = {}

        for indicator_name, params in param_ranges.items():
            # Create a list of parameter combinations using the Cartesian product
            param_combinations = list(product(*params.values()))
            # Convert tuples to dictionaries for better readability
            param_combinations_dict = [dict(zip(params.keys(), comb)) for comb in param_combinations]
            unique_combinations[indicator_name] = param_combinations_dict

        return unique_combinations


# Example data (simulated stock prices)
data = np.random.randn(100) + 100  # 100 data points simulating stock prices

# Initialize the generator with a list of indicators
indicators = [RSI, MACD, BollingerBands]
param_generator = IndicatorParamGenerator(indicators)

# Generate parameter ranges (1 to 100 for each parameter)
param_ranges = param_generator.generate_param_ranges()

# Generate unique combinations of parameters
unique_combinations = param_generator.generate_unique_combinations(param_ranges)

# Calculate indicators for each combination of parameters
indicator_results = {}

for indicator_name, combinations in unique_combinations.items():
    indicator_class = globals()[indicator_name]  # Get the class by name
    results_for_indicator = []
    
    for comb in combinations:
        # Instantiate the indicator class with the parameter combination
        indicator_instance = indicator_class(**comb)
        
        # Calculate the indicator's value
        indicator_value = indicator_instance.calculate(data)
        
        # Store the results with the parameter combination
        results_for_indicator.append({
            'parameters': comb,
            'indicator_value': indicator_value
        })
    
    indicator_results[indicator_name] = results_for_indicator

# Convert the results to a DataFrame for easy viewing
df_results = []
for indicator_name, results in indicator_results.items():
    for result in results:
        result['indicator_name'] = indicator_name
        df_results.append(result)

df = pd.DataFrame(df_results)

# Print the first few rows of the results
print(df.head())