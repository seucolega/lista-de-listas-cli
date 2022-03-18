import os

from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL: str = config(
    'DATABASE_URL', f'sqlite:///{os.path.dirname(__file__)}/db.sqlite3'
)
connect_args = (
    {'check_same_thread': False}
    if SQLALCHEMY_DATABASE_URL.startswith('sqlite:')
    else {}
)
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.create_all(bind=engine)
db_session = SessionLocal()
