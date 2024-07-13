from typing import List

import numpy as np

from schema.year_overview import YearOverview


class PredictionFeature:
    def __init__(self, feature: str, precision: int):
        self.feature = feature
        self.precision = precision


class PredictionService:
    def __init__(self):
        self.median_owners_feature = PredictionFeature("median_owners", 0)
        self.median_reviews_feature = PredictionFeature("median_reviews", 0)
        self.median_price_feature = PredictionFeature("median_price", 2)

    @staticmethod
    def perform_regression(x: List[int], y: List[float]) -> (float, float):
        """Perform simple 1d linear regression"""
        y = np.array(y)
        x = np.array(x)
        k, b = np.polyfit(x, y, 1)
        return k, b

    @staticmethod
    def predict(x: int, k: float, b: float) -> float:
        """Predict 1d linear regression value"""
        return k * x + b

    def get_trended_years(self, years: List[YearOverview]) -> List[YearOverview]:
        """Trend all features"""

        def handle_feature(x: List[int], feature: PredictionFeature):
            values = [getattr(y.overview, feature.feature) for y in years]
            k, b = self.perform_regression(years_nums, values)
            for year in years:
                prediction = self.predict(year.year, k, b)
                if feature.precision == 0:
                    prediction = int(prediction)
                else:
                    prediction = np.round(prediction, feature.precision)
                setattr(year.regression, feature.feature, prediction)

        years_nums = [y.year for y in years]

        for feature in [
            self.median_price_feature,
            self.median_owners_feature,
            self.median_reviews_feature,
        ]:
            handle_feature(x=years_nums, feature=feature)

        return years


prediction_service = PredictionService()
