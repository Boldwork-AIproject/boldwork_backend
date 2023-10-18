import os
from fastapi import HTTPException, status
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()  # .env 파일을 활성화

# .env 파일에서 SECRET_KEY 가져오기
SECRET_KEY = os.getenv("SECRET_KEY")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
    
def verify_access_token(token: str):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        expire = data.get("exp")

        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied"
            )
        if datetime.utcnow() > datetime.utcfromtimestamp(expire):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token expired!"
            )
        return data

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )