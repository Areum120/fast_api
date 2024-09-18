# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app import schemas, crud, models
# from app.dependencies import  get_db
#
# router = APIRouter()
#
# # 사용자 정보 조회
# # 사용자가 자신의 정보를 확인할 수 있게 하며, 이를 위해 JWT 토큰을 사용해 인증된 사용자만 접근할 수 있도록 합니다.
# @router.get("/me", response_model=schemas.UserResponse)
# def get_user_info(current_user: models.User = Depends(get_current_user)):
#     return current_user
#
#
# # 사용자 정보 수정 (Update User Info)
# # 사용자가 자신의 프로필 정보를 수정하는 API.
# # 예를 들어 이름, 이메일, 전화번호 등을 수정할 수 있으며, 이 역시 인증이 필요합니다.
# @router.put("/me", response_model=schemas.UserResponse)
# def update_user_info(user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     return crud.update_user(db, current_user.user_id, user_update)
#
# # 비밀번호 변경 (Change Password)
# # 사용자가 기존 비밀번호를 변경할 수 있는 API.
# # 현재 비밀번호를 확인한 후 새로운 비밀번호로 업데이트하는 절차를 처리합니다.
# # python
# @router.put("/me/password", response_model=schemas.Message)
# def change_password(password_update: schemas.PasswordUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     return crud.change_user_password(db, current_user.user_id, password_update)
#
# # 사용자 계정 삭제 (Delete User Account)
# # 사용자가 자신의 계정을 삭제하는 API.
# # 인증된 사용자가 자신의 계정을 삭제할 수 있게 처리합니다.
# @router.delete("/me", response_model=schemas.Message)
# def delete_user_account(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     return crud.delete_user(db, current_user.user_id)
