import io
import cv2
import uuid
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_test_auth_headers():
    unique_email = f"test_analysis_{uuid.uuid4().hex[:8]}@example.com"
    reg_payload = {"email": unique_email, "password": "Password123!", "full_name": "Analysis Tester"}
    res = client.post("/api/auth/register", json=reg_payload)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def create_dummy_image_bytes(width=400, height=400, color=(200, 200, 200), fmt="JPEG") -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()

def test_invalid_file_type():
    headers = get_test_auth_headers()
    response = client.post(
        "/api/analysis/analyze",
        files={"file": ("test.txt", b"hello world text data", "text/plain")},
        headers=headers
    )
    assert response.status_code == 400
    assert "Unsupported image format" in response.json()["detail"]

def test_no_face_detected():
    headers = get_test_auth_headers()
    # Plain grey image has no face
    img_bytes = create_dummy_image_bytes(400, 400, color=(128, 128, 128))
    response = client.post(
        "/api/analysis/analyze",
        files={"file": ("no_face.jpg", img_bytes, "image/jpeg")},
        headers=headers
    )
    assert response.status_code == 422
    assert "No usable face detected" in response.json()["detail"]

def test_image_too_dark():
    headers = get_test_auth_headers()
    # Dark image (< 35 mean brightness)
    img_bytes = create_dummy_image_bytes(400, 400, color=(10, 10, 10))
    response = client.post(
        "/api/analysis/analyze",
        files={"file": ("dark.jpg", img_bytes, "image/jpeg")},
        headers=headers
    )
    assert response.status_code == 400
    assert "too dark" in response.json()["detail"].lower()

def test_file_size_exceeded():
    headers = get_test_auth_headers()
    # 11MB dummy payload
    large_bytes = b"0" * (11 * 1024 * 1024)
    response = client.post(
        "/api/analysis/analyze",
        files={"file": ("large.jpg", large_bytes, "image/jpeg")},
        headers=headers
    )
    assert response.status_code == 400
    assert "exceeds" in response.json()["detail"].lower()

def test_pdf_report_generation():
    headers = get_test_auth_headers()
    # Test /api/report/generate with valid payload
    mock_payload = {
        "analysis_data": {
            "face_shape": {
                "face_shape": "oval",
                "ratios": {"face_aspect_ratio": 1.35, "jaw_to_cheek_ratio": 0.78, "forehead_to_cheek_ratio": 0.80},
                "measurements": {"face_length_px": 320.0, "forehead_width_px": 190.0, "cheekbone_width_px": 230.0, "jaw_width_px": 180.0},
                "reasoning": "Aspect ratio of 1.35 indicates balanced proportions.",
                "description": "Balanced oval contours.",
                "styling_tips": ["Flatters oval glasses."],
                "limitations": "2D projection heuristic estimate.",
                "uncertainty_level": "Low"
            },
            "skin_tone": {
                "shade": "Fair / Light",
                "undertone": "Cool",
                "ita_angle": 48.5,
                "lab_values": {"L": 68.2, "a": 12.1, "b": 14.5},
                "seasonal_palette": "Summer Cool",
                "description": "Soft luminous cool tone."
            },
            "makeup_recommendations": [
                {
                    "id": "lip_02",
                    "name": "Velvet Fig Rose MLBB",
                    "brand": "Peripera",
                    "category": "lipstick",
                    "shade_name": "Rosy Nude #17",
                    "hex_code": "#C86D7C",
                    "match_score": 95.0,
                    "reason": "Muted rosy MLBB shade."
                }
            ]
        }
    }
    response = client.post("/api/report/generate", json=mock_payload, headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
