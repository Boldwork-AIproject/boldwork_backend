import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from fastapi import FastAPI
from starlette import status

from app.routers import login, upload

app = FastAPI()
app.include_router(login.router)
app.include_router(upload.router)

# 메인페이지
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "메인 페이지입니다."}