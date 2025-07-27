from datetime import date
from typing import List

import numpy as np
from sqlalchemy import asc, desc, func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.game import Game
from models.tag import Tag, GameTagAssociation
from schema.games_overview import GamesOverview
from schema.revenue import Revenue
from schema.tag import ExtendedTag
from utils.constants import RevenueCoeff
from utils.validate_range import validate_range


class GameService:
    @staticmethod
    async def read_all_tags(session) -> List[Tag]:
        query = select(Tag).order_by(asc(Tag.title))
        result = await session.execute(query)
        tags = result.scalars().all()
        return tags

    @staticmethod
    async def read_tag_by_id(session, tag_id) -> Tag:
        query = select(Tag).filter(Tag.id == tag_id)
        result = await session.execute(query)
        tag = result.scalars().first()
        return tag

    @staticmethod
    async def read_games(
        session,
        min_reviews: int = 0,
        max_reviews: int = None,
        min_price: float = 0,
        max_price: float = None,
        min_date: date = date(2020, 1, 1),
        max_date: date = date(2024, 12, 31),
        whitelist_tag_ids: list = None,
        blacklist_tag_ids: list = None,
        tag_threshold: int = 5,
    ) -> List[Game]:
        min_reviews, max_reviews = validate_range(min_reviews, max_reviews)
        min_price, max_price = validate_range(min_price, max_price)
        min_date, max_date = validate_range(min_date, max_date)

        query = select(Game).where(Game.reviews >= min_reviews)
        if max_reviews:
            query = query.where(Game.reviews <= max_reviews)

        query = query.where(Game.price >= min_price)
        if max_price:
            query = query.where(Game.price <= max_price)

        query = query.where(Game.release_date.between(min_date, max_date))

        if whitelist_tag_ids:
            for tag_id in whitelist_tag_ids:
                query = query.filter(
                    Game.tag_associations.any(
                        (GameTagAssociation.tag_id == tag_id) &
                        (GameTagAssociation.tag_number <= tag_threshold)
                    )
                )

        if blacklist_tag_ids:
            for tag_id in blacklist_tag_ids:
                query = query.filter(
                    ~Game.tag_associations.any(
                        (GameTagAssociation.tag_id == tag_id) &
                        (GameTagAssociation.tag_number <= tag_threshold)
                    )
                )

        query = query.options(
            selectinload(Game.tag_associations).selectinload(GameTagAssociation.tag)
        )

        query = query.order_by(desc(Game.reviews))
        result = await session.execute(query)
        games = result.scalars().all()

        print(len(games))

        return games

    @staticmethod
    async def analyze_games(
        games: List[Game],
        reviews_coeff: float,
        revenue_agg: List[float],
        update_games: bool = False,
    ) -> GamesOverview:
        data = GamesOverview(total_games=len(games))
        if not games:
            return data

        reviews = np.array([game.reviews for game in games])
        prices = np.array([game.price for game in games])

        owners = reviews * reviews_coeff
        revenues = np.round(owners * prices * RevenueCoeff)

        if update_games:
            for i, game in enumerate(games):
                game.owners = owners[i]
                game.revenue = revenues[i]

        data.median_reviews = int(np.median(reviews))
        data.median_owners = int(np.median(owners))
        data.median_price = round(float(np.median(prices)), 2)
        data.revenue_total = int(np.sum(revenues))

        for agg in revenue_agg:
            rev_agg = Revenue(agg=agg, value=int(np.quantile(revenues, agg)))
            data.revenue.append(rev_agg)

        return data

    @staticmethod
    async def get_top_tags(
        session, games: List[Game], skip_tag_ids: List[int], limit: int = 3
    ) -> List[ExtendedTag]:
        game_ids = [game.id for game in games]

        stmt = (
            select(
                Tag.id,
                Tag.title,
                func.count(Tag.id).label("games_count")
            )
            .join(GameTagAssociation, Tag.id == GameTagAssociation.tag_id)
            .filter(GameTagAssociation.game_id.in_(game_ids))
            .group_by(Tag.id, Tag.title)
        )

        if skip_tag_ids:
            stmt = stmt.filter(~Tag.id.in_(skip_tag_ids))

        stmt = (
            stmt.group_by(Tag.id, Tag.title)
            .order_by(desc(func.count(Tag.id)))
            .limit(limit)
        )

        result = await session.execute(stmt)

        tags = [ExtendedTag.from_orm(tag) for tag in result.all()]

        return tags


game_service = GameService()
