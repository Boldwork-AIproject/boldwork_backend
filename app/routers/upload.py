from fastapi import APIRouter, Header
from starlette import status

from jwt_utils import verify_access_token

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

# 업로드 페이지
@router.get('/customer', status_code=status.HTTP_200_OK)
async def upload_customer_choice(token: str = Header(None)):
    payload = verify_access_token(token) # payload의 형식 : {'sub': 'user1@example.com', 'exp': 1697530595}
    return {"message": "업로드 > 신규고객|기존고객 선택 페이지"}