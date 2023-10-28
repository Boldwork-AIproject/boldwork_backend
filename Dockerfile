# 베이스 이미지로 Ubuntu 사용
FROM ubuntu:latest

# 시스템 업데이트 및 패키지 목록 업데이트
RUN apt update

# 필요한 패키지 설치
RUN apt install python3.10 python3-pip -y
RUN apt-get install -y ffmpeg
RUN apt-get install pkg-config
RUN apt-get install libmysqlclient-dev -y
RUN apt-get install git -y

# 작업 디렉토리 생성
WORKDIR /app

# 현재 디렉토리의 파일을 컨테이너의 작업 디렉토리로 복사
COPY . /app

# Python 패키지 설치
RUN pip install -r requirements.txt
RUN pip install konlpy

RUN pip install git+https://github.com/openai/whisper.git
RUN pip install -q git+https://github.com/pyannote/pyannote-audio

# 컨테이너 실행 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]