import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from sqlalchemy import Column, INTEGER, String, TIMESTAMP

from database import Base

class EmailCodeCheck(Base):
    __tablename__ = "email_code_check"
    id = Column(INTEGER, primary_key=True)
    email = Column(String(255), nullable=False)
    code = Column(String(255), nullable=False)
    creation_time = Column(TIMESTAMP, nullable=False)
    expiration_time = Column(TIMESTAMP, nullable=False)

class Consultant(Base):
    __tablename__ = "consultant"
    id = Column(INTEGER, primary_key=True)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    birthday = Column(String(255), nullable=False)