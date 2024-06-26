from typing import List

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db, init_db
from models.game import Game
from models.tag import Tag
from schema.competitor_overview import CompetitorOverview
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
    whitelist_tag_ids: List[int] = Query(None),
    blacklist_tag_ids: List[int] = Query(None),
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
    results = []
    whitelist_tag_ids = [tag_id]
    for year in range(min_year, max_year + 1, 1):
        games = await game_service.read_games(
            session=db,
            min_reviews=min_reviews,
            min_year=year,
            max_year=year,
            whitelist_tag_ids=whitelist_tag_ids,
            blacklist_tag_ids=None,
        )
        overview = await game_service.analyze_games(games=games, reviews_coeff=30)
        year_overview = YearOverview(year=year, overview=overview)
        results.append(year_overview)
    return results


@app.get("/analyze/tags")
async def get_tags_analysis(
    reviews_coeff: int = 30,
    min_reviews: int = 30,
    min_year: int = 2019,
    max_year: int = 2020,
    tag_ids: List[int] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[TagOverview]:
    """Check tags metrics side-by-side."""
    results = []
    for tag in tag_ids:
        whitelist_tag_ids = [tag]
        games = await game_service.read_games(
            session=db,
            min_reviews=min_reviews,
            min_year=min_year,
            max_year=max_year,
            whitelist_tag_ids=whitelist_tag_ids,
            blacklist_tag_ids=None,
        )
        overview = await game_service.analyze_games(
            games=games, reviews_coeff=reviews_coeff
        )
        tag_overview = TagOverview(tag=tag, overview=overview)
        results.append(tag_overview)
    return results


@app.get("/seed")
async def seed(db: AsyncSession = Depends(get_db)):
    df = pd.read_csv("data/initial_games.csv")
    df = df.drop_duplicates(subset=["App ID"], keep="first")

    for index, row in df.iterrows():
        async with db.begin():
            try:
                reviews_score = float(row["Reviews Score Fancy"][:-1].replace(",", "."))
            except:
                reviews_score = 0
            release_date = pd.to_datetime(row["Release Date"])
            try:
                price = float(row["Launch Price"][1:].replace(",", "."))
            except:
                price = 0

            game = Game(
                appid=row["App ID"],
                title=row["Title"],
                reviews=row["Reviews Total"],
                reviews_score=reviews_score,
                price=price,
                release_date=release_date,
            )
            db.add(game)

            tag_titles = row["Tags"].split(",")
            game_tags = []
            for tag_title in tag_titles:
                tag_title = tag_title.strip()
                statement = select(Tag).where(Tag.title == tag_title)
                result = await db.execute(statement)
                tag = result.scalar()
                if not tag:
                    tag = Tag(title=tag_title)
                    db.add(tag)
                game_tags.append(tag)
            game.tags = game_tags
        await db.commit()
