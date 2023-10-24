from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.models import User
from app.services import auth_service
from app import settings
import jwt
from typing import str, List
# 토큰 헤더에서 토큰을 추출합니다.
async def get_token_header(
    request: Request
) -> str:

    token = request.headers["Authorization"].split(" ")[1]  # `token` 매개변수는 `str` 타입입니다.
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])  # `payload` 변수는 `dict` 타입입니다.
        user_id = payload.get("sub")  # `user_id` 변수는 `str` 타입입니다.
        user = await auth_service.get_user_by_id(user_id)  # `user` 변수는 `User` 타입입니다.
        return user.id
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# 마이페이지 정보 확인
router = APIRouter()

@router.get("/mypage")
async def get_mypage(
    token: str = Depends(get_token_header),  # `token` 매개변수는 `str` 타입입니다.
):

    # 토큰으로 사용자 조회
    user_id = token  # `user_id` 변수는 `str` 타입입니다.
    user = await User.get(user_id)  # `user` 변수는 `User` 타입입니다.

    # 사용자 권한 확인
    if user.is_admin:
        # 관리자 권한이 있는 경우 모든 사용자 정보를 조회합니다.
        users: List[User] = await User.all()
    else:
        # 관리자 권한이 없는 경우 자신의 정보를 조회합니다.
        users: List[User] = [user]

    # 응답 생성
    return JSONResponse({
        "message": "My Page Information Retrieved",
        "data": users,  # `users` 변수는 `list` 타입입니다.
    })


# # API 라우터 등록
# app.include_router(router)


# # User 모델
# class User(Base):
#     id = Column(Integer, primary_key=True)  # `id` 속성은 `int` 타입입니다.
#     email = Column(String(255), unique=True)  # `email` 속성은 `str` 타입입니다.
#     password = Column(String(255))  # `password` 속성은 `str` 타입입니다.
#     name = Column(String(255))  # `name` 속성은 `str` 타입입니다.
#     phone_number = Column(String(255))  # `phone_number` 속성은 `str` 타입입니다.
#     birthday = Column(String(255))  # `birthday` 속성은 `str` 타입입니다.
#     is_admin = Column(Boolean, default=False)  # `is_admin` 속성은 `bool` 타입입니다.
#     def __repr__(self):
#         return f"<User {self.id} {self.email} {self.name}>"


# import 부족한 부분
# `settings` 모듈 import
# `jwt` 모듈 import

# 타입힌트 추가
# `get_token_header()` 함수의 `token` 매개변수에 `str` 타입을 지정했습니다.
# `get_mypage()` 함수의 `token` 매개변수에 `str` 타입을 지정했습니다.
# `get_mypage()` 함수의 `user` 변수에 `User` 타입을 지정했습니다.
# `get_mypage()` 함수의 `users` 변수에 `list` 타입을 지정했습니다