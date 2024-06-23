from pydantic import BaseModel

from schema.games_overview import GamesOverview


class YearOverview(BaseModel):
    year: int
    overview: GamesOverview
