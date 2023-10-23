FROM ubuntu:latest
RUN apt update
RUN apt install python3.10 python3-pip -y
RUN apt-get install -y ffmpeg
RUN apt-get install pkg-config
RUN apt-get install libmysqlclient-dev -y
RUN apt-get install git -y
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/openai/whisper.git
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]