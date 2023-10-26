from fastapi import APIRouter, Form, HTTPException, Query, status, Depends
from sqlalchemy import and_, or_, asc, desc
from database import SessionLocal
from datetime import timedelta
from typing import List, Dict, Union, Any

from funcs.check_token import get_current_user
from funcs.hash_password import HashPassword
from models import Conversation, Consultant, Customer

hash_password = HashPassword()

router = APIRouter(
    prefix="/mypage",
    tags=["mypage"]
)

@router.get('/', status_code=status.HTTP_200_OK)
def mypage(payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)):
    db = SessionLocal()
    result = db.query(Consultant.id, Consultant.email, Consultant.name, Consultant.phone, Consultant.birthday).filter(Consultant.email == payload["sub"]).first()
    db.close()
    return {"message": "마이페이지입니다.", "data": result}


@router.put('/')
def change_myinfo(
    name: str = Form(None),
    password: str = Form(None),
    phone: str = Form(None),
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ) -> Dict[str, str]:
    
    db = SessionLocal()
    # 상담사 정보 조회
    consultant = db.query(Consultant).filter(Consultant.email == payload["sub"]).first()
    # 정보 업데이트
    if name:
        setattr(consultant, "name", name)
    if password:
        hashed_password = hash_password.create_hash(password)
        setattr(consultant, "hashed_password", hashed_password)
    if phone:
        setattr(consultant, "phone", phone)

    db.commit()
    db.refresh(consultant)
    db.close()
    return {"message": "고객 정보가 변경되었습니다."}