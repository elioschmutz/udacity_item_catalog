from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    items = relationship("Item", backref="category")


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(500))
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)
    category_id = Column(Integer, ForeignKey('category.id'))


engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def setup():
    Base.metadata.create_all(engine)
