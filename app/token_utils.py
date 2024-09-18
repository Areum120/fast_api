import os
import jwt
from datetime import datetime, timedelta
from typing import Dict

# token encoding, decoding
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_jwt_token(user_id: int) -> str:
    expiration = datetime.utcnow() + timedelta(hours=1)
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
