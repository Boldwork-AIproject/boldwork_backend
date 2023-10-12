import sys
sys.path.append("..")
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jwt_utils import verify_token  # jwt_utils 모듈을 import
router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

# OAuth2PasswordBearer를 사용하여 access_token을 가져옵니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # 로그인 엔드포인트 URL을 지정

# /upload 엔드포인트에 접근 권한을 설정합니다.
@router.get("/")
async def upload_files(token: str = Depends(oauth2_scheme)):
    # access_token이 유효한지 확인
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Access token is invalid")
    return {"message": "Access granted. You can upload files."}
