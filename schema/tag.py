from pydantic import BaseModel


class Tag(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True
