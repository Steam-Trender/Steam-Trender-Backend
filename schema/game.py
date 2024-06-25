from datetime import date
from typing import List

from pydantic import BaseModel

from schema.tag import Tag


class Game(BaseModel):
    id: int
    appid: int
    title: str
    reviews: int
    reviews_score: float
    release_date: date
    price: float
    tags: List[Tag]

    class Config:
        orm_mode = True
