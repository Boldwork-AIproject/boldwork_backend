from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy import and_, or_, asc, desc
from database import SessionLocal
from datetime import timedelta
from typing import List, Dict, Union, Any

from funcs.check_token import get_current_user
from models import Conversation, Consultant, Customer

router = APIRouter(
    prefix="/check",
    tags=["check"]
)

# 상담리스트 - 한 페이지 내에서 노출할 상담 수
size = 6

# 상담사 - 상담리스트
@router.get("/", status_code=status.HTTP_200_OK)
def conversation_page(
    datetime: str = Query(None, description="날짜 내림차순/오름차순"),
    name: str = Query(None, description="이름 내림차순/오름차순"),
    keyword_choice: str = Query(None, description="키워드 선택"),
    research: str = Query(None, description="이름/번호 검색"),
    page: int = 1,
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ) -> Dict[str, Union[str, int, List[Dict[str, Any]]]]:

    db = SessionLocal()
    # 현재 로그인한 상담사 id를 기준으로 상담 데이터 조회
    consultant_id_value = db.query(Consultant).filter(Consultant.email == payload["sub"]).first().id
    query = db.query(
        Conversation.id.label('conversation_id'),
        Conversation.customer_id,
        Conversation.keyword,
        Conversation.creation_time,
        Customer.name.label('customer_name'),
        Customer.phone.label('customer_phone')
    ).join(
        Customer,
        Conversation.customer_id == Customer.id
    )

    # 필터 조건 설정
    filters = []
    # 해당 상담사의 상담 리스트
    filters.append(Conversation.consultant_id == consultant_id_value)

    # 필터: 키워드 선택시
    if keyword_choice:
        filters.append(Conversation.keyword.like(f'%{keyword_choice}%'))
    # 필터: 검색어 입력시
    if research:
        research_filter = or_(Customer.name.like(f'%{research}%'), Customer.phone.like(f'%{research}%'))
        filters.append(research_filter)
    
    # 필터링 적용
    if filters:
        query = query.filter(and_(*filters))

    # 오름차순 / 내림차순 적용
    # Order by datetime and name
    if datetime == 'asc' and name == 'asc':
        query = query.order_by(asc(Conversation.creation_time), asc(Customer.name))
    elif datetime == 'asc' and name == 'desc':
        query = query.order_by(asc(Conversation.creation_time), desc(Customer.name))
    elif datetime == 'desc' and name == 'asc':
        query = query.order_by(desc(Conversation.creation_time), asc(Customer.name))
    elif datetime == 'desc' and name == 'desc':
        query = query.order_by(desc(Conversation.creation_time), desc(Customer.name))
    
    # Order by datetime
    elif datetime == 'asc':
        query = query.order_by(Conversation.creation_time.asc())
    elif datetime == 'desc':
        query = query.order_by(Conversation.creation_time.desc())

    # Order by name
    elif name == 'asc':
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
        dict(conversation_id=row[0], customer_id=row[1], keyword=row[2], creation_time=row[3], customer_name=row[4], customer_phone=row[5])
        for row in data
    ]

    return {"message": "해당 상담원의 상담 리스트입니다.", 'totalPage': totalPage , 'data': data}


# 개별 상담 상세 페이지
@router.get("/{conversation_id}", status_code=status.HTTP_200_OK)
def one_conversation(
    conversation_id: int, 
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ) -> Dict[str, Union[str, Dict[str, Any]]]:

    # !! keyword_analysis, sentiment_analysis 추가해야함.
    db = SessionLocal()
    result = db.query(
        Conversation.file,
        Conversation.raw_text["message"],
        Conversation.summary,
        Consultant.name.label('consultant_name'),
        Customer.name.label('customer_name'),
    ).join(
        Consultant,
        Conversation.consultant_id == Consultant.id
    ).join(
        Customer,
        Conversation.customer_id == Customer.id
    ).filter(
        Conversation.id == conversation_id
    ).first()
    db.close()

    data = {
        'audio_file': result[0],
        'messages': result[1],
        'summary': result[2],
        'consultant_name': result[3],
        'customer_name': result[4]}

    return {"message": "상담 상세 페이지입니다.", "data": data}