import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from fastapi import FastAPI
from starlette import status

from app.routers import login, logout, upload, signup, inference, check, info, mypage

app = FastAPI()
app.include_router(login.router)
app.include_router(logout.router)
app.include_router(upload.router)
app.include_router(signup.router)
app.include_router(inference.router)
app.include_router(check.router)
app.include_router(info.router)
app.include_router(mypage.router)

# 메인페이지
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "메인 페이지입니다."}