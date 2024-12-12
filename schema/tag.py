from pydantic import BaseModel


class Tag(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class ExtendedTag(Tag):
    games_count: int
