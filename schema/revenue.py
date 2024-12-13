from pydantic import BaseModel


class Revenue(BaseModel):
    agg: float
    value: int
