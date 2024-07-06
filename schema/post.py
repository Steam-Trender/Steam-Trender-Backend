from pydantic import BaseModel


class Post(BaseModel):
    id: int
    link: str
    title: str
    image: str
    description: str

    class Config:
        from_attributes = True
