from sqlalchemy import Column, Date, Float, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    appid = Column(Integer, unique=True, nullable=False)
    title = Column(String)
    reviews = Column(Integer)
    reviews_score = Column(Float)
    release_date = Column(Date)
    price = Column(Float)
    tags = relationship(
        "Tag", secondary="game_tags", back_populates="games", lazy="selectin"
    )
