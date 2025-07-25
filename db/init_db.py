import os
from sqlalchemy import create_engine
from models import Base

DB_PATH = os.path.join(os.path.dirname(__file__), 'rudebot.sqlite3')
engine = create_engine(f'sqlite:///{DB_PATH}')

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    print('Database initialized.') 