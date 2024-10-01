from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.crud import  create_verification_code
from app.database import SessionLocal
from app.dependencies import get_db
from app.email_utils import send_email
from app.models import (User,  Referral, EmailVerificationCode)
from app.password_utils import get_password_hash, verify_password
from app.schemas import UserCreate, VerificationRequest
import random

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/register")
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        # 사용자 중복 확인
        existing_user = db.query(User).filter(User.user_email == user.user_email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        if not user.password:
            raise HTTPException(status_code=400, detail="Password is required")

        # 비밀번호 해시화
        hashed_password = get_password_hash(user.password)

        # 새 사용자 생성
        new_user = User(
            user_email=user.user_email,
            password=hashed_password,  # 해시화된 비밀번호 저장
            phone_number=user.phone_number,
            email_verified=False  # 기본값은 False로 설정
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # DB에서 생성된 id 등 반영

        # 추천인 정보가 제공된 경우 처리
        if user.referrer_username:
            referrer = db.query(User).filter(User.username == user.referrer_username).first()
            if referrer:
                new_referral = Referral(
                    referrer_id=referrer.user_id,
                    referred_id=new_user.user_id
                )
                db.add(new_referral)
                db.commit()
                db.refresh(new_referral)

        return {"message": "Registration successful. Please proceed with email verification."}

    except HTTPException as http_ex:
        db.rollback()
        raise http_ex

    except Exception as e:
        db.rollback()
        return {"message": f"Failed to register user: {str(e)}"}, 500

# email 인증 code 발송
@router.post("/send_verification_code")
async def send_verification_code(
        request: VerificationRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    user_email = request.user_email
    try:
        # 6자리 인증 코드 생성
        verification_code = str(random.randint(100000, 999999))

        # 인증 코드 저장 (사용자 존재 여부에 따라 처리)
        await create_verification_code(db, user_email, verification_code)

        # 이메일 인증 메일 발송 (비동기 백그라운드 작업)
        background_tasks.add_task(send_email, user_email, verification_code)

        return {"message": "Verification email sent. Please check your email for your verification code."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification code: {str(e)}")


# 이메일 인증 코드 조회
@router.get("/verify_code")
async def verify_code(email: str, code: str, db: Session = Depends(get_db)):
    # 코드와 이메일을 DB에서 조회
    verification_code_entry = db.query(EmailVerificationCode).filter(
        EmailVerificationCode.user_email == email,
        EmailVerificationCode.verification_code == code
    ).first()

    if not verification_code_entry:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    current_time = datetime.now(ZoneInfo("Asia/Seoul"))
    if verification_code_entry.expires_at < current_time:
        raise HTTPException(status_code=400, detail="Code expired")

    # 이메일 인증 완료
    user = db.query(User).filter(User.user_email == email).first()
    if user:
        user.email_verified = True
        db.commit()  # 변경 사항 커밋
    else:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Email verified successfully"}


# 이메일 인증 토큰 발송
# @router.post("/send_verification_token")
# async def send_verification_token(
#     request: VerificationRequest,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db)
# ):
#
#     user_email = request.user_email
#     try:
#         # 사용자 조회
#         user = db.query(User).filter(User.user_email == user_email).first()
#
#         # 사용자가 존재하는 경우
#         if user:
#             return {"message": "Email already exists. Please check your email for verification instructions."}
#
#         # 사용자가 존재하지 않는 경우, 이메일 인증 토큰 생성 및 발송
#         token = await create_verification_token(db, user_email)
#
#         # 이메일 인증 메일 발송 (비동기 백그라운드 작업)
#         background_tasks.add_task(send_email, user_email, token)
#
#         return {"message": "Verification email sent. Please check your email."}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to send verification token: {str(e)}")

# 이메일 인증 완료 API
# @router.get("/verify")
# async def verify_email(token: str, db: Session = Depends(get_db)):
#     # 토큰을 DB에서 조회
#     verification_token = db.query(EmailVerificationToken).filter(EmailVerificationToken.token == token).first()
#     if not verification_token:
#         raise HTTPException(status_code=400, detail="Invalid token")
#
#     current_time = datetime.now(ZoneInfo("Asia/Seoul"))
#     if verification_token.expires_at < current_time:
#         raise HTTPException(status_code=400, detail="Token expired")
#
#     # 사용자를 활성화
#     user = db.query(User).filter(User.user_id == verification_token.user_id).first()
#     if user.email_verified:
#         return {"message": "Email already verified"}
#
#     user.email_verified = True
#     db.commit()
#
#     return {"message": "Email verified successfully"}

