from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
SECRETS_FILE_PATH = os.path.join(PARENT_DIR, 'secrets.json')

secrets = json.loads(open(SECRETS_FILE_PATH).read())
SECRET_KEY = secrets["SECRET_KEY"]

SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{SECRET_KEY["user"]}:{SECRET_KEY["password"]}@{SECRET_KEY["host"]}:{SECRET_KEY["port"]}/{SECRET_KEY["database"]}?charset=utf8'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()