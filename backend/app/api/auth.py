from fastapi import APIRouter, HTTPException, status, Depends, Header
from app.models.schemas import UserCreate, UserLogin, Token, UserProfileResponse, UserProfileUpdate, ForgotPasswordRequest, ForgotPasswordResponse
from app.db.database import get_db_connection
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger("lumiface.auth")

def _mask_email(email: str) -> str:
    """Safely mask email address for diagnostic logs without revealing user identity."""
    if not email or "@" not in email:
        return "***"
    parts = email.split("@")
    user_part = parts[0]
    masked_user = user_part[0] + "***" if len(user_part) > 1 else "*"
    return f"{masked_user}@{parts[1]}"

def get_authenticated_user_email(authorization: Optional[str] = Header(None)) -> str:
    """Dependency to extract and verify user email from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required. Please sign in to access this resource."
        )
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or "email" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token. Please sign in again."
        )
    
    return payload["email"]

@router.post("/register", response_model=Token)
def register_user(user: UserCreate):
    email_clean = user.email.strip().lower()
    masked = _mask_email(email_clean)
    logger.info(f"Processing registration request for email: {masked}")

    if not email_clean or "@" not in email_clean:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    if not user.full_name or len(user.full_name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Full name must be at least 2 characters.")
    if not user.password or len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email_clean,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        logger.warning(f"Registration failed: Account with email {masked} already exists.")
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")
    
    pwd_hash = hash_password(user.password)
    name_clean = user.full_name.strip()
    
    cursor.execute(
        "INSERT INTO users (email, full_name, password_hash) VALUES (?, ?, ?)",
        (email_clean, name_clean, pwd_hash)
    )
    conn.commit()
    
    cursor.execute("SELECT id, email, full_name, created_at FROM users WHERE LOWER(email) = LOWER(?)", (email_clean,))
    row = cursor.fetchone()
    conn.close()
    
    logger.info(f"Registration successful for user ID: {row['id']} ({masked})")

    user_resp = UserProfileResponse(
        id=row["id"],
        email=row["email"],
        full_name=row["full_name"],
        created_at=str(row["created_at"])
    )
    
    access_token = create_access_token({"sub": str(row["id"]), "email": row["email"], "name": row["full_name"]})
    return Token(access_token=access_token, user=user_resp)

@router.post("/login", response_model=Token)
def login_user(user: UserLogin):
    email_clean = user.email.strip().lower()
    masked = _mask_email(email_clean)
    logger.info(f"Processing login request for email: {masked}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, password_hash, created_at FROM users WHERE LOWER(email) = LOWER(?)", (email_clean,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        logger.warning(f"Login failed Stage 1: User account not found in database ({masked})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password. Please check your credentials."
        )
    
    if not verify_password(user.password, row["password_hash"]):
        logger.warning(f"Login failed Stage 2: Password verification failed for user ID {row['id']} ({masked})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password. Please check your credentials."
        )
    
    logger.info(f"Login successful Stage 3: Authenticated user ID {row['id']} ({masked})")

    user_resp = UserProfileResponse(
        id=row["id"],
        email=row["email"],
        full_name=row["full_name"],
        created_at=str(row["created_at"])
    )
    
    access_token = create_access_token({"sub": str(row["id"]), "email": row["email"], "name": row["full_name"]})
    return Token(access_token=access_token, user=user_resp)

@router.get("/me", response_model=UserProfileResponse)
def get_user_profile(user_email: str = Depends(get_authenticated_user_email)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, created_at FROM users WHERE LOWER(email) = LOWER(?)", (user_email,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="User account not found.")
        
    return UserProfileResponse(
        id=row["id"],
        email=row["email"],
        full_name=row["full_name"],
        created_at=str(row["created_at"])
    )

@router.put("/profile", response_model=UserProfileResponse)
def update_user_profile(
    body: UserProfileUpdate,
    user_email: str = Depends(get_authenticated_user_email)
):
    new_name = body.full_name.strip()
    if len(new_name) < 2:
        raise HTTPException(status_code=400, detail="Full name must be at least 2 characters.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET full_name = ?, updated_at = CURRENT_TIMESTAMP WHERE LOWER(email) = LOWER(?)", (new_name, user_email))
    conn.commit()
    
    cursor.execute("SELECT id, email, full_name, created_at FROM users WHERE LOWER(email) = LOWER(?)", (user_email,))
    row = cursor.fetchone()
    conn.close()
    
    return UserProfileResponse(
        id=row["id"],
        email=row["email"],
        full_name=row["full_name"],
        created_at=str(row["created_at"])
    )

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(body: ForgotPasswordRequest):
    email_clean = body.email.strip().lower()
    if not email_clean or "@" not in email_clean:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
        
    return ForgotPasswordResponse(
        status="notice",
        message=f"Password reset request received for {email_clean}. Automated email dispatch requires active SMTP configuration. Please contact your system administrator or support team to reset your credentials."
    )
