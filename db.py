import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, JSON
from sqlalchemy.ext.mutable import MutableDict


engine = create_engine('postgres://{0}:{1}@localhost/{2}'.format(config.db_user, config.db_passw, config.db_name))

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True)
    data = Column(MutableDict.as_mutable(JSON))

    def __repr__(self):
        return "<User(id=%s, user_id=%s, data=%s)>" % (
            self.id, self.user_id, self.data
        )


Session = sessionmaker(engine)
session = Session()
Base.metadata.create_all(engine)


