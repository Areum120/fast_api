import uvicorn
from fastapi import FastAPI
from app.routers import users, test, test_api

app = FastAPI()

# 라우터 등록
app.include_router(users.router)
# app.include_router(test.router)
# app.include_router(test_api.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
