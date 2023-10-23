from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/logout",
    tags=["logout"]
)

# 로그아웃 -> access_token 쿠키 삭제 -> 메인 페이지(/)로 이동
@router.get("/")
def logout(response : Response) -> RedirectResponse:
  response = RedirectResponse("/", status_code= 302)
  response.delete_cookie(key ="access_token")
  return response