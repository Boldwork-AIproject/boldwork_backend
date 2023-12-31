import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from sqlalchemy import Column, INTEGER, String, Boolean, TIMESTAMP, LargeBinary, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from database import Base


class EmailCodeCheck(Base):
    __tablename__ = "email_code_check"

    id = Column(INTEGER, primary_key=True)
    email = Column(String(255), nullable=False)
    code = Column(String(255), nullable=False)
    creation_time = Column(TIMESTAMP, nullable=False)
    expiration_time = Column(TIMESTAMP, nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)


class Consultant(Base):
    __tablename__ = 'consultant'

    id = Column(INTEGER, primary_key=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    birthday = Column(String, nullable=False)
    status = Column(String, nullable=False, default='대기')
    extension = Column(String, nullable=False, default='0000')
    disabled = Column(Boolean, nullable=False, default=False)

    customer = relationship("Customer", back_populates="consultant")
    

class Customer(Base):
    __tablename__ = 'customer'

    id = Column(INTEGER, primary_key=True)
    consultant_id = Column(INTEGER, ForeignKey("consultant.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    birthday = Column(String, nullable=True)
    email = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    memo = Column(String, nullable=True)

    consultant = relationship("Consultant", back_populates="customer")


class Conversation(Base):
    __tablename__ = 'conversation'

    id = Column(INTEGER, primary_key=True)
    consultant_id = Column(INTEGER, ForeignKey("consultant.id"), nullable=False)
    customer_id = Column(INTEGER, ForeignKey("customer.id"), nullable=False)
    keyword = Column(String)
    file = Column(String, nullable=False)
    raw_text = Column(JSON)
    summary = Column(String)
    creation_time = Column(TIMESTAMP, nullable=False)