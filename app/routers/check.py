from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.models import Consultation, User, Conversation
from typing import List, int
router = APIRouter()

# `user` 매개변수는 `User` 타입입니다.
@router.get("/check")
async def get_consultations(
    user: User = Depends(get_current_user),  # `user` 매개변수는 `User` 타입입니다.
    page: int = 1,  # `page` 매개변수는 `int` 타입입니다.
    size: int = 10,  # `size` 매개변수는 `int` 타입입니다.
):
    """상담사 상담 리스트"""

    # 상담사 상담 목록 조회
    consultations: List[Consultation] = await Consultation.filter(
        author=user,  # `user` 매개변수는 `User` 타입입니다.
        status="open",
    ).paginate(page=page, per_page=size)

    # 응답 생성
    return JSONResponse({
        "code": 200,
        "message": "Search successful",
        "page": consultations.page,  # `page` 매개변수는 `int` 타입입니다.
        "size": consultations.per_page,  # `size` 매개변수는 `int` 타입입니다.
        "totalPage": consultations.pages,
        "totalCount": consultations.total,
        "data": consultations,  # `items` 속성은 `list` 타입입니다.
    })

# `conversation_id` 매개변수는 `int` 타입입니다.
@router.get("/check/{conversation_id}")
async def get_conversation(
    conversation_id: int,  # `conversation_id` 매개변수는 `int` 타입입니다.
    user: User = Depends(get_current_user),  # `user` 매개변수는 `User` 타입입니다.
):
    """상담 1개에 대한 AI상담내용"""

    # 상담 조회
    conversation: Conversation = await Conversation.get(conversation_id)  # `conversation_id` 매개변수는 `int` 타입입니다.

    # 상담이 존재하지 않으면 오류
    if not conversation:
        raise HTTPException(status_code=404, detail="상담이 존재하지 않습니다.")

    # 상담의 AI상담내용 반환
    return JSONResponse({
        "code": 200,
        "message": "Search successful",
        "conversation": conversation.conversation,  # `conversation` 속성은 `str` 타입입니다.
        "sentiment_analysis": conversation.sentiment_analysis,  # `sentiment_analysis` 속성은 `str` 타입입니다.
        "keyword_analysis": conversation.keyword_analysis,  # `keyword_analysis` 속성은 `list` 타입입니다.
        "audio_file": conversation.audio_file,  # `audio_file` 속성은 `str` 타입입니다.
    })