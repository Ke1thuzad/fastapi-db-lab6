from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import getenv
from dotenv import load_dotenv


load_dotenv()

POSTGRES_USER = getenv("POSTGRES_USER")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = getenv("POSTGRES_HOST")
POSTGRES_PORT = getenv("POSTGRES_PORT")
POSTGRES_DB = getenv("POSTGRES_DB")

url = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_engine(url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()