from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
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
        Session().add(obj)
        Session().commit()
        return self.query().filter_by(id=obj.id).one()

    @classmethod
    def query(self):
        return Session().query(self)


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
    provider = Column(String(250))
    picture = Column(String(250))
    login_sessions = relationship("LoginSession", backref="user")

    @classmethod
    def lookup_by_user_id(self, user_id):
        user = self.query().filter_by(id=user_id).one()
        return user

    @classmethod
    def lookup_by_email(self, email):
        try:
            return self.query().filter_by(email=email).one()
        except:
            return None


class LoginSession(Base):
    __tablename__ = 'login_session'

    id = Column(Integer, primary_key=True)
    token = Column(String(250), nullable=False)
    provider = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))

    @classmethod
    def lookup_by_token(self, token):
        return self.query().filter_by(token=token).first()

engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine
Session = scoped_session(sessionmaker(bind=engine))


def setup():
    Base.metadata.create_all(engine)
