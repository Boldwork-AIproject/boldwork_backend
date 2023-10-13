import sys
sys.path.append("..")
from fastapi import APIRouter, HTTPException
from database import SessionLocal
from datetime import timedelta

import schemas, models
from jwt_utils import create_access_token

router = APIRouter(
    prefix="/login",
    tags=["login"]
)

@router.get("/")
def login_page():
    return {"message": "로그인 페이지입니다."}

@router.post("/")
def login_post(email: str, password: str):
    db = SessionLocal()
    user = db.query(models.Consultant).filter(models.Consultant.email == email).first()
    db.close()

    if user is None or user.hashedpassword != password:
        error_response = {
            "code": 401,
            "message": "Unauthorized",
            "error": "Authentication failed",
            "details": "Please check your email and password and try again."
        }
        raise HTTPException(status_code=401, detail=error_response)
    
    access_token = create_access_token(data={"sub": email}, expires_delta=timedelta(hours=1))
    return {"access_token": access_token, "token_type": "bearer", "messsage": "LOGIN SUCCESS"}