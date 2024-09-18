from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.crud import create_verification_token
from app.database import SessionLocal
from app.dependencies import get_db
from app.email_utils import send_email
from app.models import (User, EmailVerificationToken)
from app.schemas import EmailSettings
from app.password_utils import get_password_hash, verify_password
from pydantic import EmailStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from starlette.responses import JSONResponse

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

@router.post("/register")
async def register_user(
    user: schemas.UserCreate, background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)):
    try:
        # 사용자 중복 확인
        existing_user = db.query(models.User).filter(models.User.username == user.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        if not user.password:
            raise HTTPException(status_code=400, detail="Password is required")

        # 비밀번호 해시화
        hashed_password = get_password_hash(user.password)

        # 새 사용자 생성
        new_user = models.User(
            name=user.name,
            username=user.username,
            password=hashed_password,  # 해시화된 비밀번호 저장
            phone_number=user.phone_number,
            email=user.email,
            email_verified=False  # 기본값은 False로 설정
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # DB에서 생성된 id 등 반영

        # 추천인 정보가 제공된 경우 처리
        if user.referrer_username:
            referrer = db.query(models.User).filter(models.User.username == user.referrer_username).first()
            if referrer:
                new_referral = models.Referral(
                    referrer_id=referrer.user_id,
                    referred_id=new_user.user_id
                )
                db.add(new_referral)
                db.commit()
                db.refresh(new_referral)

        # 이메일 인증 토큰 생성
        token = await create_verification_token(new_user.user_id)

        # 이메일 설정을 데이터베이스에서 조회
        email_settings = db.query(models.EmailSettings).first()  # EmailSettings를 모델에 추가해야 함

        # 이메일 인증 메일 발송
        if email_settings:
            background_tasks.add_task(send_email, email_settings, user.email, token)
        else:
            raise HTTPException(status_code=500, detail="Email settings not configured")

        return {"message": "Registration successful. Please check your email to verify your account."}

    except HTTPException as http_ex:
        db.rollback()
        raise http_ex

    except Exception as e:
        db.rollback()
        return {"message": f"Failed to register user: {str(e)}"}, 500

# ID 중복검사
@router.get("/check_username/{username}")
async def check_username(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username)
    if user:
        return {"exists": True}
    return {"exists": False}

# 이메일 인증 완료 API
@router.get("/verify")
async def verify_email(token: str, db: Session = Depends(get_db)):
    # 토큰을 DB에서 조회
    verification_token = db.query(EmailVerificationToken).filter(EmailVerificationToken.token == token).first()
    if not verification_token:
        raise HTTPException(status_code=400, detail="Invalid token")

    current_time = datetime.now(ZoneInfo("Asia/Seoul"))
    if verification_token.expires_at < current_time:
        raise HTTPException(status_code=400, detail="Token expired")

    # 사용자를 활성화
    user = db.query(User).filter(User.user_id == verification_token.user_id).first()
    if user.email_verified:
        return {"message": "Email already verified"}

    user.email_verified = True
    db.commit()

    return {"message": "Email verified successfully"}

