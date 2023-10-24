from fastapi import APIRouter, HTTPException, status
from database import SessionLocal
from datetime import datetime, timedelta
from typing import Dict

from schemas import SignupData
from models import Consultant, EmailCodeCheck
from funcs.hash_password import HashPassword
from funcs.send_email_code import generate_verification_code, send_verification_email

hash_password = HashPassword()

router = APIRouter(
    prefix="/signup",
    tags=["signup"]
)

# 회원가입 페이지
@router.get("/", status_code=status.HTTP_200_OK)
def signup() -> Dict[str, str]:
    return {"message": "회원가입 페이지입니다."}


# 이메일 인증 요청
@router.post("/request-verification")
def request_verification(email: str) -> Dict[str, str]:
    # DB에 등록된 이메일인지 확인
    db = SessionLocal()
    email_exist = db.query(Consultant).filter(Consultant.email == email).first()
    db.close()

    # 등록되지 않은 이메일인 경우 이메일 인증코드 발송
    if email_exist:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="Email already signed up"
        )
    else:
        # 이메일 인증 코드 생성
        verification_code = generate_verification_code()
        
        # 이메일 인증 코드 발송
        send_verification_email(email, verification_code)

        # 이메일 인증 코드 관련 정보 DB 저장
        current_time = datetime.now()
        db = SessionLocal()
        new_email_code_check = EmailCodeCheck(
            email=email,
            code=verification_code,
            creation_time=current_time,
            expiration_time=current_time + timedelta(minutes=5)
        )
        db.add(new_email_code_check)
        db.commit()
        db.refresh(new_email_code_check)
        db.close()
        return {"message": "Verification code sent to your email"}


# 이메일 인증
@router.post("/verify")
def verify_email(email: str, code: str) -> Dict[str, str]:
    db = SessionLocal()
    temp_user = db.query(EmailCodeCheck).filter(EmailCodeCheck.email == email).first()

    # 모종의 이유로 이메일이 조회되지 않는 경우
    if temp_user is None:
        db.close()
        raise HTTPException(status_code=404, detail="Email not found")
    
    # 이메일 인증 코드 유효시간이 지난 경우
    elif temp_user.expiration_time < datetime.now():
        db.close()
        raise HTTPException(status_code=400, detail="Email verification code has expired")
    
    if temp_user.code == code:
        temp_user.is_verified = True
        db.commit()
        db.close()
        return {"message": "Email verification successful"}
    
    db.close()
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Error occured in verifying email code",
    )


@router.post("/")
def signup_post(data: SignupData) -> Dict[str, str]:
    db = SessionLocal()
    temp_user = db.query(EmailCodeCheck).filter(EmailCodeCheck.email == data.email).first()
    if temp_user is None or not temp_user.is_verified:
        db.close()
        raise HTTPException(status_code=400, detail="Email not verified")
    
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
def signup() -> Dict[str, str]:
    return {"message": "회원가입 완료 페이지입니다."}