import torch
import pandas as pd
from torch.utils.data import DataLoader, TensorDataset

# Import all classes from previous steps
# PatternFeatureExtractor, MultiTimeframeDataset, TransformerSignalGenerator,
# TradingEnvironment, RLTradingAgent, ModelFineTuner

# === Step 1: Load Multi-Timeframe Data ===
from yfinance import download
timeframe_data = {
    "1m": download("AAPL", period="5d", interval="1m").reset_index(),
    "5m": download("AAPL", period="1mo", interval="5m").reset_index(),
    "1h": download("AAPL", period="3mo", interval="1h").reset_index()
}

# === Step 2: Setup Pattern Detectors ===
detectors = [
    DoubleBottomDetector, HeadAndShouldersDetector, BullishEngulfingDetector,
    MorningStarDetector, HammerDetector, PiercingLineDetector, RoundedBottomDetector, FallingWedgeDetector, InverseHeadAndShouldersDetector, TripleBottomDetector,
    DoubleTopDetector, ShootingStarDetector, BearishEngulfingDetector, TripleTopDetector, RisingWedgeDetector, EveningStarDetector, DarkCloudCoverDetector, RoundedTopDetector, 
]

tor = PatternFeatureExtractor(detectors)

# === Step 3: Build Multi-Timeframe Dataset ===
dataset_builder = MultiTimeframeDataset(timeframe_data, extractor)
multi_tf_data = dataset_builder.build()

# === Step 4: Create Transformer Model ===
input_dim = multi_tf_data.shape[1]
transformer_model = TransformerSignalGenerator(input_dim=input_dim)

# === Step 5: Create Trading Environment ===
env = TradingEnvironment(multi_tf_data)

# === Step 6: Create RL Agent ===
rl_agent = RLTradingAgent(env, algorithm="PPO")

# === Step 7: Prepare Dataloader for Transformer Pretraining (Optional) ===
features_tensor = torch.tensor(multi_tf_data.values, dtype=torch.float32)
labels_tensor = torch.randint(0, 3, (features_tensor.size(0),))  # Dummy labels for pretraining
dataset = TensorDataset(features_tensor, labels_tensor)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Pretrain Transformer (Optional)
optimizer = torch.optim.Adam(transformer_model.parameters(), lr=1e-4)
criterion = torch.nn.CrossEntropyLoss()
transformer_model.train()
for epoch in range(3):  # Few epochs for pretraining
    total_loss = 0
    for X_batch, y_batch in dataloader:
        optimizer.zero_grad()
        outputs = transformer_model(X_batch.unsqueeze(1))  # Add sequence dim
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Pretraining Epoch {epoch+1}, Loss: {total_loss:.4f}")

# === Step 8: Train RL Agent ===
rl_agent.train(timesteps=100_000)

# === Step 9: Save Models ===
torch.save(transformer_model.state_dict(), "transformer_model.pth")
rl_agent.save("rl_trading_agent.zip")

print("✅ Training complete! Models saved.")