class ParameterOptimizer:
    def __init__(self, model, scaler, encoder, X_columns):
        self.model = model
        self.scaler = scaler
        self.encoder = encoder
        self.X_columns = X_columns

    def find_optimal_parameters(self, parameter_combinations):
        prediction_data = []
        for combination in parameter_combinations:
            indicator_name = combination['indicator']
            params = combination['params']
            flat_params = {f'{indicator_name}_{k}': v for k, v in params.items()}
            prediction_entry = {'Indicator': indicator_name}
            prediction_entry.update(flat_params)
            prediction_data.append(prediction_entry)

        prediction_df = pd.DataFrame(prediction_data)

        # Handle missing columns
        missing_cols = set(self.X_columns) - set(prediction_df.columns)
        for col in missing_cols:
            prediction_df[col] = 0

        # Ensure column order
        prediction_df = prediction_df[self.X_columns]

        # Encode indicator names
        prediction_df['Indicator'] = self.encoder.transform(prediction_df['Indicator'])

        # Ensure numeric
        prediction_df = prediction_df.fillna(0)
        prediction_df = prediction_df.apply(pd.to_numeric)

        X_full = prediction_df.values
        X_full_scaled = self.scaler.transform(X_full)

        # Predict
        predicted_returns = self.model.predict(X_full_scaled)
        prediction_df['Predicted_Return'] = predicted_returns

        # Find optimal parameters
        optimal_index = prediction_df['Predicted_Return'].idxmax()
        optimal_params = prediction_df.loc[optimal_index]
        return optimal_params
