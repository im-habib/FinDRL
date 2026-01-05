

if __name__ == '__main__':
    # Initialize the MomentumIndicators class
    momentum = MomentumIndicators(new_data)

    # Calculate all momentum indicators
    mom_new_data = momentum.calculate()

    # Display the updated DataFrame with calculated indicators
    mom_new_data.head()