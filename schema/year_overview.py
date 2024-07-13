from pydantic import BaseModel

from schema.games_overview import GamesOverview
from schema.regression_overview import RegressionOverview


class YearOverview(BaseModel):
    year: int
    overview: GamesOverview
    regression: RegressionOverview = RegressionOverview()
