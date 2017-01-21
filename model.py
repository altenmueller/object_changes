from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class ObjectChange(Base):
    __tablename__ = 'object_changes'
    id = Column(Integer, primary_key=True)
    object_id = Column(Integer, nullable=False)
    object_type = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)
    changes = Column(String, nullable=False)


def create_db():
    Base.metadata.create_all(bind=engine)


create_db()
