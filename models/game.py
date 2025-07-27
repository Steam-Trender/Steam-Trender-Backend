from sqlalchemy import Column, Date, Float, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.db import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    appid = Column(Integer, unique=True, nullable=False)
    title = Column(String)
    canonized_title = Column(String)
    reviews = Column(Integer)
    reviews_score = Column(Integer)
    release_date = Column(Date)
    price = Column(Float)
    tag_associations = relationship(
        "GameTagAssociation", back_populates="game"
    )
    tags = association_proxy("tag_associations", "tag")

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

    @property
    def tags_sorted(self):
        return [assoc.tag for assoc in sorted(self.tag_associations, key=lambda assoc: assoc.tag_number)]
