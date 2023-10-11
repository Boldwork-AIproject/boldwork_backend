import sys
sys.path.append("..")
from fastapi import APIRouter, HTTPException
from database import SessionLocal
import schemas, models

router = APIRouter(
    prefix="/login",
    tags=["login"]
)

@router.get("/")
def login_page():
    return {"message": "로그인 페이지입니다."}

@router.post("/")
def login_post(consultant: schemas.ConsultantInDB):
    db = SessionLocal()
    user = db.query(models.Consultant).filter(models.Consultant.email == consultant.email).first()
    db.close()

    if user is None:
        error_response = {
            "code": 401,
            "message": "Unauthorized",
            "error": "Authentication failed",
            "details": "User not found"
        }
        raise HTTPException(status_code=401, detail=error_response)
    
    if user.hashed_password != consultant.hashed_password:
        error_response = {
            "code": 401,
            "message": "Unauthorized",
            "error": "Authentication failed",
            "details": "Please check your email and password and try again."
        }
        raise HTTPException(status_code=401, degail=error_response)
    
    return {"messsage": "LOGIN SUCCESS"}