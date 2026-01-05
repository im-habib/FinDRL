class NeuralNetworkModel:
    def __init__(self, input_dim):
        self.model = Sequential()
        self.model.add(Dense(64, input_dim=input_dim, activation='relu'))
        self.model.add(Dense(32, activation='relu'))
        self.model.add(Dense(1, activation='linear'))
        self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=8):
        self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size
        )

    def predict(self, X):
        return self.model.predict(X)
