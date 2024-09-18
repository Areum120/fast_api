from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import SessionLocal
from app.dependencies import get_db
from app.models import User
from app.password_utills import get_password_hash, verify_password

# URL 경로 맵핑, HTTP 메서드 맵핑, 요청 파라미터 처리, 응답 반환
router = APIRouter(
       responses={404: {"description": "Not found"}},
)

# 회원가입, 새로운 사용자 데이터 수집 및 검증 (이메일 인증, 비밀번호 규칙)
@router.post("/register")
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
            email=user.email
        )

        db.add(new_user)

        # 변경 사항을 데이터베이스에 커밋
        db.commit()
        db.refresh(new_user)  # db_user 객체를 최신 상태로 갱신 (DB에서 생성된 id 등 반영)

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

        return {"message": "Registration Successful"}

    except HTTPException as http_ex:
        db.rollback()
        raise http_ex

    except Exception as e:
        db.rollback()
        return {"message": f"Failed to register user: {str(e)}"}, 500

@router.get("/check_username/{username}")
async def check_username(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username)
    if user:
        return {"exists": True}
    return {"exists": False}
