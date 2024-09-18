from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 회원가입 비밀번호 해쉬화
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 사용자 로그인 시 비밀번호를 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
