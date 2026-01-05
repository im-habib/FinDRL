import pandas as pd

# 2. MultiTimeframeDataset

class MultiTimeframeDataset:
    def __init__(self, timeframe_data: dict, extractor: PatternFeatureExtractor):
        """
        timeframe_data: dict like {'1m': pd.DataFrame, '5m': pd.DataFrame, ...}
        extractor: PatternFeatureExtractor instance
        """
        self.timeframe_data = timeframe_data
        self.extractor = extractor

    def build(self) -> pd.DataFrame:
        """
        Returns combined DataFrame: OHLCV + pattern features from all timeframes
        """
        all_features = []

        for tf, df in self.timeframe_data.items():
            print(f"Processing timeframe: {tf}")
            pattern_features = self.extractor.extract(df)
            ohlcv_features = df[['open', 'high', 'low', 'close', 'volume']]

            combined = pd.concat([ohlcv_features, pattern_features], axis=1)
            combined.columns = [f"{tf}_{col}" for col in combined.columns]  # Prefix columns
            all_features.append(combined)

        # Align timeframes by intersection of indexes
        merged = pd.concat(all_features, axis=1).dropna()
        print("Multi-timeframe dataset built successfully.")
        return merged