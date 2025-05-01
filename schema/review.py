from pydantic import BaseModel


class Author(BaseModel):
    playtime_at_review: int


class Review(BaseModel):
    language: str
    review: str
    author: Author
