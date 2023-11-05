from datetime import datetime
import os
import uuid
from pydub import AudioSegment
from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile, Query
from datetime import timedelta
from typing import Dict, List, Optional, Set, Union

from sqlalchemy import and_
from database import SessionLocal
from starlette import status
import librosa
import soundfile as sf

from models import Consultant, Customer, Conversation
from schemas import SearchExistCustomer
from funcs.check_token import get_current_user

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

# 파일 크기 제한을 300MB로 설정
MAX_FILE_SIZE = 300 * 1024 * 1024

# 파일 확장자를 가져오는 함수
def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


# 업로드 페이지
@router.get('', status_code=status.HTTP_200_OK)
def upload(
    customer: int = Query(None, description="기존 고객 id"), 
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ) -> Dict[str, Union[str, Dict[str, Optional[str]]]]:

    # (기존 고객) 상담 업로드 페이지
    if customer:
        db = SessionLocal()
        consultant_id = db.query(Consultant).filter(Consultant.email == payload['sub']).first().id
        customer_data = db.query(
            Customer.name, Customer.phone, Customer.birthday, Customer.email, Customer.gender).filter(
                Customer.id == customer, Customer.consultant_id == consultant_id
            ).first()
        customer_data = {"name": customer_data[0], "phone": customer_data[1], "birthday": customer_data[2], "email": customer_data[3], "gender": customer_data[4]}
        db.close()
        return {"message": "(기존 고객) 상담 업로드 페이지입니다.", "customer": customer_data}
    
    # (새로운 고객) 상담 업로드 페이지
    else:
        return {"message": "(새로운 고객) 상담 업로드 페이지입니다."}


# 새로운 고객 정보, 음성 파일 업로드
@router.post('')
async def upload_post(
    name: str = Form(...),
    phone: str = Form(...),
    birthday: str = Form(None),
    email: str = Form(None),
    gender: str = Form(None),
    audio_file: UploadFile = File(...), 
    customer: int = Query(None, description="기존 고객 id"), 
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ) -> Dict[str, str]:

    # 현재 작업 디렉토리 가져오기
    current_directory = os.getcwd()

    # 고유한 ID 생성
    unique_id = str(uuid.uuid4())
    filename = f"audio_{unique_id}{get_file_extension(audio_file.filename)}"
    
    if audio_file.filename[-3:] == 'wav' or audio_file.filename[-3:] == 'mp3':
        # 저장할 파일의 상대 경로
        output_file = os.path.join(current_directory, "audio", filename)

        signal, _ = librosa.load(audio_file.file, sr=16000)
        sf.write(output_file, signal, 16000)

        if audio_file.filename[-3:] == 'mp3':
            # WAV 파일로 변환할 경로
            wav_output_file = f"{output_file[:-4]}.wav"

            # MP3 파일을 로드
            audio = AudioSegment.from_mp3(output_file)

            # WAV 파일로 저장, MP3 파일 삭제
            audio.export(wav_output_file, format="wav")
            os.remove(output_file)
            output_file = wav_output_file
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='mp3 또는 wav 형식의 파일이어야 합니다.'
        )

    db = SessionLocal()
    consultant_id = db.query(Consultant).filter(Consultant.email == payload['sub']).first().id
    
    # 새로운 고객일 경우
    if not customer:

        # 기존 고객인지 확인 (이름, 전화번호)
        not_new_customer = db.query(Customer).filter(and_(Customer.name == name, Customer.phone == phone)).first()
        if not_new_customer:
            db.close()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 고객입니다"
            )
        
        # 새로운 고객이 맞으면 DB에 고객 정보 저장
        else:
            new_customer = Customer(
                consultant_id=consultant_id,
                name=name,
                phone=phone,
                birthday=birthday,
                email=email,
                gender=gender
            )
            db.add(new_customer)
            db.commit()
            db.refresh(new_customer)
            customer_id = db.query(Customer).filter(and_(Customer.name == name, Customer.phone == phone)).first().id
    else:
        customer_id = customer

    # 오디오 파일 경로 DB에 저장    
    new_audio_path = Conversation(
        consultant_id=consultant_id,
        customer_id=customer_id,
        file=output_file,
        creation_time=datetime.utcnow()
    )
    db.add(new_audio_path)
    db.commit()
    db.refresh(new_audio_path)
    db.close()

    return {"message": "File uploaded!", "audio_file_path": output_file}


# 신규고객 or 기존고객 선택 페이지
@router.get('/customer', status_code=status.HTTP_200_OK)
def customer_choice(
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ) -> Dict[str, str]:   # payload의 형식 : {'sub': 'user1@example.com', 'exp': 1697530595}
    return {"message": "업로드 > 신규고객|기존고객 선택 페이지"}


# 기존고객 검색 페이지
@router.get('/existing', status_code=status.HTTP_200_OK)
def search_customer_page(
    name: str = Query(None, description="고객이름", min_length=1), 
    phone: str = Query(None, description="전화번호", max_length=11), 
    selected: int = Query(None, description="선택된 고객"), 
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ) -> Dict[str, Union[str, int, List[Dict[str, Union[int, str]]]]]:

    if selected:
        return {"message": "기존 고객 선택 완료", "customer_id": selected}

    if (not name) and (not phone):
        return {"message": "업로드 > 기존고객 선택 > 기존고객 검색 페이지"}
    
    db = SessionLocal()
    customers = []
    consultant_id = db.query(Consultant).filter(Consultant.email == payload['sub']).first().id
    try:
        if name and phone:
            # 이름 + 전화번호로 고객 검색
            customers_by_name_and_phone = db.query(Customer.id, Customer.name, Customer.phone).filter(and_(Customer.consultant_id == consultant_id, Customer.name == name, Customer.phone == phone)).all()
            for c in customers_by_name_and_phone:
             temp = {"id":c[0], "name":c[1], "phone":c[2]}
             customers.append(temp)

        elif name:
            # 이름으로 고객 검색
            customers_by_name = db.query(Customer.id, Customer.name, Customer.phone).filter(and_(Customer.consultant_id == consultant_id, Customer.name == name)).all()
            for c in customers_by_name:
             temp = {"id":c[0], "name":c[1], "phone":c[2]}
             customers.append(temp)

        elif phone:
            # 전화번호로 고객 검색
            customers_by_phone = db.query(Customer.id, Customer.name, Customer.phone).filter(and_(Customer.consultant_id == consultant_id, Customer.phone == phone)).all()
            for c in customers_by_phone:
             temp = {"id":c[0], "name":c[1], "phone":c[2]}
             customers.append(temp)
        
        if len(customers) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No customer data"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching for customers"
        )
    
    finally:
        db.close()
    return {"message": "Customer list returned", "customer_list": customers}


# 리스트에서 고객 선택 이후 확인 버튼 -> 다음 페이지로 고객 정보 보냄
@router.post('/existing')
def existing_customer_post(
    data: SearchExistCustomer,
    name: str = Query(None, description="고객이름", min_length=1),
    phone: str = Query(None, description="전화번호", max_length=11),
    selected: int = Query(None, description="선택된 고객"),
    payload: Dict[str, Union[str, timedelta]] = Depends(get_current_user)
    ) -> Dict[str, Union[Optional[str], int]]:

    # 고객 리스트에서 고객 선택한 경우 -> 고객 id를 다음 페이지(GET /upload)로 전송
    if selected:
        return {"message": "기존 고객 선택 완료", "customer": selected}
    
    # 입력한 name 또는 phone을 쿼리 파라미터로 전송 -> GET /existing
    return {"message": "고객 선택", "name": data.name, "phone": data.phone}