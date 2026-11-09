import os
from dotenv import load_dotenv
from sqlalchemy import URL
from sqlmodel import create_engine, Session

load_dotenv()

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)

engine = create_engine(database_url, pool_pre_ping=True)

def get_session():
    with Session(engine) as session:
        yield session