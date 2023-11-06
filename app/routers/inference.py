from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Form
from database import SessionLocal
from typing import Dict, Union

from funcs.check_token import get_current_user
from funcs.speaker_diarization import process_audio
from funcs.summarization import summarize
from funcs.get_words import GetWords
from funcs.get_sentiment import speaker_seperation, get_sentiment_score
from funcs.get_favorable_tone import favorable_tone
from funcs.get_speech_participation import get_speech_participation_score
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
    segments, data_list = process_audio(audio_file_path)
    
    # 발화 분리
    raw_text, speaker1_text, speaker2_text = speaker_seperation(data_list)

    result = {}
    result['raw_text'] = raw_text   # 통 대화 내용
    result['message'] = data_list   # 화자 분리한 대화 내용

    # 감정 점수
    speaker1_score, speaker2_score, sentiment_score, conversation_sentiment = get_sentiment_score(speaker1_text, speaker2_text)
    result['sentiment'] = {
        'speaker1_score': speaker1_score,
        'speaker2_score': speaker2_score,
        'sentiment_score': sentiment_score,
        'conversation_sentiment': conversation_sentiment
        }

    # summarization
    summary = summarize(raw_text)
    
    get_words = GetWords(raw_text)
    # 비속어 빈도
    result['badwords'] = get_words.get_badword_percentage()
    # 등장 키워드 및 빈도
    result['keywords'] = get_words.get_keywords()
    # 호의적인 태도 점수(백분율 0-1 사이)
    result['favorable_tone_score'] = favorable_tone(audio_file_path)
    # 대화 참여도 점수
    result['speech_participation_score'] = get_speech_participation_score(segments)
    # 필터링 키워드
    filter_keyword = get_words.get_filter_keywords()

    # DB 저장
    db = SessionLocal()
    conversation = db.query(Conversation).filter(Conversation.file == audio_file_path).first()
    conversation_id = conversation.id
    if conversation:
        conversation.raw_text = result
        conversation.summary = summary
        conversation.keyword = filter_keyword
        db.commit()
        db.refresh(conversation)
        db.close()
        return {"message": "AI 분석 완료", "conversation_id": conversation_id}
    else:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="데이터를 찾을 수 없습니다."
        )