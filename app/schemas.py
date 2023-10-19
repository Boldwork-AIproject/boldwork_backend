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

class SearchExistCustomer(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None