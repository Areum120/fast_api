import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

def get_env_variable(name: str, default=None):
    return os.getenv(name, default)

async def send_email(recipient_email: str, token: str):
    conf = ConnectionConfig(
        MAIL_USERNAME=get_env_variable("MAIL_USERNAME"),
        MAIL_PASSWORD=get_env_variable("MAIL_PASSWORD"),
        MAIL_FROM=get_env_variable("MAIL_FROM"),
        MAIL_PORT=int(get_env_variable("MAIL_PORT", 587)),
        MAIL_SERVER=get_env_variable("MAIL_SERVER"),
        MAIL_TLS=get_env_variable("MAIL_TLS", "True") == "True",
        MAIL_SSL=get_env_variable("MAIL_SSL", "False") == "True",
        USE_CREDENTIALS=get_env_variable("USE_CREDENTIALS", "True") == "True",
        VALIDATE_CERTS=get_env_variable("VALIDATE_CERTS", "True") == "True"
    )

    # 이메일 발송
    message = MessageSchema(
        subject="이메일 인증해주세요.",
        recipients=[recipient_email],
        body=f"링크를 눌러 이메일 인증을 완료해주세요.: http://your-domain.com/verify?token={token}",
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
