from pydantic import BaseModel

from schema.update import Update


class ServerStatus(BaseModel):
    status_name: str
    status_code: str
    update: Update


class Years(BaseModel):
    min_year: int
    max_year: int
