class DatasetPreparer:
    def __init__(self, results):
        self.results_df = pd.DataFrame(results)
        self.X = None
        self.y = None
        self.scaler = None
        self.encoder = None

    def prepare_dataset(self):
        self.results_df.dropna(subset=['Cumulative_Return'], inplace=True)
        X = self.results_df.drop(['Indicator', 'Cumulative_Return'], axis=1)
        y = self.results_df['Cumulative_Return']

        # Encode indicator names
        self.encoder = LabelEncoder()
        X['Indicator'] = self.encoder.fit_transform(self.results_df['Indicator'])

        # Ensure numeric
        X = X.fillna(0)
        X = X.apply(pd.to_numeric)

        # Store features and target
        self.X = X
        self.y = y
        return X, y

    def split_and_scale(self, test_size=0.2):
        X_values = self.X.values
        y_values = self.y.values

        X_train, X_test, y_train, y_test = train_test_split(
            X_values, y_values, test_size=test_size, random_state=42
        )

        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        return X_train_scaled, X_test_scaled, y_train, y_test
