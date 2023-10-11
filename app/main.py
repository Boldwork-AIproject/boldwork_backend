import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from dotenv import load_dotenv
load_dotenv()  # .env 파일을 활성화

from fastapi import FastAPI
from starlette import status

from app.routers import login

app = FastAPI()
app.include_router(login.router)

# 메인페이지
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "메인 페이지입니다."}