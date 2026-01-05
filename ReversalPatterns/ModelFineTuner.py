# Step 6: ModelFineTuner

import torch

class ModelFineTuner:
    def __init__(self, transformer_model, rl_agent, learning_rate=1e-4, freeze_transformer=True):
        """
        transformer_model: Instance of TransformerSignalGenerator
        rl_agent: Instance of RLTradingAgent
        learning_rate: LR for optimizer
        freeze_transformer: Freeze Transformer encoder during fine-tuning
        """
        self.transformer = transformer_model
        self.rl_agent = rl_agent
        self.optimizer = torch.optim.Adam(self._get_trainable_params(), lr=learning_rate)
        self.criterion = torch.nn.CrossEntropyLoss()

    def _get_trainable_params(self):
        """
        Return parameters to train
        """
        if freeze_transformer:
            for name, param in self.transformer.named_parameters():
                if "classifier" not in name:
                    param.requires_grad = False
        return filter(lambda p: p.requires_grad, self.transformer.parameters())

    def fine_tune_transformer(self, dataloader, epochs=5):
        """
        Fine-tune Transformer classifier head
        dataloader: torch DataLoader with (X, y)
        """
        self.transformer.train()
        for epoch in range(epochs):
            total_loss = 0
            for X_batch, y_batch in dataloader:
                self.optimizer.zero_grad()
                outputs = self.transformer(X_batch)
                loss = self.criterion(outputs, y_batch)
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss:.4f}")

    def fine_tune_rl_agent(self, timesteps=50_000):
        """
        Fine-tune RL agent's policy network on updated environment
        """
        print("Fine-tuning RL agent...")
        self.rl_agent.train(timesteps)
        print("RL agent fine-tuning complete!")

    def save_all(self, transformer_path="transformer_finetuned.pth", rl_path="rl_agent_finetuned.zip"):
        torch.save(self.transformer.state_dict(), transformer_path)
        self.rl_agent.save(rl_path)
        print(f"Saved Transformer to {transformer_path} and RL agent to {rl_path}")

    def load_all(self, transformer_path="transformer_finetuned.pth", rl_path="rl_agent_finetuned.zip"):
        self.transformer.load_state_dict(torch.load(transformer_path))
        self.rl_agent.load(rl_path)
        print(f"Loaded Transformer from {transformer_path} and RL agent from {rl_path}")