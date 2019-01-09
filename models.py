from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
import datetime


@as_declarative()
class Base(object):
    def as_dict(self):
        """ Returns all table-columns as a dict.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            }

    @classmethod
    def create(self, **kwargs):
        obj = self(**kwargs)
        session.add(obj)
        session.commit()
        return session.query(self).filter_by(id=obj.id).one()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False, unique=True)
    items = relationship("Item", backref="category")

    def as_dict(self):
        values = super(Category, self).as_dict()
        values['items'] = [item.as_dict() for item in self.items]
        return values


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(500))
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)
    category_id = Column(Integer, ForeignKey('category.id'))


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def setup():
    Base.metadata.create_all(engine)
