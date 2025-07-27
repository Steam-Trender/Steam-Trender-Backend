import json
import os
import re
from datetime import date, datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

import config
from config import DATA_FOLDER
from models.game import Game
from models.tag import Tag, GameTagAssociation
from models.update import Update
from utils.canonize import canonize


class DatabaseService:
    @staticmethod
    async def get_last_update(session: AsyncSession) -> Update:
        statement = select(Update).order_by(desc(Update.date)).limit(1)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    def get_last_json() -> date | None:
        date_pattern = re.compile(r"^(\d{4}_\d{2}_\d{2})")
        max_date = None

        for filename in os.listdir(config.DATA_FOLDER):
            match = date_pattern.match(filename)
            if not match:
                continue
            date_str = match.group(1)
            date = datetime.strptime(date_str, "%Y_%m_%d").date()
            if max_date is None or date > max_date:
                max_date = date

        return max_date

    @staticmethod
    async def update_db(ddate: date, db: AsyncSession) -> None:
        update = Update(date=ddate)
        db.add(update)
        date_str = ddate.strftime("%Y_%m_%d")
        with open(f"{DATA_FOLDER}/{date_str}.json", "r") as fp:
            data = json.load(fp)

        # pre-fetching
        existing_games = await db.execute(select(Game))
        game_map = {game.appid: game for game in existing_games.scalars()}
        existing_tags = await db.execute(select(Tag))
        tag_map = {tag.title: tag for tag in existing_tags.scalars()}

        for entry in data:
            appid = int(entry["appid"])
            if appid == -1:
                continue

            title = entry["title"]
            canonized_title = canonize(title)
            if len(title) == 0:
                continue

            price = float(entry["price"]) / 100
            if price == 0:
                continue

            release_date_field = (
                "early_access_date" if entry["early_access_date"] else "release_date"
            )
            try:
                release_date = datetime.strptime(
                    entry[release_date_field], "%b %d, %Y"
                ).date()
            except ValueError:
                continue

            tags = [tag.strip() for tag in entry["tags"].split(",")]
            if len(tags) == 0:
                continue

            tag_objects = []
            for idx, tag_title in enumerate(tags, 1):
                tag = tag_map.get(tag_title)
                if not tag:
                    tag = Tag(title=tag_title)
                    db.add(tag)
                    tag_map[tag_title] = tag
                tag_objects.append(
                    GameTagAssociation(tag=tag, tag_number=idx)
                )

            reviews_score = int(entry["reviews_fancy"].replace("%", ""))
            reviews = entry["reviews"]

            game = game_map.get(appid)
            if game:
                game.title = title
                game.canonized_title = canonized_title
                game.reviews = reviews
                game.reviews_score = reviews_score
                game.tag_associations.clear()
                game.tag_associations = tag_objects
                continue

            game = Game(
                appid=appid,
                title=title,
                canonized_title=canonized_title,
                reviews=reviews,
                reviews_score=reviews_score,
                price=price,
                release_date=release_date,
                tag_associations=tag_objects,
            )

            db.add(game)
            await db.commit()

    async def seed_db(self, db) -> None:
        last_update = await self.get_last_update(db)
        if last_update is not None:
            return
        last_json = self.get_last_json()
        if last_json is not None:
            print(f"start seeding: {last_json}")
            await self.update_db(ddate=last_json, db=db)


db_service = DatabaseService()
