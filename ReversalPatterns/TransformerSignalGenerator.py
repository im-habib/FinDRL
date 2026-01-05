# 3. TransformerSignalGenerator

import torch
import torch.nn as nn

class TransformerSignalGenerator(nn.Module):
    def __init__(self, input_dim, d_model=128, nhead=8, num_layers=3, num_classes=3, dropout=0.1):
        """
        input_dim: Number of features from MultiTimeframeDataset
        d_model: Embedding dimension for Transformer
        nhead: Number of attention heads
        num_layers: Number of Transformer encoder layers
        num_classes: Output classes (Buy, Hold, Sell)
        dropout: Dropout rate
        """
        super(TransformerSignalGenerator, self).__init__()

        # Input embedding layer
        self.embedding = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)

        # Transformer Encoder
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=512, dropout=dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)

        # Classifier head
        self.classifier = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes),
            nn.Softmax(dim=-1)
        )

    def forward(self, x):
        """
        x: Tensor of shape (batch_size, sequence_length, input_dim)
        """
        x = self.embedding(x)
        x = self.pos_encoder(x)
        x = self.transformer_encoder(x)
        # Global average pooling over sequence length
        x = torch.mean(x, dim=1)
        return self.classifier(x)


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        # Create constant 'pe' matrix with values dependent on position and i
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-torch.log(torch.tensor(10000.0)) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)  # apply sin to even indices in the array
        pe[:, 1::2] = torch.cos(position * div_term)  # apply cos to odd indices in the array
        pe = pe.unsqueeze(0)  # Add batch dimension
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        Add positional encoding to input tensor x.
        x: Tensor of shape (batch_size, sequence_length, d_model)
        """
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)