import datetime
from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy import and_, or_, asc, desc
from database import SessionLocal
from datetime import timedelta
from typing import List, Dict, Set, Union, Any

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
    ) -> Dict[str, Union[str, Union[Dict[str, Any], List[Dict[str, Any]]]]]:

    db = SessionLocal()
    result = db.query(
        Conversation.file,
        Conversation.raw_text["message"],
        Conversation.raw_text["badwords"],
        Conversation.raw_text["keywords"],
        Conversation.raw_text["sentiment"],
        Conversation.raw_text["favorable_tone_score"],
        Conversation.raw_text["speech_participation_score"],
        Conversation.summary,
        Consultant.name.label('consultant_name'),
        Customer.name.label('customer_name'),
        Conversation.customer_id
    ).join(
        Consultant,
        Conversation.consultant_id == Consultant.id
    ).join(
        Customer,
        Conversation.customer_id == Customer.id
    ).filter(
        Conversation.id == conversation_id
    ).first()


    # 이전 상담 대비 키워드 증감률
    keyword_growth_rate = []
    lately_keyword = db.query(Conversation.raw_text["keywords"]).filter(Conversation.customer_id == result[-1]).order_by(desc(Conversation.id)).all()
    # 이전 상담이 있을 경우
    if len(lately_keyword) > 1:
        lately_keyword = lately_keyword[1]
        for keyword, frequency in result[3][:10]:
            # 해당 키워드가 이전 상담에 있을 경우
            flag = False
            for k in lately_keyword[0]:
                if keyword == k[0]:
                    keyword_growth_rate.append([int(round(frequency / k[1] * 100, 0))])
                    flag = True
                    break
            
            # 해당 키워드가 이전 상담에 없을 경우
            if not flag:
                keyword_growth_rate.append(100)

    # 이전 상담이 없을 경우
    else:
        keyword_growth_rate = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
    
    # keywords: [키워드, 빈도, 증감률]
    keywords = []
    for k in zip(result[3][:10], keyword_growth_rate):
        keywords.append([k[0][0], k[0][1], k[1]])


    # 해당 고객의 이전 상담 감성 점수
    lately_conversation = db.query(Conversation.consultant_id, Conversation.creation_time, Conversation.raw_text).order_by(desc(Conversation.id)).all()[1:5]
    previous_sentiment = []
    for l in lately_conversation:
        temp = {}
        temp["previous_consultant"] = db.query(Consultant.name).filter(Consultant.id == l["consultant_id"]).first()[0]
        temp["creation_time"] = l["creation_time"]
        temp["conversation_sentiment"] = l["raw_text"]["sentiment"]["conversation_sentiment"]
        temp["sentiment_score"] = l["raw_text"]["sentiment"]["sentiment_score"]
        previous_sentiment.append(temp)
    db.close()

    data = {
        'audio_file': result[0],
        'messages': result[1],
        'badwords': result[2],
        'keywords': keywords,
        'sentiment': result[4],
        'favorable_tone_score': result[5],
        'speech_participation_score': result[6],
        'summary': result[7],
        'consultant_name': result[8],
        'customer_name': result[9],
        'previous_sentiment': previous_sentiment}

    return {"message": "상담 상세 페이지입니다.", "data": data}