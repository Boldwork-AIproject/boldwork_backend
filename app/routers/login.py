import os
from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from database import SessionLocal
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()  # .env 파일을 활성화

from schemas import TokenResponse
from models import Consultant
from funcs.hash_password import HashPassword
from jwt_utils import create_access_token

router = APIRouter(
    prefix="/login",
    tags=["login"]
)

SECRET_KEY = os.getenv("SECRET_KEY")
manager = LoginManager(SECRET_KEY, '/login', use_cookie=True)
ACCESS_TOKEN_EXPIRE_MINUTES = 60
hash_password = HashPassword()

@manager.user_loader()
def query_user(email: str) -> str:
    db = SessionLocal()
    user = db.query(Consultant).filter(Consultant.email == email).first()
    db.close()
    return user['email']


# 로그인 페이지
@router.get("/", status_code=status.HTTP_200_OK)
def login() -> dict:
    return {"message": "로그인 페이지입니다."}


@router.post("/", response_model=TokenResponse)
def login_post(
    response: Response, 
    user: OAuth2PasswordRequestForm = Depends()
    ) -> dict:

    # DB에 등록된 이메일인지 확인
    db = SessionLocal()
    consultant_exist = db.query(Consultant).filter(Consultant.email == user.username).first()
    db.close()

    # 등록되지 않은 회원일 경우
    if not consultant_exist:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Please check your email and password and try again."
        )
    
    # 등록된 회원일 경우 -> 비밀번호 확인 -> 토큰 발급
    if hash_password.verify_hash(user.password, consultant_exist.hashed_password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        # 토큰을 쿠키로 설정
        response.set_cookie(key="access_token", value=access_token)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"}
    )