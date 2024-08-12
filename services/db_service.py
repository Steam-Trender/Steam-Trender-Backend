import json
import os
import re
from datetime import date, datetime

from fastapi import Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

import config
from app.db import get_db
from config import DATA_FOLDER
from models.game import Game
from models.tag import Tag
from models.update import Update


class DatabaseService:
    @staticmethod
    async def get_or_null(
        model, field: str, value: str, db: AsyncSession = Depends(get_db)
    ):
        statement = select(model).where(model[field] == value)
        result = await db.execute(statement)
        entity = result.scalar()
        return entity

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

    async def seed_db(self, db) -> None:
        last_update = await self.get_last_update(db)
        if last_update is None:
            last_json = self.get_last_json()
            if last_json is None:
                return
            await self.update_db(ddate=last_json, db=db)
            return

        current_date = date.today()
        if (last_update.date - current_date).days < 30:
            return

        # scrap new data and update db

        return

    async def update_db(self, ddate: date, db: AsyncSession) -> None:
        update = Update(date=ddate)
        db.add(update)
        date_str = ddate.strftime("%Y_%m_%d")
        with open(f"{DATA_FOLDER}/{date_str}.json", "r") as fp:
            data = json.load(fp)

        data = data[:1]

        for entry in data:
            appid = int(entry["appid"])
            if appid == -1:
                continue

            title = entry["title"]
            if len(title) == 0:
                continue

            price = float(entry["price"]) / 100
            if price == 0:
                continue

            try:
                release_date = datetime.strptime(
                    entry["release_date"], "%b %d, %Y"
                ).date()
            except ValueError:
                continue

            tags = [tag.strip() for tag in entry["tags"].split(",")]
            if len(tags) == 0:
                continue

            tag_objects = []
            for tag_title in tags:
                # tag = await self.get_or_null(model=Tag, field="title", value=tag_title)
                statement = select(Tag).where(Tag.title == tag_title)
                result = await db.execute(statement)
                tag = result.scalar()
                if not tag:
                    tag = Tag(title=tag_title)
                    db.add(tag)
                tag_objects.append(tag)

            reviews_score = int(entry["reviews_fancy"].replace("%", ""))
            reviews = entry["reviews"]

            statement = select(Game).where(Game.appid == appid)
            result = await db.execute(statement)
            game = result.scalar()

            if game:
                game.title = title
                game.reviews = reviews
                game.reviews_score = reviews_score
                game.tags.clear()
                game.tags = tag_objects
                continue

            game = Game(
                appid=appid,
                title=title,
                reviews=reviews,
                reviews_score=reviews_score,
                price=price,
                release_date=release_date,
                tags=tag_objects,
            )

            db.add(game)

        await db.commit()


db_service = DatabaseService()
