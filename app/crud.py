import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, session
from . import models, schemas
from app.models import Token, TokenRateLimit, User, EmailVerificationCode
from .password_utils import get_password_hash
from .token_utils import create_jwt_token
from app.token_rate_limit import TokenRateLimit as TokenRateLimitChecker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 사용자 생성
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        # name=user.name,
        user_email=user.user_email,
        password=hashed_password,  # 해시화된 비밀번호 저장
        phone_number=user.phone_number,
    )
    db.add(db_user)
    db.commit()
    return db_user

#사용자 조회 (email로 조회)
def get_user_by_user_email(db: Session, user_email: str):
    return db.query(models.User).filter(models.User.user_email == user_email).first()

# 토큰 생성
def create_token(db: Session, user_id: int) -> Token:
    # Rate limit 설정 및 체크
    rate_limit_checker = TokenRateLimitChecker(db=db, max_tokens=30, period=10)
    rate_limit_checker.check(user_id)  # Rate limit 체크

    now = datetime.now(timezone.utc)  # 현재 시간
    expiration = now + timedelta(minutes=30)  # 새 토큰의 만료 시간을 30분 후로 설정

    # 현재 사용자의 활성 토큰을 확인하여 이미 로그인 중인지 확인
    existing_tokens = db.query(Token).filter(
        Token.user_id == user_id,
        Token.expires_at > now
    ).all()

    if existing_tokens:
        print("Warning: User is already logged in.")

    # JWT 토큰 생성 (구현 필요)
    token_str = create_jwt_token(user_id)

    # 새 토큰 객체 생성
    token = Token(
        user_id=user_id,
        token=token_str,
        issued_at=now,
        expires_at=expiration,
    )

    try:
        # 새 토큰을 데이터베이스에 추가
        db.add(token)

        # 레이트 리미트 기록 추가 또는 업데이트
        upsert_token_rate_limit(db, user_id)

        db.commit()
        db.refresh(token)
    except IntegrityError as e:
        db.rollback()
        raise e

    return token

# token 생성 제한 관리
def upsert_token_rate_limit(db: Session, user_id: int):
    # 현재 시간
    now = datetime.now(timezone.utc)

    try:
        # 레이트 리미트 레코드를 삽입하거나 업데이트
        rate_limit = db.query(TokenRateLimit).filter_by(user_id=user_id).first()

        if rate_limit:
            # 레코드가 이미 존재하면 업데이트
            rate_limit.attempts += 1
            rate_limit.last_attempt = now
        else:
            # 레코드가 존재하지 않으면 새로 삽입
            new_rate_limit = TokenRateLimit(
                user_id=user_id,
                created_at=now,
                attempts=1,
                last_attempt=now
            )
            db.add(new_rate_limit)

        db.commit()
        db.refresh(rate_limit)  # 변경 사항 반영
        return rate_limit
    except IntegrityError as e:
        db.rollback()
        # 레코드가 이미 존재하는 경우 다시 시도
        rate_limit = db.query(TokenRateLimit).filter_by(user_id=user_id).first()
        if rate_limit:
            rate_limit.attempts += 1
            rate_limit.last_attempt = now
            db.commit()
            db.refresh(rate_limit)
        else:
            raise e

# token 삭제
def delete_token(db: Session, user_id: int):
    # 사용자 ID로 활성 토큰 조회
    tokens = db.query(models.Token).filter(
        models.Token.user_id == user_id,
        models.Token.expires_at > datetime.now(timezone.utc)
    ).all()

    # 활성 토큰이 있으면 삭제
    for token in tokens:
        db.delete(token)

    db.commit()


# 기기 CRUD
def register_device(db: Session, user_id: int, device_type: str, device_name: str, ip_address: str):
    device = db.query(models.UserDevice).filter(
        models.UserDevice.user_id == user_id,
        models.UserDevice.device_type == device_type,
        models.UserDevice.device_name == device_name
    ).first()

    if not device:
        device = models.UserDevice(user_id=user_id, device_type=device_type, device_name=device_name,
                                   ip_address=ip_address)
        db.add(device)
    device.last_used = datetime.now(timezone.utc)
    db.commit()
    db.refresh(device)
    return device

# 등록된 기기에서만 로그인을 허용하도록 설정
# def is_device_registered(db: Session, user_id: int, device_type: str, device_name: str) -> bool:
#     # 사용자가 등록한 기기 목록을 조회하여 기기가 등록되어 있는지 확인
#     device = db.query(models.UserDevice).filter(
#         models.UserDevice.user_id == user_id,
#         models.UserDevice.device_type == device_type,
#         models.UserDevice.device_name == device_name
#     ).first()
#     return device is not None

# 기기 정보 업데이트
def register_or_update_device(db: Session, user_id: int, device_info: schemas.Device):
    # 기기 정보를 확인합니다.
    device = db.query(models.UserDevice).filter(
        models.UserDevice.user_id == user_id,
        # python으로 수집
        # models.UserDevice.device_type == device_info.device_type,
        # models.UserDevice.device_name == device_info.device_name
    ).first()

    if device:
        # 기기 정보가 이미 등록되어 있는 경우, `last_used`를 현재 시각으로 업데이트합니다.
        device.last_used = datetime.now(timezone.utc)
    else:
        # 기기 정보가 등록되어 있지 않은 경우, 새 기기를 등록합니다.
        device = models.UserDevice(
            user_id=user_id,
            # device_type=device_info.device_type,#python으로 수집
            # device_name=device_info.device_name,#python으로 수집
            ip_address=device_info.ip_address,
            last_used= datetime.now(timezone.utc)
        )
        db.add(device)
    db.commit()
    db.refresh(device)
    return device


# 추천인 저장
def create_referral(db: Session, referrer_username: str, referred_username: str):
    # username을 저장
    referrer = db.query(models.User).filter(models.User.username == referrer_username).first()
    referred = db.query(models.User).filter(models.User.username == referred_username).first()

    if not referrer:
        raise HTTPException(status_code=404, detail="Referrer not found")
    if not referred:
        raise HTTPException(status_code=404, detail="Referred user not found")

    # username의 id를 저장
    new_referral = models.Referral(
        referrer_id=referrer.id,
        referred_id=referred.id
    )
    db.add(new_referral)
    db.commit()
    db.refresh(new_referral)

    return new_referral

# 추천인 조회
def get_referral_by_usernames(db: Session, referrer_username: str, referred_username: str):
    # model에 있는 username을 조회
    referrer = db.query(models.User).filter(models.User.username == referrer_username).first()
    referred = db.query(models.User).filter(models.User.username == referred_username).first()

    if not referrer or not referred:
        raise HTTPException(status_code=404, detail="One or both users not found")

    # 추천인이 있으면 referrals table의 id와 일치하는지 확인
    return db.query(models.Referral).filter(
        models.Referral.referrer_id == referrer.id,
        models.Referral.referred_id == referred.id
    ).first()

# 모든 추천인 관계를 조회, 데이터분석 및 관리자모드에서 일괄처리시 필요
def get_all_referrals(db: Session):
    return db.query(models.Referral).all()


# 이메일 인증 코드 저장
async def create_verification_code(db: Session, user_email: str, verification_code: str):
    # 이메일 소문자로 변환
    user_email = user_email.lower()

    # 현재 시간 가져오기
    now = datetime.now(timezone.utc)

    # 대소문자 구분하여 사용자 조회(email_verification_codes table에서 조회)
    existing_user = db.query(EmailVerificationCode).filter(EmailVerificationCode.user_email == user_email).first()

    # 인증 코드 조회 시 이메일을 소문자로 변환하여 비교
    existing_code_entry = db.query(EmailVerificationCode).filter(func.lower(EmailVerificationCode.user_email) == user_email).first()

    logger.info(f"Querying for user_email: {user_email}")
    logger.info(f"Existing user: {existing_user}")
    logger.info(f"Existing code entry: {existing_code_entry}")

    if existing_user:
        # 사용자가 존재하는 경우, 인증 코드가 이미 존재하는지 확인
        if existing_code_entry:
            # 인증 코드가 이미 존재하는 경우, 업데이트
            existing_code_entry.code = verification_code  # 코드 업데이트
            existing_code_entry.expires_at = now + timedelta(minutes=5)  # 유효 시간 업데이트
            existing_code_entry.created_at = now  # created_at 필드도 업데이트
            db.commit()
        else:
            # 새로운 인증 코드 생성
            new_code_entry = EmailVerificationCode(
                user_email=user_email,
                code=verification_code,
                created_at=now,  # created_at 필드 추가
                expires_at=now + timedelta(minutes=5)  # 코드 유효시간 5분
            )
            db.add(new_code_entry)
            db.commit()
    else:
        # 사용자가 존재하지 않을 경우, 새로운 인증 코드 생성
        new_code_entry = EmailVerificationCode(
            user_email=user_email,
            code=verification_code,
            created_at=now,  # created_at 필드 추가
            expires_at=now + timedelta(minutes=5)  # 코드 유효시간 5분
        )
        db.add(new_code_entry)
        db.commit()


# 이메일 인증 토큰 저장
# async def create_verification_token(db: Session, user_email: str):
#     # 사용자 조회
#     user = db.query(User).filter(User.user_email == user_email).first()
#
#     # 사용자가 존재하는 경우 예외 처리
#     if user:
#         raise ValueError("User already exists")
#
#     # 사용자 없을 때 이메일 인증 토큰 생성
#     token = str(uuid.uuid4())
#     expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)  # 토큰 유효시간 5분
#
#     verification_token = EmailVerificationToken(
#         token=token,
#         expires_at=expires_at
#     )
#     db.add(verification_token)
#     db.commit()
#     return token

# # 모든 사용자 조회
# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()
# # 사용자 업데이트
# def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
#     db_user = get_user_by_id(db, user_id)
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     for key, value in user_update.dict(exclude_unset=True).items():
#         setattr(db_user, key, value)
#
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# 사용자 조회 (ID로 조회)
def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

# 사용자 삭제(탈퇴 시)
def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted successfully"}

# 사용자 비밀번호 변경
