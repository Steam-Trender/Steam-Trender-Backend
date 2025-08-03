from datetime import date
from typing import List

from pydantic import BaseModel, Field

from schema.tag import Tag


class Game(BaseModel):
    id: int
    appid: int
    title: str
    canonized_title: str
    reviews: int
    reviews_score: float
    release_date: date
    price: float
    tags: List[Tag] = Field(alias="tags_sorted")
    owners: int
    revenue: float

    class Config:
        from_attributes = True
