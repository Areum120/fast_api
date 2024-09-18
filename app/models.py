# app/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, func
from sqlalchemy.orm import relationship
from .database import Base  # Base를 database.py에서 가져옵니다.

# 사용자 관리 테이블
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    email_verified = Column(Boolean, default=False)  # 이메일 인증 여부
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 유저가 추천한 사용자 목록
    referrals = relationship("Referral", back_populates="referrer", foreign_keys="[Referral.referrer_id]")
    # 유저가 추천받은 사용자 목록
    referred_by = relationship("Referral", back_populates="referred_user", foreign_keys="[Referral.referred_id]")

    # 토큰
    tokens = relationship("Token", back_populates="user")
    # 토큰 생성 빈도 관리
    rate_limits = relationship("TokenRateLimit", back_populates="user")
    # 기기
    devices = relationship("UserDevice", back_populates="user")
    # 유저의 구독 내역
    subscriptions = relationship("Subscription", back_populates="user")
    # 유저의 결제 내역
    payments = relationship("Payment", back_populates="user")

# login token
class Token(Base):
    __tablename__ = "tokens"
    token_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    token = Column(String, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="tokens")

# login token 생성 빈도 관리
class TokenRateLimit(Base):
    __tablename__ = "token_rate_limits"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    attempts = Column(Integer, default=0)
    last_attempt = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="rate_limits")

# 이메일 인증 토큰 테이블
class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"
    token_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    token = Column(String, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="email_verification_tokens")




# 사용자 기기 관리
class UserDevice(Base):
    __tablename__ = "user_devices"
    device_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    # python으로 수집
    # device_type = Column(String)
    # device_name = Column(String)
    ip_address = Column(String)
    last_used = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="devices")

# 구독
class Subscription(Base):
    __tablename__ = "subscriptions"
    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    plan_name = Column(String, nullable=False)  # 예: Basic, Premium 등
    status = Column(String, nullable=False)  # 예: active, canceled 등
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    user = relationship("User", back_populates="subscriptions")

# 결제
class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # 예: credit card, paypal 등
    payment_date = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    user = relationship("User", back_populates="payments")

# 추천인 관리
class Referral(Base):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey('users.user_id'))
    referred_id = Column(Integer, ForeignKey('users.user_id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    referrer = relationship("User", back_populates="referrals", foreign_keys=[referrer_id])
    referred_user = relationship("User", back_populates="referred_by", foreign_keys=[referred_id])