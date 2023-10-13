FROM python:3.10.12
WORKDIR /app
COPY ./ /app
RUN pip install -r requirements.txt
COPY secrets.json /app/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]