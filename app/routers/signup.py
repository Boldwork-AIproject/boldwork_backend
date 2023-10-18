from fastapi import APIRouter, HTTPException, status
from database import SessionLocal

from schemas import SignupData
from models import Consultant
from funcs.hash_password import HashPassword

hash_password = HashPassword()

router = APIRouter(
    prefix="/signup",
    tags=["signup"]
)

# 회원가입 페이지
@router.get("/", status_code=status.HTTP_200_OK)
def signup():
    return {"message": "회원가입 페이지입니다."}


@router.post("/")
def signup_post(data: SignupData):
    # 이미 등록된 이메일인지 확인
    db = SessionLocal()
    exist_email = db.query(Consultant).filter(Consultant.email == data.email).first()
    db.close()

    # 이미 등록된 회원인 경우 -> 회원가입 X
    if exist_email:
        raise HTTPException(
            status_code=400,
            detail="이미 등록된 회원입니다. 다른 이메일을 사용하세요."
        )
    
    # 등록되지 않은 회원인 경우 -> 회원가입 O
    # 새로운 상담사 정보 DB에 저장
    hashed_password = hash_password.create_hash(data.password)
    new_consultant = Consultant(
        email=data.email,
        hashed_password=hashed_password,
        name=data.name,
        phone=data.phone,
        birthday=data.birthday
    )
    db.add(new_consultant)
    db.commit()
    db.refresh(new_consultant)
    db.close()
    return {"message": "새로운 상담사 가입이 완료되었습니다."}


# 회원가입 완료 페이지
@router.get("/complete", status_code=status.HTTP_200_OK)
def signup():
    return {"message": "회원가입 완료 페이지입니다."}
