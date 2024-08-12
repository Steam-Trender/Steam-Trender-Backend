import asyncio
import threading
from datetime import date, datetime, timedelta
from typing import List

import pytz
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal, get_db, init_db
from schema.competitor_overview import CompetitorOverview
from schema.post import Post
from schema.tag import Tag
from schema.tag_overview import TagOverview
from schema.update import Update
from schema.utils import CustomStatus, Years
from schema.year_overview import YearOverview
from services.blog_service import blog_service
from services.db_service import db_service
from services.game_service import game_service
from services.mail_service import mail_service
from services.prediction_service import prediction_service
from services.scraper_service import scraper_service
from utils.year_coeff import get_year_coeff

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://yourfrontenddomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Accept", "X-Requested-With"],
)


def schedule_update_data_job():
    def process():
        current_date = date.today().strftime("%Y_%m_%d")
        scraper_service.scrap(filename=current_date)
        mail_service.send_data(filename=current_date)

    threading.Thread(target=process).start()


scheduler = BackgroundScheduler(
    timezone=pytz.timezone("Europe/Moscow"),
)


@app.on_event("startup")
async def startup_event():
    await init_db()
    async with SessionLocal() as db:
        await db_service.seed_db(db=db)
    scheduler.add_job(
        schedule_update_data_job,
        # trigger=IntervalTrigger(minutes=30, start_date=datetime.now()),
        trigger=DateTrigger(run_date=datetime.now() + timedelta(seconds=10)),
        id="update_data_job",
        replace_existing=True,
    )
    scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


@app.get("/ping")
async def get_health() -> CustomStatus:
    """Check API status."""
    return CustomStatus(status_name="pong", status_code="OK")


@app.get("/update")
async def get_last_update(db: AsyncSession = Depends(get_db)) -> Update:
    """Get last update (date)"""
    last_update = await db_service.get_last_update(db)
    return last_update


@app.get("/posts")
async def get_posts(
    blog_url: str = "https://teletype.in/@sadari", category: str = ""
) -> List[Post]:
    """Get all posts from teletype"""
    posts = blog_service.get_all_posts(url=blog_url, category=category)
    return posts


@app.get("/years")
async def get_years() -> Years:
    return Years(max_year=2024, min_year=2017)


@app.get("/tags")
async def get_tags(db: AsyncSession = Depends(get_db)) -> List[Tag]:
    """Get all tags."""
    try:
        tags = await game_service.read_all_tags(db)
        return tags
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/analyze/competitors")
async def get_competitors_analysis(
    reviews_coeff: int = 30,
    min_reviews: int = 0,
    max_reviews: int = None,
    min_year: int = 2020,
    max_year: int = 2024,
    whitelist_tag_ids: List[int] = Query(None),
    blacklist_tag_ids: List[int] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> CompetitorOverview:
    """Analyze competitors based on some filters."""
    try:
        games = await game_service.read_games(
            session=db,
            min_reviews=min_reviews,
            max_reviews=max_reviews,
            min_year=min_year,
            max_year=max_year,
            whitelist_tag_ids=whitelist_tag_ids,
            blacklist_tag_ids=blacklist_tag_ids,
        )
        overview = await game_service.analyze_games(
            games=games, reviews_coeff=reviews_coeff, revenue_agg=[0.5]
        )
        result = CompetitorOverview(games=games, overview=overview)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/analyze/trends")
async def get_trends_analysis(
    min_reviews: int = 0,
    min_year: int = 2020,
    max_year: int = 2024,
    tag_ids: List[int] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[YearOverview]:
    """Check tag trends over years."""
    results = []
    for year in range(min_year, max_year + 1, 1):
        games = await game_service.read_games(
            session=db,
            min_reviews=min_reviews,
            min_year=year,
            max_year=year,
            whitelist_tag_ids=tag_ids,
            blacklist_tag_ids=None,
        )
        coeff = get_year_coeff(year)
        overview = await game_service.analyze_games(
            games=games, reviews_coeff=coeff, revenue_agg=[0, 0.25, 0.5, 0.75, 1]
        )
        year_overview = YearOverview(year=year, overview=overview)
        results.append(year_overview)
    results = prediction_service.get_trended_years(results)
    return results


@app.get("/analyze/tags")
async def get_tags_analysis(
    reviews_coeff: int = 30,
    min_reviews: int = 30,
    min_year: int = 2020,
    max_year: int = 2024,
    tag_ids: List[int] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[TagOverview]:
    """Check tags metrics side-by-side."""
    results = []
    for tag_id in tag_ids:
        whitelist_tag_ids = [tag_id]
        games = await game_service.read_games(
            session=db,
            min_reviews=min_reviews,
            min_year=min_year,
            max_year=max_year,
            whitelist_tag_ids=whitelist_tag_ids,
            blacklist_tag_ids=None,
        )
        overview = await game_service.analyze_games(
            games=games,
            reviews_coeff=reviews_coeff,
            revenue_agg=[0, 0.25, 0.5, 0.75, 1],
        )
        tag = await game_service.read_tag_by_id(session=db, tag_id=tag_id)
        tag_overview = TagOverview(tag=tag, overview=overview)
        results.append(tag_overview)
    return results
