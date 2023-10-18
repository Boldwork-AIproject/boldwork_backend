import random
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()  # .env 파일을 활성화


# 환경 변수에서 앱 비밀번호 가져오기
app_password = os.getenv("GMAIL_APP_PASSWORD")

# 이메일 인증코드 생성 함수
def generate_verification_code():
    return str(random.randint(100000, 999999))

# 이메일 발송 함수
def send_verification_email(email, code):
    subject = "Email Verification Code"
    message = f"Your verification code is: {code}"
    msg = EmailMessage()
    msg.set_content(message)
    msg["Subject"] = subject
    msg["From"] = "barleymilk640@gmail.com"  # 발송 이메일 주소
    msg["To"] = email

    # Gmail 사용 예시
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("barleymilk640@gmail.com", app_password)  # 발송 이메일 계정 정보
    server.send_message(msg)
    server.quit()