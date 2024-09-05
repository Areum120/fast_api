from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

# 사용자 관리 테이블
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)
    phone = Column(String)
    email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    referrals_given = relationship("Referral", foreign_keys="Referral.referrer_id", back_populates="referrer")
    referrals_received = relationship("Referral", foreign_keys="Referral.referree_id", back_populates="referree")

# 추천인 관리 테이블
class Referral(Base):
    __tablename__ = "referrals"

    referral_id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    referree_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    referred_at = Column(DateTime, default=datetime.utcnow)

    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_given")
    referree = relationship("User", foreign_keys=[referree_id], back_populates="referrals_received")
