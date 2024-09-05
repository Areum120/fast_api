from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .test import router
from .. import models, schemas, crud
from ..crud import create_user, add_referral
from ..dependencies import get_db
from ..models import User
from ..schemas import UserCreate


# # URL 경로 맵핑, HTTP 메서드 맵핑, 요청 파라미터 처리, 응답 반환
router = APIRouter(
    prefix="/users",# 이 라우터에 정의된 모든 경로의 앞에 /users를 자동으로 추가
    tags=["users"],# 공통 코드 반복 줄이고, 모든 엔드포인트에서 설정 자동 상속
    responses={404: {"description": "Not found"}},
)

@router.post("/register/")
async def register_user(user: UserCreate, recommender_username: Optional[str] = None, db: Session = Depends(get_db)):
    # 사용자 중복 확인
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # 비밀번호 암호화
    hashed_password = crud.get_password_hash(user.password)

    # 새 사용자 생성
    new_user = create_user(db, UserCreate(
        username=user.username,
        name=user.name,
        password=hashed_password,
        phone=user.phone,
        email=user.email
    ))

    # 추천인 정보 저장
    if recommender_username:
        recommender = db.query(User).filter(User.username == recommender_username).first()
        if recommender:
            add_referral(db, referrer_id=recommender.id, referee_id=new_user.id)
        else:
            raise HTTPException(status_code=400, detail="Recommender not found")

    return {"message": "Registration Successful"}


# 아이디 중복검사
@router.get("/check_username/{username}")
async def check_username(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username)
    if user:
        return {"exists": True}
    return {"exists": False}