from datetime import date
from typing import List

import numpy as np
from sqlalchemy import desc
from sqlalchemy.future import select

from models.game import Game
from models.tag import Tag
from schema.games_overview import GamesOverview
from utils.constants import RevenueCoeff


class GameService:
    @staticmethod
    async def read_all_tags(session) -> List[Tag]:
        query = select(Tag)

        result = await session.execute(query)
        tags = result.scalars().all()

        return tags

    @staticmethod
    async def read_games(
        session,
        min_reviews: int,
        min_year: int,
        max_year: int,
        whitelist_tag_ids: list = None,
        blacklist_tag_ids: list = None,
    ) -> List[Game]:
        query = select(Game).where(Game.reviews >= min_reviews)

        if min_year != 0 and max_year != 0:
            start_date = date(min_year, 1, 1)
            end_date = date(max_year, 12, 31)
            query = query.where(Game.release_date.between(start_date, end_date))

        if whitelist_tag_ids:
            query = query.where(Game.tags.any(Tag.id.in_(whitelist_tag_ids)))

        if blacklist_tag_ids:
            query = query.where(~Game.tags.any(Tag.id.in_(blacklist_tag_ids)))

        query = query.order_by(desc(Game.reviews)).limit(100)
        result = await session.execute(query)
        games = result.scalars().all()

        return games

    @staticmethod
    async def analyze_games(games: List[Game], reviews_coeff: float) -> GamesOverview:
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

            data.median_reviews = float(np.median(reviews))
            data.median_owners = float(np.median(owners))
            data.median_price = float(np.median(prices))
            data.median_revenue = float(np.median(revenues))

        return data
