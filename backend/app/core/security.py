import os
import hashlib
import hmac
import json
import base64
import time
from typing import Dict, Any, Optional

SECRET_KEY = os.getenv("LUMIFACE_SECRET_KEY", "lumiface_kbeauty_diagnostic_secret_key_2026")
TOKEN_EXPIRY_SECONDS = 86400 * 7 # 7 days

def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with 16-byte random salt."""
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}${pwd_hash.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify raw password against stored salt$hash string."""
    try:
        parts = stored_hash.split('$')
        if len(parts) != 2:
            return False
        salt = bytes.fromhex(parts[0])
        original_hash = parts[1]
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(pwd_hash.hex(), original_hash)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any]) -> str:
    """Generate signed JWT-style session token with expiration timestamp."""
    payload = dict(data)
    payload["exp"] = int(time.time()) + TOKEN_EXPIRY_SECONDS
    
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signature_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify signed JWT-style session token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, sig_b64 = parts
        
        # Verify signature
        signature_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
        
        # Restore base64 padding
        sig_b64_padded = sig_b64 + "=" * (-len(sig_b64) % 4)
        actual_sig = base64.urlsafe_b64decode(sig_b64_padded.encode())
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        payload_b64_padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64_padded.encode())
        payload = json.loads(payload_bytes.decode())
        
        if payload.get("exp", 0) < int(time.time()):
            return None
            
        return payload
    except Exception:
        return None
