from pydantic import BaseModel
from pydantic.networks import EmailStr
from typing import Optional
from datetime import datetime

class SignupData(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str
    birthday: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UploadNewFile(BaseModel):
    name: str
    phone: str
    birthday: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[str] = None

class SearchExistCustomer(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None

class OneExistCustomer(BaseModel):
    name: str
    phone: str