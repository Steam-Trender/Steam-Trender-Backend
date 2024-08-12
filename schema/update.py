from datetime import date

from pydantic import BaseModel


class Update(BaseModel):
    id: int
    date: date

    class Config:
        from_attributes = True
