from pydantic import BaseModel

from schema.update import Update


class ServerStatus(BaseModel):
    status: str
    update: Update


class Years(BaseModel):
    min_year: int
    max_year: int
