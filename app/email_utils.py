import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader

def get_env_variable(name: str, default=None):
    return os.getenv(name, default)

# 이메일 발송 함수
async def send_email(recipient_email: str, verification_code: str):
    conf = ConnectionConfig(
        MAIL_USERNAME=get_env_variable("MAIL_USERNAME"),
        MAIL_PASSWORD=get_env_variable("MAIL_PASSWORD"),
        MAIL_FROM=get_env_variable("MAIL_FROM"),
        MAIL_PORT=int(get_env_variable("MAIL_PORT", 465)),
        MAIL_SERVER=get_env_variable("MAIL_SERVER"),
        MAIL_SSL_TLS=bool(get_env_variable("MAIL_SSL_TLS", True)),
        MAIL_STARTTLS=bool(get_env_variable("MAIL_STARTTLS", False)),
        USE_CREDENTIALS=bool(get_env_variable("USE_CREDENTIALS", True)),
        VALIDATE_CERTS=bool(get_env_variable("VALIDATE_CERTS", True)),
    )

    # Jinja2 환경 설정
    env = Environment(loader=FileSystemLoader('./templates'))  # 템플릿 폴더 경로 설정
    template = env.get_template('verification_email.html')  # 템플릿 파일 로드

    # 템플릿 렌더링
    html_content = template.render(verification_code=verification_code)

    # 이메일 발송
    message = MessageSchema(
        subject="이메일 인증해주세요.",
        recipients=[recipient_email],
        body=html_content,  # 렌더링된 HTML 본문 사용
        subtype="html"  # HTML 형식으로 전송
    )

    fm = FastMail(conf)
    await fm.send_message(message)
