import os

# 환경변수 가져오기
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# 환경변수 값 출력
print(f"config, DB_HOST: {DB_HOST}")
print(f"config, DB_PORT: {DB_PORT}")
print(f"config, DB_NAME: {DB_NAME}")
print(f"config, DB_USER: {DB_USER}")
print(f"config, DB_PASSWORD: {DB_PASSWORD}")  # 민감한 정보이므로 실제로는 로그에 남기지 않는 것이 좋습니다.
