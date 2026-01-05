# 1. PatternFeatureExtractor
import pandas as pd

class PatternFeatureExtractor:
    def __init__(self, detectors: list):
        """
        detectors: list of ChartPatternDetector subclasses
        """
        self.detectors = detectors

    def extract(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Run all detectors on data and return pattern features as DataFrame.
        Each column = one pattern, values = 0 (not detected) or 1 (detected).
        """
        features = pd.DataFrame(index=data.index)

        for detector_cls in self.detectors:
            detector = detector_cls(data)
            detections = detector.detect()

            feature_name = detector_cls.__name__
            features[feature_name] = 0  # initialize column

            # Mark detected timestamps
            for result in detections:
                if isinstance(result, dict):
                    ts = result.get('confirm_close', None)
                else:
                    ts = result
                if ts in features.index:
                    features.at[ts, feature_name] = 1

        return features.fillna(0)