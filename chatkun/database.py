import os

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Sequence
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SlackMessage(Base):
    __tablename__ = 'slack_messages'

    id = Column(Integer, Sequence('message_id_seq'), primary_key=True)
    text = Column(Text)
    thread_ts = Column(String)
    channel = Column(String)
    user_id = Column(String)
    created_at = Column(DateTime)


def setup_database(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    return session_maker
