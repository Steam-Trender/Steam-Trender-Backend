from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.db import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    game_associations = relationship(
        "GameTagAssociation", back_populates="tag"
    )
    games = association_proxy("game_associations", "game")





class GameTagAssociation(Base):
    __tablename__ = "game_tags"

    game_id = Column("game_id", ForeignKey("games.id"), primary_key=True)
    tag_id = Column("tag_id", ForeignKey("tags.id"), primary_key=True)
    tag_number = Column(Integer, nullable=False, default=1)

    game = relationship("Game", back_populates="tag_associations")
    tag = relationship("Tag", back_populates="game_associations")
