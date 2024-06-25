from pydantic import BaseModel


class Tag(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True
