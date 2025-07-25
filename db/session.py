from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

DB_PATH = 'db/rudebot.sqlite3'
engine = create_engine(
    f'sqlite:///{DB_PATH}',
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
Session = sessionmaker(bind=engine)

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close() 