from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from app.models import TokenRateLimit as TokenRateLimitModel

# 로그인 시 토큰 생성 제한
class TokenRateLimit:
    def __init__(self, db: Session, max_tokens: int, period: int):
        self.db = db
        self.max_tokens = max_tokens
        self.period = period  # 기간을 분 단위로 설정
        # 현재 시간을 UTC로 변환하여 offset-aware로 설정
        self.now = datetime.now(timezone.utc)
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
            # last_attempt을 offset-aware로 변환
            if rate_limit.last_attempt.tzinfo is None:
                last_attempt_aware = rate_limit.last_attempt.replace(tzinfo=timezone.utc)
            else:
                last_attempt_aware = rate_limit.last_attempt  # 이미 offset-aware인 경우

            if (self.now - last_attempt_aware).total_seconds() >= self.period * 60:
                rate_limit.attempts = 0
                rate_limit.last_attempt = self.now  # 새로운 시도로 업데이트
        else:
            rate_limit = TokenRateLimitModel(user_id=user_id, last_attempt=self.now, attempts=0)
            self.db.add(rate_limit)

        rate_limit.attempts += 1
        self.db.commit()