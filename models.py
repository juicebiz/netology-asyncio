from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import Integer, Column, String, Text

PG_DSN = 'postgresql+asyncpg://swapy:swapy1pwd@localhost:5431/swapy'
engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class SwapiPeople(Base):

    __tablename__ = 'swapi_people'
    id = Column(Integer, primary_key=True)
    birth_year = Column(String(32))
    eye_color = Column(String(16))
    gender = Column(String(16))
    hair_color = Column(String(16))
    height = Column(String(8))
    homeworld = Column(String(255))
    mass = Column(String(8))
    name = Column(String(255))
    skin_color = Column(String(32))
    films = Column(Text)
    species = Column(Text)
    starships = Column(Text)
    url = Column(String(255))
    vehicles = Column(Text)
