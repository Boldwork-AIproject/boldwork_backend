from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import json

secrets = json.loads(open('secrets.json').read())
SECRET_KEY = secrets["SECRET_KEY"]

SQLALCHEMY_DATABASE_URL = f'postgresql://{SECRET_KEY["user"]}:{SECRET_KEY["password"]}@{SECRET_KEY["host"]}:{SECRET_KEY["port"]}/{SECRET_KEY["database"]}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()