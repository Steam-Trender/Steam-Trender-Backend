from typing import List

import numpy as np

from schema.year_overview import YearOverview


class PredictionFeature:
    def __init__(self, feature: str, precision: int):
        self.feature = feature
        self.precision = precision

    def get_values(self, years: List[YearOverview]) -> List[float]:
        values = [getattr(y.overview, self.feature) for y in years]
        return values


class PredictionRevenueFeature(PredictionFeature):
    def __init__(self, feature: str, precision: int, agg: float):
        super().__init__(feature, precision)
        self.agg = agg

    def get_values(self, years: List[YearOverview]) -> List[float]:
        values = [
            next((rev.value for rev in y.overview.revenue if rev.agg == self.agg), 0)
            for y in years
        ]
        return values


class PredictionService:
    def __init__(self):
        median_owners_feature = PredictionFeature("median_owners", 0)
        median_reviews_feature = PredictionFeature("median_reviews", 0)
        median_price_feature = PredictionFeature("median_price", 2)
        median_revenue_feature = PredictionRevenueFeature("median_revenue", 0, 0.5)
        self.prediction_features = [
            median_owners_feature,
            median_reviews_feature,
            median_price_feature,
            median_revenue_feature,
        ]

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

        def get_feature_prediction(
            x: List[int], y: List[float], feature: PredictionFeature
        ) -> None:
            k, b = self.perform_regression(x, y)
            for year in years:
                prediction = self.predict(year.year, k, b)
                if feature.precision == 0:
                    prediction = int(prediction)
                else:
                    prediction = np.round(prediction, feature.precision)
                setattr(year.regression, feature.feature, prediction)

        years_nums = [y.year for y in years]

        for prediction_feature in self.prediction_features:
            values = prediction_feature.get_values(years)
            get_feature_prediction(x=years_nums, y=values, feature=prediction_feature)

        return years


prediction_service = PredictionService()
