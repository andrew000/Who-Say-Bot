from sqlalchemy import Column, BigInteger, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import config

Base = declarative_base()
engine = create_engine(config.DATABASE, echo=False)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class WhoSayTable(Base):
    __tablename__ = 'WhoSayTable'
    id = Column(BigInteger, primary_key=True)
    name = Column(String, index=True, unique=True, nullable=False)
    say = Column(String)
