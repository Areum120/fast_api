from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
import bcrypt

# 사용자 생성
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        name=user.name,
        username=user.username,
        password=user.password,
        phone=user.phone,
        email=user.email
    )
    db.add(db_user)  # 데이터베이스 세션에 사용자 객체 추가
    db.commit()  # 데이터베이스에 변경사항 커밋
    db.refresh(db_user)  # 커밋 후 새로 생성된 사용자 객체를 새로고침
    return db_user  # 새로 생성된 사용자 객체 반환

# 비밀번호 해쉬로 저장
def get_password_hash(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

#사용자 조회 (username(ID)으로 조회)
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# 추천인 저장
def get_user_id_by_username(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    return user.id if user else None

def add_referral(db: Session, recommender_username: str, new_user_username: str):
    referrer_id = get_user_id_by_username(db, recommender_username)
    referree_id = get_user_id_by_username(db, new_user_username)

    if not referrer_id or not referree_id:
        raise ValueError("One or both of the usernames do not exist")

    referral = models.Referral(
        referrer_id=referrer_id,
        referree_id=referree_id,
        referred_at=datetime.utcnow()
    )
    db.add(referral)
    db.commit()
    db.refresh(referral)
    return referral


# 사용자 조회 (ID로 조회)
def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

# 모든 사용자 조회
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# 사용자 업데이트
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

# 사용자 삭제
def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted successfully"}
