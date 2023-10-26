from fastapi import APIRouter, Form, HTTPException, Query, status, Depends
from sqlalchemy import and_, or_, asc, desc
from database import SessionLocal
from datetime import timedelta
from typing import List, Dict, Union, Any

from funcs.check_token import get_current_user
from models import Consultant, Customer

router = APIRouter(
    prefix="/info",
    tags=["info"]
)

# 고객리스트 - 한 페이지 내에서 노출할 고객 수
size = 4

# 상담사가 관리하는 고객 리스트
@router.get("/", status_code=status.HTTP_200_OK)
def customer_info_list(
    name: str = Query(None, description="이름 내림차순/오름차순"),
    research: str = Query(None, description="이름/번호 검색"),
    page: int = 1,
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ) -> Dict[str, Union[str, int, List[Dict[str, Any]]]]:

    db = SessionLocal()
    # 현재 로그인한 상담사 id를 기준으로 고객 조회
    consultant_id_value = db.query(Consultant).filter(Consultant.email == payload["sub"]).first().id
    query = db.query(
        Customer.id.label('customer_id'),
        Customer.name.label('customer_name'),
        Customer.phone.label('customer_phone')
    )

    # 필터 조건 설정
    filters = []
    # 해당 상담사의 고객 리스트
    filters.append(Customer.consultant_id == consultant_id_value)

    # 필터: 검색어 입력시
    if research:
        research_filter = or_(Customer.name.like(f'%{research}%'), Customer.phone.like(f'%{research}%'))
        filters.append(research_filter)
    
    # 필터링 적용
    if filters:
        query = query.filter(and_(*filters))
    
    # Order by name
    if name == 'asc':
        query = query.order_by(Customer.name.asc())
    elif name == 'desc':
        query = query.order_by(Customer.name.desc())
    
    result = query.all()

    # 조회한 데이터 수와 페이지 수 계산
    totalCount = len(result)
    totalPage = (totalCount // size) if (totalCount % size == 0) else (totalCount // size + 1)

    db.close()

    # 해당 페이지의 데이터만 슬라이싱
    if totalPage > 1:
        data = result[size * (page - 1) : size * page]
    elif totalPage == 1:
        data = result
    data = [
        dict(customer_id=row[0], customer_name=row[1], customer_phone=row[2])
        for row in data
    ]

    return {"message": "해당 상담원의 고객 리스트입니다.", 'totalPage': totalPage , 'data': data}


# 고객 1명 정보
@router.get("/{customer_id}", status_code=status.HTTP_200_OK)
def get_one_customer(
    customer_id: int, 
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ):

    db = SessionLocal() 
    # 현재 로그인한 상담사 id를 기준으로 고객 조회
    consultant_id_value = db.query(Consultant).filter(Consultant.email == payload["sub"]).first().id
    query = db.query(Customer)

    # 필터 조건 설정
    filters = []
    # 해당 상담사의 고객 리스트
    filters.append(Customer.consultant_id == consultant_id_value)
    filters.append(Customer.id == customer_id)
    # 필터링 적용
    if filters:
        query = query.filter(and_(*filters))
    result = query.first()
    db.close()
    
    return {"message": f"{result.name} 고객 정보입니다.", "data": result}


# 고객 1명 정보
@router.put("/{customer_id}", status_code=status.HTTP_200_OK)
def change_customer_info(
    customer_id: int,
    name: str = Form(None),
    phone: str = Form(None),
    birthday: str = Form(None),
    email: str = Form(None),
    gender: str = Form(None),
    memo: str = Form(None),
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)):

    db = SessionLocal()
    # 고객 정보 조회
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    # 정보 업데이트
    if name:
        setattr(customer, "name", name)
    if phone:
        setattr(customer, "phone", phone)
    if birthday:
        setattr(customer, "birthday", birthday)
    if email:
        setattr(customer, "email", email)
    if gender:
        setattr(customer, "gender", gender)
    if memo:
        setattr(customer, "memo", memo)

    db.commit()
    db.refresh(customer)
    db.close()
    db.close()
    return {"message": "고객 정보 변경 완료"}