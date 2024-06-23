from pydantic import BaseModel


class GamesOverview(BaseModel):
    total_games: int
    median_reviews: float = 0.0
    median_owners: float = 0.0
    median_price: float = 0.0
    median_revenue: float = 0.0
