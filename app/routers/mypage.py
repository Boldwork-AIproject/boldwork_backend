from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.models import User


# 토큰 헤더에서 토큰을 추출합니다.
async def get_token_header(
    request: Request
) -> str:

    token = request.headers["Authorization"].split(" ")[1]
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]).get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# 마이페이지 정보 확인
router = APIRouter()

@router.get("/mypage")
async def get_mypage(
    token: str = Depends(get_token_header),  # `token` 매개변수는 `str` 타입입니다.
):

    # 토큰으로 사용자 조회
    user = await User.get(token)  # `user` 변수는 `User` 타입입니다.

    # 사용자 정보 조회
    user = await User.get(user.id)  # `user` 변수는 `User` 타입입니다.

    # 응답 생성
    return JSONResponse({
        "message": "My Page Information Retrieved",
        "data": user,  # `user` 변수는 `User` 타입입니다.
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