from pydantic import BaseModel

from schema.games_overview import GamesOverview
from schema.tag import Tag


class TagOverview(BaseModel):
    tag: Tag
    overview: GamesOverview
