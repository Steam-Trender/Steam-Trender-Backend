from pydantic import BaseModel


class CustomStatus(BaseModel):
    status_name: str
    status_code: str
