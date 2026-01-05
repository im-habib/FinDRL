import inspect
import itertools

def analyze_function(func):
    """
    Analyzes the function to extract parameter names and default values.

    Args:
    - func (callable): The function to analyze.

    Returns:
    - dict: A dictionary with parameter names and their default values.
    """
    signature = inspect.signature(func)
    parameters = {
        param.name: param.default
        for param in signature.parameters.values()
        if param.default is not param.empty
    }
    return parameters

def generate_random_parameters(base_values, min_value=1, max_value=200):
    """
    Generates the maximum number of unique parameter sets, ensuring each generated value 
    is greater than its base value.

    Args:
    - base_values (dict): A dictionary with base parameter names and their base values.
    - min_value (int): The minimum value for the parameters.
    - max_value (int): The maximum value for the parameters.

    Returns:
    - List[dict]: A list of dictionaries containing the parameters.
    """
    if len(base_values) == 1:
        # Only one parameter
        key, base_value = next(iter(base_values.items()))
        effective_min_value = max(base_value + 1, min_value)
        possible_values = list(range(effective_min_value, max_value + 1))
        
        if not possible_values:
            raise ValueError("No possible values to generate.")
        
        return [{key: value} for value in possible_values]
    else:
        # Multiple parameters
        possible_values_dict = {
            key: list(range(max(base_value + 1, min_value), max_value + 1))
            for key, base_value in base_values.items()
        }
        
        # Compute the Cartesian product of all possible values
        all_keys = list(possible_values_dict.keys())
        all_combinations = itertools.product(*possible_values_dict.values())
        
        return [dict(zip(all_keys, combination)) for combination in all_combinations]


def extract_parameters(parameters):
    extracted_params = {}

    for indicator in parameters:
        for key, value in indicator.items():
            extracted_params[key] = []
            for param_set in value:
                extracted_params[key].append(param_set)

    return extracted_params

def extract_list_to_key_value(pairs):
    for key, value in pairs.items():
        return key, value
    return pairs

def hoc_print(data=None, reasone=''):
    print(f"-----Reasone: {reasone}------")
  
    print(data)

    print(f"\n\n")


# # Generate random values for parameters within the specified range
# def generate_random_value(min_value=1, max_value=200):
#     return random.uniform(min_value, max_value)  # Example: Random float value between min_val and max_val

# # Create a list of parameter sets with random values
# def create_parameter_sets(params, num_sets, min_value=1, max_value=200):
#     parameter_sets = []
#     for _ in range(num_sets):
#         param_dict = {param_name: generate_random_value(min_value, max_value) for param_name, _ in params}
#         parameter_sets.append(param_dict)
#     return parameter_sets

# # Number of parameter sets to create
# num_sets = 2000
# # Min and max values for random generation
# min_val = 1
# max_val = 200

# # Generate the parameter sets
# random_parameter_sets = create_parameter_sets(params, num_sets, min_val, max_val)

# # Print the first 5 parameter sets to verify
# for i, param_set in enumerate(random_parameter_sets[:5]):
#     print(f"Parameter Set {i+1}: {param_set}")


# def apply_parameters(func, data, parameters_list):
#     """
#     Applies the generated parameters to the function.

#     Args:
#     - func (callable): The function to apply parameters to.
#     - data: The data to pass to the function.
#     - parameters_list (list): A list of parameter dictionaries.

#     Returns:
#     - list: A list of function results.
#     """
#     results = []
#     for params in parameters_list:
#         result = func(data, **params)
#         results.append(result)
#     return results

# # Example indicator function
# class Indicator:
#     def __init__(self, data):
#         self.data = data
    
#     def relative_strength_index(self, period):
#         # Dummy implementation for example purposes
#         return self.data.rolling(window=period).mean()
    
#     def connors_rsi(self, period_rsi=3, period_streak=2, period_rank=100):
#         rsi = self.relative_strength_index(data.close, period=period_rsi)
#         streak = data.close.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)).rolling(window=period_streak).sum()
#         up_down_rsi = self.relative_strength_index(streak, period=period_streak)
#         pct_rank = data.close.rank(pct=True) * 100
#         connors_rsi = (rsi + up_down_rsi + pct_rank) / 3
#         return connors_rsi

# # Dummy data for example purposes
# import pandas as pd
# data = pd.DataFrame({'close': [random.uniform(100, 200) for _ in range(100)]})

# indicator = Indicator(data)

# # Analyze the function to get base parameter values
# base_values = analyze_function(indicator.relative_strength_index)

# # Generate 100 sets of random parameters
# generated_parameters = generate_random_parameters(base_values, num_parameters=100, min_value=1, max_value=50)

# # Apply the generated parameters to the indicator function
# results = apply_parameters(indicator.connors_rsi, data, generated_parameters)

# # Display the generated parameters and results
# for index, (params, result) in enumerate(zip(generated_parameters, results)):
#     print(f"Set {index + 1}: {params}")
#     print(result)
