from typing import List

from pydantic import BaseModel

from schema.game import Game
from schema.games_overview import GamesOverview


class CompetitorOverview(BaseModel):
    games: List[Game]
    overview: GamesOverview
