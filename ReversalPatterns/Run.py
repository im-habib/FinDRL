import torch

# === Load Saved Models ===
transformer_model.load_state_dict(torch.load("transformer_model.pth"))
rl_agent.load("rl_trading_agent.zip")

# === Setup for Live Data ===
live_data = download("AAPL", period="1d", interval="1m").reset_index()
live_features = extractor.extract(live_data)
live_combined = pd.concat([live_data[['open', 'high', 'low', 'close', 'volume']], live_features], axis=1)
live_tensor = torch.tensor(live_combined.values, dtype=torch.float32).unsqueeze(0)  # Batch dim

# === Predict Signals ===
transformer_model.eval()
with torch.no_grad():
    signal_probs = transformer_model(live_tensor)
    predicted_signal = torch.argmax(signal_probs, dim=1).item()

signal_map = {0: "Hold", 1: "Buy", 2: "Sell"}
print(f"📢 Predicted Action: {signal_map[predicted_signal]}")