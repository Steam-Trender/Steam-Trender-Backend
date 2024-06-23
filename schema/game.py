from typing import List

from pydantic import BaseModel

from schema.tag import Tag


class Game(BaseModel):
    id: int
    title: str
    reviews: int
    price: float
    tags: List[Tag]
