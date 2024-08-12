from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from schema.competitor_overview import CompetitorOverview
from schema.tag_overview import TagOverview
from schema.year_overview import YearOverview
from services.game_service import game_service
from services.prediction_service import prediction_service
from utils.year_coeff import get_year_coeff

router = APIRouter()


@router.get("/analyze/competitors", response_model=CompetitorOverview)
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


@router.get("/analyze/trends", response_model=List[YearOverview])
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


@router.get("/analyze/tags", response_model=List[TagOverview])
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
