from pydantic import BaseModel


class Post(BaseModel):
    id: int
    url: str
    title: str
    image: str
    description: str
