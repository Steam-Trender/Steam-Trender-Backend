from sqlalchemy import Column, Date, Integer

from app.db import Base


class Update(Base):
    __tablename__ = "updates"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
