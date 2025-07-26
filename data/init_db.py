"""
Initialize the database with tables.
Updated for new data directory structure.
"""
import os
from sqlalchemy import create_engine
from models import Base

# Database path (updated for new data directory structure)
DB_PATH = os.path.join(os.path.dirname(__file__), 'rudebot.sqlite3')
engine = create_engine(f'sqlite:///{DB_PATH}')

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    print('Database initialized.') 