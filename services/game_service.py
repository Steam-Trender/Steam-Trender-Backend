from datetime import date
from typing import List

import numpy as np
from sqlalchemy import desc
from sqlalchemy.future import select

from models.game import Game
from models.tag import Tag
from schema.games_overview import GamesOverview
from schema.revenue import Revenue
from utils.constants import RevenueCoeff


class GameService:
    @staticmethod
    async def read_all_tags(session) -> List[Tag]:
        query = select(Tag)
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
        min_date: date = date(2020, 1, 1),
        max_date: date = date(2024, 12, 31),
        whitelist_tag_ids: list = None,
        blacklist_tag_ids: list = None,
    ) -> List[Game]:
        if max_reviews is not None and max_reviews < 0:
            max_reviews = None
        if max_reviews:
            min_reviews, max_reviews = min(min_reviews, max_reviews), max(
                min_reviews, max_reviews
            )

        query = select(Game).where(Game.reviews >= min_reviews)

        if max_reviews:
            query = query.where(Game.reviews <= max_reviews)

        if max_date < min_date:
            min_date, max_date = max_date, min_date

        query = query.where(Game.release_date.between(min_date, max_date))

        if whitelist_tag_ids:
            for tag_id in whitelist_tag_ids:
                query = query.filter(Game.tags.any(Tag.id == tag_id))

        if blacklist_tag_ids:
            query = query.where(~Game.tags.any(Tag.id.in_(blacklist_tag_ids)))

        query = query.order_by(desc(Game.reviews))
        result = await session.execute(query)
        games = result.scalars().all()

        return games

    @staticmethod
    async def analyze_games(
        games: List[Game], reviews_coeff: float, revenue_agg: List[float]
    ) -> GamesOverview:
        data = GamesOverview(total_games=len(games))
        reviews = []
        owners = []
        prices = []
        revenues = []
        if games:
            for game in games:
                game.owners = game.reviews * reviews_coeff
                game.revenue = np.round(game.owners * game.price * RevenueCoeff)

                reviews.append(game.reviews)
                owners.append(game.owners)
                prices.append(game.price)
                revenues.append(game.revenue)

            data.median_reviews = int(np.median(reviews))
            data.median_owners = int(np.median(owners))
            data.median_price = round(float(np.median(prices)), 2)

            for agg in revenue_agg:
                rev_agg = Revenue(agg=agg, value=float(np.quantile(revenues, agg)))
                data.revenue.append(rev_agg)

        return data


game_service = GameService()
