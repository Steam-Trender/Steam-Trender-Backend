from pydantic import BaseModel


class CustomStatus(BaseModel):
    status_name: str
    status_code: str


class Years(BaseModel):
    min_year: int
    max_year: int
