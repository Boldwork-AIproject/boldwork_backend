from fastapi import APIRouter, HTTPException, status, Depends, Form
from database import SessionLocal

from funcs.check_token import get_current_user
from models import Conversation

router = APIRouter(
    prefix="/test-check",
    tags=["test-check"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def ai_analysis_loading_page(
    conversation_id: int,
    payload: dict = Depends(get_current_user)
    ) -> dict:
    db = SessionLocal()
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    raw_text = conversation.raw_text
    db.close()
    return {"message": "인식 결과.", "raw": raw_text["raw"]}