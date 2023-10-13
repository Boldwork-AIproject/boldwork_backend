from pydantic import BaseModel
from pydantic.networks import EmailStr
from datetime import datetime

class Consultant(BaseModel):
    email: EmailStr
    hashedpassword: str
    name: str
    phone: str
    birthday: str
    status: str = '대기'
    extension: str = None

class ConsultantInDB(BaseModel):
    email: EmailStr
    hashedpassword: str

    class Config:
        schema_extra = {
            "example": {
                "email": "example@gmail.com",
                "hashedpassword": "hashedpassword",
            }
        }

class EmailCodeCheck(BaseModel):
    email: EmailStr
    code: str
    creation_time: datetime
    expiration_time: datetime