from sqlalchemy import Column, Date, Float, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    appid = Column(Integer, unique=True, nullable=False)
    title = Column(String)
    reviews = Column(Integer)
    reviews_score = Column(Integer)
    release_date = Column(Date)
    price = Column(Float)
    tags = relationship(
        "Tag", secondary="game_tags", back_populates="games", lazy="selectin"
    )

    _revenue = None
    _owners = None

    @property
    def owners(self):
        return self._owners

    @owners.setter
    def owners(self, value):
        self._owners = value

    @property
    def revenue(self):
        return self._revenue

    @revenue.setter
    def revenue(self, value):
        self._revenue = value
