from typing import List

from pydantic import BaseModel

from schema.revenue import Revenue


class GamesOverview(BaseModel):
    total_games: int = 0
    median_reviews: int = 0
    median_owners: int = 0
    median_price: float = 0.0
    revenue_total: int = 0
    revenue: List[Revenue] = []
