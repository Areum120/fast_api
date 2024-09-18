from datetime import datetime, timedelta
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from app.models import TokenRateLimit as TokenRateLimitModel

class TokenRateLimit:
    def __init__(self, db: Session, max_tokens: int, period: int):
        self.db = db
        self.max_tokens = max_tokens
        self.period = period  # 기간을 분 단위로 설정
        self.now = datetime.utcnow()
        self.start_time = self.now - timedelta(minutes=self.period)

    def check(self, user_id: int):
        # 특정 기간 동안 사용자가 생성한 토큰 수를 계산
        token_count = self.db.query(TokenRateLimitModel).filter(
            TokenRateLimitModel.user_id == user_id,
            TokenRateLimitModel.created_at >= self.start_time
        ).count()

        if token_count >= self.max_tokens:
            raise HTTPException(status_code=429, detail="Too many requests, try again later.")

        # Rate limit 기록 추가
        rate_limit = self.db.query(TokenRateLimitModel).filter_by(user_id=user_id).first()
        if rate_limit:
            if (self.now - rate_limit.last_attempt).total_seconds() >= self.period * 60:
                rate_limit.attempts = 0
                rate_limit.last_attempt = self.now
        else:
            rate_limit = TokenRateLimitModel(user_id=user_id, last_attempt=self.now, attempts=0)
            self.db.add(rate_limit)

        rate_limit.attempts += 1
        self.db.commit()
