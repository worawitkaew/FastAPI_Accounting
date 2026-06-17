
import pytest

from main import app
# from .test_main import test_client

from fastapi.testclient import TestClient

@pytest.fixture
def test_client():
  
    client = TestClient(app)
    return client
    
@pytest.mark.asyncio
def test_ProductType1(test_client):

    response = test_client.get("/test")
    assert response.json() == {
    "message_test": "Hello World_test"
    }

@pytest.fixture
def get_token(test_client):
    # ส่ง request สำหรับ login และดึง token
    login_data = {"username": "username_test", "password": "password_test"}
    response = test_client.post("/routes/pre_route/token", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]  # หรือใช้ข้อมูลที่ส่งกลับจาก API ตามที่ต้องการ

# ทดสอบ API ที่ต้องการ authentication
@pytest.mark.asyncio
def test_login(test_client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = test_client.get("/", headers=headers)
    assert response.json() == {
  "message": "Hello World",
  "current_user": {
    "username": "username_test",
    "disabled": False
  }
}