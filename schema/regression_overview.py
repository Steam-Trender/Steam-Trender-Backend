from pydantic import BaseModel


class RegressionOverview(BaseModel):
    median_reviews: int = 0
    median_owners: int = 0
    median_price: float = 0.0
    median_revenue: int = 0
