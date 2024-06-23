from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db, init_db
from schema.competitor_overview import CompetitorOverview
from schema.games_overview import GamesOverview
from schema.tag_overview import TagOverview
from schema.utils import CustomStatus
from schema.year_overview import YearOverview
from services.game_service import GameService

app = FastAPI()
game_service = GameService()


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/ping")
async def get_health() -> CustomStatus:
    """Check API status."""
    return CustomStatus(status_name="pong", status_code="OK")


@app.get("/analyze/competitors")
async def get_competitors_analysis(
    reviews_coeff: int = 30,
    min_reviews: int = 30,
    min_year: int = 2019,
    max_year: int = 2020,
    whitelist_tag_ids: list = None,
    blacklist_tag_ids: list = None,
    db: AsyncSession = Depends(get_db),
) -> CompetitorOverview:
    """Analyze competitors based on some filters."""
    try:
        games = await game_service.read_games(
            session=db,
            min_reviews=min_reviews,
            min_year=min_year,
            max_year=max_year,
            whitelist_tag_ids=whitelist_tag_ids,
            blacklist_tag_ids=blacklist_tag_ids,
        )
        overview = await game_service.analyze_games(
            games=games, reviews_coeff=reviews_coeff
        )
        result = CompetitorOverview(games=games, overview=overview)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/analyze/trends")
async def get_trends_analysis(
    min_reviews: int = 30,
    min_year: int = 2019,
    max_year: int = 2020,
    tag_id: int = 0,
    db: AsyncSession = Depends(get_db),
) -> List[YearOverview]:
    """Check tag trends over years."""
    games = None
    result = [YearOverview(games=None, year=int)]
    return result


@app.get("/analyze/tags")
async def get_tags_analysis(
    reviews_coeff: int = 30,
    min_reviews: int = 30,
    min_year: int = 2019,
    max_year: int = 2020,
    tag_ids: list = None,
    db: AsyncSession = Depends(get_db),
) -> List[TagOverview]:
    """Check tags metrics side-by-side."""
    games = None
    result = [TagOverview(games=games, tag=None)]
    return result
