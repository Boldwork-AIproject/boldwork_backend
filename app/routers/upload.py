from fastapi import APIRouter, Depends, Request, HTTPException
from starlette import status
from jose import JWTError

from jwt_utils import verify_access_token

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        data = verify_access_token(token)
        return data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

# 업로드 페이지
@router.get('/customer', status_code=status.HTTP_200_OK)
async def upload_customer_choice(payload = Depends(get_current_user)):   # payload의 형식 : {'sub': 'user1@example.com', 'exp': 1697530595}
    return {"message": "업로드 > 신규고객|기존고객 선택 페이지"}