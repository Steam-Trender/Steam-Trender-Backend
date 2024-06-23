from sqlalchemy import Column, ForeignKey, Integer, String, Table

from app.db import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)


game_tags = Table(
    "game_tags",
    Base.metadata,
    Column("game_id", ForeignKey("games.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)
