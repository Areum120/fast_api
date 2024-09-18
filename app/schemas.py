from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# 사용자 생성 시 필요한 스키마
class UserCreate(BaseModel):
    name: str
    username: str
    password: str = Field(..., min_length=8)  # 비밀번호는 필수이며 최소 길이 8자
    phone_number: str
    email: str
    referrer_username: Optional[str] = None  # 추천인 사용자명 (선택 사항)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

# 사용자 조회 시 사용하는 스키마
class User(BaseModel):
    id: int  # user_id를 id로 변경하여 DB 필드와 일치시킴
    name: str
    username: str
    # phone_number와 email 필드를 포함할지 선택적으로 결정
    phone_number: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
# 로그인
class UserLogin(BaseModel):
    username: str
    password: str

# 토큰
class TokenResponse(BaseModel):
    token: str
    expires_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    user_id: int
    token: str
    issued_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

# 사용자기기
class Device(BaseModel):
    # device_type: Optional[str] = None #python으로 수집
    # device_name: Optional[str] = None #python으로 수집
    ip_address: Optional[str] = None
    last_used: Optional[datetime] = None

# 추천인 조회 시 사용하는 스키마
class Referral(BaseModel):
    id: int
    referrer_id: int
    referred_id: int
    created_at: datetime

    class Config:
        from_attributes = True
