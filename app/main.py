from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db, init_db
from schema.games_overview import GamesOverview
from schema.utils import CustomStatus
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
async def get_competitors(
    min_reviews: int = 30,
    min_year: int = 2019,
    max_year: int = 2020,
    whitelist_tag_ids: list = None,
    blacklist_tag_ids: list = None,
    db: AsyncSession = Depends(get_db),
) -> GamesOverview:
    try:
        games = await game_service.read_games(
            db, min_reviews, min_year, max_year, whitelist_tag_ids, blacklist_tag_ids
        )
        overview = await game_service.analyze_games(games, 30)
        return overview
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
