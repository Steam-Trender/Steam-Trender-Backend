from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    reviews = Column(Integer)
    release_date = Column(Date)
    price = Column(Integer)
    tags = relationship("Tag", secondary="game_tags")
