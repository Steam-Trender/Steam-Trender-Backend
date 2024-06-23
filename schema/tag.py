from pydantic import BaseModel


class Tag(BaseModel):
    id: int
    title: str
