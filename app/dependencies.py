from sqlalchemy.orm import Session
from .database import SessionLocal

# astAPI에서 데이터베이스 세션 생성과 닫기 위해 설정.
# FastAPI의 Depends 통해 엔드포인트에 주입됨.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
