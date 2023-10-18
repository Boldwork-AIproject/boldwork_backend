from pydantic import BaseModel
from pydantic.networks import EmailStr
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

class TokenData(BaseModel):
    email: str | None = None

class Customer(BaseModel):
    consultant_email: str
    email: EmailStr
    name: str
    phone: str
    birthday: str
    status: str
    extension: str
    disabled: bool | None = None

class UserInDB(Customer):
    hashed_password: str

class ConversationInDB(BaseModel):
    name: str
    phone: str
    birthday: str
    email: str
    gender: str

class FileForInference(BaseModel):
    customer_id: int
    file: str