import os
import uuid
from zoneinfo import ZoneInfo

import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict

from sqlalchemy.orm import session
# from app.models import EmailVerificationToken

# token encoding, decoding
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# 로그인 토큰 발급
def create_jwt_token(user_id: int) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {"sub": user_id, "exp": expiration}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt_token(token: str) -> Dict:
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_jwt
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

# 이메일 토큰 발급
# async def create_verification_token(user_id: int):
#     token = str(uuid.uuid4())
#     expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)  # 토큰 유효시간 5분
#     # 토큰을 데이터베이스에 저장 (여기서는 예시로 메모리 사용)
#     verification_token = EmailVerificationToken(user_id=user_id, token=token, expires_at=expires_at)
#     session.add(verification_token)
#     session.commit()
#     return token