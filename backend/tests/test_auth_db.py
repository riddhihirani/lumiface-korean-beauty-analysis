import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password, verify_password

client = TestClient(app)

def test_password_hashing_and_verification():
    raw_password = "SecretPassword123!"
    hashed = hash_password(raw_password)
    
    assert hashed != raw_password
    assert "$" in hashed
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_user_registration_and_login_flow():
    import uuid
    test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    test_name = "Min-ah Park"
    test_pwd = "SecurePassword123"
    
    # 1. Register new user
    reg_payload = {
        "email": test_email,
        "password": test_pwd,
        "full_name": test_name
    }
    response = client.post("/api/auth/register", json=reg_payload)
    assert response.status_code == 200
    reg_data = response.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == test_email
    assert reg_data["user"]["full_name"] == test_name
    
    token = reg_data["access_token"]
    
    # 2. Duplicate registration attempt should fail
    dup_response = client.post("/api/auth/register", json=reg_payload)
    assert dup_response.status_code == 400
    assert "already exists" in dup_response.json()["detail"]
    
    # 3. Login with correct credentials
    login_response = client.post("/api/auth/login", json={"email": test_email, "password": test_pwd})
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["user"]["full_name"] == test_name
    
    # 4. Login with incorrect password
    bad_login = client.post("/api/auth/login", json={"email": test_email, "password": "WrongPassword"})
    assert bad_login.status_code == 401
    
    # 5. Fetch profile via /api/auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["full_name"] == test_name
    
    # 6. Update profile via /api/auth/profile
    update_response = client.put("/api/auth/profile", json={"full_name": "Min-ah Park Updated"}, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Min-ah Park Updated"

def test_forgot_password_endpoint():
    response = client.post("/api/auth/forgot-password", json={"email": "user@example.com"})
    assert response.status_code == 200
    assert "SMTP" in response.json()["message"] or "notice" in response.json()["status"]

def test_protected_routes_require_authentication():
    # 1. Unauthenticated /api/analysis/analyze request should return 401
    resp_analyze_unauth = client.post("/api/analysis/analyze")
    assert resp_analyze_unauth.status_code == 401
    assert "Authentication token required" in resp_analyze_unauth.json()["detail"]

    # 2. Unauthenticated /api/report/generate request should return 401
    resp_report_unauth = client.post("/api/report/generate", json={"analysis_data": {}})
    assert resp_report_unauth.status_code == 401
    assert "Authentication token required" in resp_report_unauth.json()["detail"]

    # 3. Authenticated requests with valid token pass auth check
    unique_email = f"prot_user_{uuid.uuid4().hex[:8]}@example.com"
    reg_payload = {
        "email": unique_email,
        "password": "Password123!",
        "full_name": "Protected User"
    }
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 200
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # With auth headers, /generate with missing analysis_data gives 400 (validation error), NOT 401 (auth error)
    report_auth_resp = client.post("/api/report/generate", json={}, headers=headers)
    assert report_auth_resp.status_code == 400

def test_auth_failure_cases_and_unknown_email():
    """Verify unknown email, incorrect password, duplicate registration, and case-insensitive email login."""
    unique_email = f"CaseTest_{uuid.uuid4().hex[:8]}@LumiFace.COM"
    pwd = "StrongPassword99!"
    name = "Case Insensitive User"

    # 1. Register with mixed case email
    reg = client.post("/api/auth/register", json={"email": unique_email, "password": pwd, "full_name": name})
    assert reg.status_code == 200

    # 2. Duplicate registration attempt with lowercase email -> should fail 400
    dup = client.post("/api/auth/register", json={"email": unique_email.lower(), "password": pwd, "full_name": name})
    assert dup.status_code == 400
    assert "already exists" in dup.json()["detail"]

    # 3. Login with lowercase email -> should succeed 200
    login_lower = client.post("/api/auth/login", json={"email": unique_email.lower(), "password": pwd})
    assert login_lower.status_code == 200
    assert "access_token" in login_lower.json()

    # 4. Login with uppercase email -> should succeed 200
    login_upper = client.post("/api/auth/login", json={"email": unique_email.upper(), "password": pwd})
    assert login_upper.status_code == 200

    # 5. Login with incorrect password -> should fail 401
    bad_pwd = client.post("/api/auth/login", json={"email": unique_email, "password": "WrongPassword!"})
    assert bad_pwd.status_code == 401
    assert "Incorrect email or password" in bad_pwd.json()["detail"]

    # 6. Login with unknown email -> should fail 401
    unknown = client.post("/api/auth/login", json={"email": "nonexistent_email_999@domain.com", "password": pwd})
    assert unknown.status_code == 401
    assert "Incorrect email or password" in unknown.json()["detail"]


