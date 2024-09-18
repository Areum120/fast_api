from fastapi import FastAPI, Depends
from app.routers import register, auth

app = FastAPI()

# 라우터 등록

# @app.get("/check_username/{username}")
# async def root():
#     return {"username": "test"}
(app.include_router(register.router))
(app.include_router(auth.router))


# from app.database import init_db
#
# if __name__ == "__main__":
#     init_db()