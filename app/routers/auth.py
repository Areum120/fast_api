from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from bcrypt import checkpw
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import schemas, crud, models
from fastapi.security import OAuth2PasswordBearer
from app.database import SessionLocal
from app.dependencies import  get_db
from app.models import User
from app.token_utils import decode_jwt_token
from app.password_utils import verify_password
from typing import List
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 이미 있는 사용자 인증, 세션 관리, 토큰 발급 등 보안
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
@router.post("/login", response_model=schemas.TokenResponse)
def login(user: schemas.UserLogin, request: Request, db: Session = Depends(get_db), device_info=schemas.Device):

    # 현재 시간을 UTC로 변환하여 offset-aware로 설정
    now = datetime.now(timezone.utc)  # 이 부분에서 변수를 정의

    # 사용자 정보 조회
    db_user = db.query(models.User).filter(models.User.user_email == user.user_email).first()

    # 사용자 존재 여부 및 비밀번호 검증
    if not db_user or not checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # 기존 활성 토큰 확인 (이미 로그인된 경우 처리)
    existing_token = db.query(models.Token).filter(
        models.Token.user_id == db_user.user_id,
        models.Token.expires_at > now  # 현재 시간과 비교
    ).first()

    if existing_token:
        raise HTTPException(status_code=403, detail="User is already logged in")

    # 기기 정보에서 IP 주소 수집
    client_ip = request.client.host
    logger.info(f"Client IP: {client_ip}")  # IP 주소 로그 출력
    device_info.ip_address = client_ip

    # 기기 정보 유효성 검증
    # if not device_info.device_type or not device_info.device_name:
    #     raise HTTPException(status_code=400, detail="Device information is incomplete")

    # 기기 정보 등록 또는 업데이트
    crud.register_or_update_device(db, db_user.user_id, device_info)

    # # 기기 정보 제한 기능 활성화
    # if not crud.is_device_registered(db, db_user.user_id, device_info):
    #     raise HTTPException(status_code=403, detail="Unauthorized device")

    # 새로운 토큰 생성
    new_token = crud.create_token(db, db_user.user_id)
    return schemas.TokenResponse(token=new_token.token, expires_at=new_token.expires_at)

# 로그아웃(온라인 사용만)
@router.post("/logout")
def logout(request: schemas.LogoutRequest, db: Session = Depends(get_db)):
    # Extract the email from the request
    user_email = request.user_email

    db_user = db.query(models.User).filter(models.User.user_email == user_email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Invalidate the user's tokens
    db.query(models.Token).filter(models.Token.user_id == db_user.user_id).delete()
    db.commit()

    return {"detail": "Logged out successfully"}


# 현재 로그인 중인 사용자 확인 API

@router.get("/current_sessions", response_model=List[schemas.User])
def current_sessions(db: Session = Depends(get_db)):
    # 현재 시간 기준으로 만료되지 않은 토큰 조회
    now_kst = datetime.now(timezone.utc)
    active_tokens = db.query(models.Token.user_id).filter(models.Token.expires_at > now_kst).all()

    user_ids = [token.user_id for token in active_tokens]
    users = db.query(models.User).filter(models.User.user_id.in_(user_ids)).all()

    return users