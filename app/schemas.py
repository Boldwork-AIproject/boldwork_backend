from pydantic import BaseModel
from pydantic.networks import EmailStr
from datetime import datetime

class Consultant(BaseModel):
    email: EmailStr
    hashed_password: str
    name: str
    phone: str
    birthday: str

class ConsultantInDB(BaseModel):
    email: EmailStr
    hashed_password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "example@gmail.com",
                "hashed_password": "hashedpassword",
            }
        }

class EmailCodeCheck(BaseModel):
    email: EmailStr
    code: str
    creation_time: datetime
    expiration_time: datetime