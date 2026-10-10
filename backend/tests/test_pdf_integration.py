import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.pdf_generator import pdf_report_generator

client = TestClient(app)

def get_sample_analysis_data():
    return {
        "analysis_id": "test-uuid-12345678-abc-def",
        "created_at": "2026-10-10T21:00:00Z",
        "detection_status": "face_detected",
        "lighting": {
            "is_valid": True,
            "brightness": 120.5,
            "contrast": 45.2,
            "blur_score": 150.0
        },
        "face_shape": {
            "face_shape": "oval",
            "ratios": {
                "face_aspect_ratio": 1.35,
                "jaw_to_cheek_ratio": 0.78,
                "forehead_to_cheek_ratio": 0.80
            },
            "measurements": {
                "face_length_px": 320.0,
                "forehead_width_px": 190.0,
                "cheekbone_width_px": 230.0,
                "jaw_width_px": 180.0
            },
            "reasoning": "Aspect ratio of 1.35 indicates balanced height with cheekbone width.",
            "description": "Proportional and balanced facial contours.",
            "styling_tips": ["Versatile face shape."],
            "limitations": "Heuristic shape estimation based on 2D projection.",
            "uncertainty_level": "Low"
        },
        "skin_tone": {
            "shade": "Fair / Light",
            "undertone": "Cool",
            "ita_angle": 48.5,
            "lab_values": {"L": 68.2, "a": 12.1, "b": 14.5},
            "seasonal_palette": "Summer Cool",
            "description": "Soft luminous cool skin spectrum.",
            "undertone_confidence": "High"
        },
        "color_palette": {
            "season": "Summer Cool",
            "title": "Summer Cool Palette",
            "description": "Soft muted cool pastel hues.",
            "best_colors": [
                {"name": "Soft Lavender", "hex": "#E5D9F2", "category": "best"},
                {"name": "Rose Pink", "hex": "#C86D7C", "category": "best"}
            ],
            "worst_colors": [
                {"name": "Mustard Yellow", "hex": "#E3A857", "category": "worst"}
            ]
        },
        "makeup_recommendations": [
            {
                "id": "lip_01",
                "name": "Velvet Rose Tint",
                "brand": "Peripera",
                "category": "lipstick",
                "shade_name": "Rose Nude #17",
                "hex_code": "#C86D7C",
                "match_score": 95.0,
                "reason": "Complements cool skin undertone.",
                "delta_e": 2.4
            }
        ],
        "eyewear_recommendations": [
            {
                "id": "eye_01",
                "frame_style": "Hexagonal Geometric Titanium",
                "category": "geometric",
                "description": "Architectural hexagonal wire frame.",
                "recommended_colors": ["Polished Silver", "Soft Grey"],
                "color_hex_swatches": ["#C0C0C0"],
                "match_score": 94.0,
                "suitability": "Highly Recommended",
                "compatibility_label": "Estimated Compatibility Score (Facial Geometry & Color Rules)",
                "reasoning": "Geometric angles complement balanced oval proportions."
            }
        ]
    }

def test_pdf_report_generator_full_payload():
    """Verify PDF generator produces valid PDF bytes for a complete diagnostic result."""
    data = get_sample_analysis_data()
    pdf_bytes = pdf_report_generator.generate(data)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF")

def test_pdf_report_generator_missing_optional_fields():
    """Verify PDF generator handles missing optional fields gracefully without crashing."""
    sparse_data = {
        "analysis_id": "sparse-id-9999",
        "created_at": "2026-10-10T21:00:00Z",
        "face_shape": {"face_shape": "round"},
        "skin_tone": {"seasonal_palette": "Spring Light"}
    }
    pdf_bytes = pdf_report_generator.generate(sparse_data, face_image_base64=None)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")

def get_test_auth_headers():
    import uuid
    unique_email = f"test_pdf_{uuid.uuid4().hex[:8]}@example.com"
    reg_payload = {"email": unique_email, "password": "Password123!", "full_name": "PDF Tester"}
    res = client.post("/api/auth/register", json=reg_payload)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_pdf_report_api_endpoint():
    """Test POST /api/report/generate returns 200 OK and PDF content attachment."""
    headers = get_test_auth_headers()
    payload = {
        "analysis_data": get_sample_analysis_data(),
        "face_image_base64": None
    }
    response = client.post("/api/report/generate", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "Korean_Beauty_Analysis_Report.pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")

def test_pdf_report_api_missing_data_error():
    """Test POST /api/report/generate returns 400 Bad Request when analysis_data is missing."""
    headers = get_test_auth_headers()
    response = client.post("/api/report/generate", json={}, headers=headers)
    assert response.status_code == 400
    assert "Missing analysis_data" in response.json()["detail"]
