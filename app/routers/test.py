from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies import get_db

router = APIRouter()

@router.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        # 간단한 쿼리 실행
        result = db.execute("SELECT 1").fetchone()
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
