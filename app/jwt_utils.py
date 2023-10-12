import os
from jose import jwt
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

def verify_token(token):
    try:
        # 토큰을 복호화하여 데이터 추출
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        # 토큰이 만료되었을 경우
        return False
    except jwt.JWTError:
        # 다른 JWT 에러가 발생한 경우
        return False