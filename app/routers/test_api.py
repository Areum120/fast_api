import requests

# 아이디 중복 확인
response = requests.get("http://127.0.0.1:8000/check_username/testuser")
print(response.status_code, response.json())

# 회원가입 요청
response = requests.post("http://127.0.0.1:8000/register/", json={
    "name": "Test Name",
    "username": "testuser",
    "password": "testpassword",
    "phone": "1234567890",
    "email": "test@example.com",
    "recommender": "recommender_name"
})
print(response.status_code, response.json())
