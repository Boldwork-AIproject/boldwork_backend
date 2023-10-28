from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Form
from database import SessionLocal
from typing import Dict, Union

from funcs.check_token import get_current_user
from funcs.speaker_diarization import process_audio
from models import Conversation


router = APIRouter(
    prefix="/inference",
    tags=["inference"]
)


@router.get("/", status_code=status.HTTP_200_OK)
def ai_analysis_loading_page(
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ) -> Dict[str, str]:
    return {"message": "AI 모델 분석 중입니다."}


# AI 분석 로딩 페이지 -> AI 분석 완료 후 데이터 다음 페이지(/check)로 보냄
@router.post("/")
def ai_analysis(
    audio_file_path: str = Form(...),
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ) -> Dict[str, Union[str, int]]:

    # STT 음성 인식 결과
    raw_text = ''
    data_list = process_audio(audio_file_path)
    for data in data_list:
      raw_text += data['text']
    result = {}
    result['raw_text'] = raw_text   # 통 대화 내용
    result['message'] = data_list   # 화자 분리한 대화 내용
    # !! 감정 분석 과정도 필요함.

    db = SessionLocal()
    conversation = db.query(Conversation).filter(Conversation.file == audio_file_path).first()
    conversation_id = conversation.id
    if conversation:
        # conversation.raw_text = {"raw": result}
        conversation.raw_text = result
        db.commit()
        db.refresh(conversation)
        db.close()
        return {"message": "AI 분석 완료", "conversation_id": conversation_id}
    else:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="데이터를 찾을 수 없습니다."
        )