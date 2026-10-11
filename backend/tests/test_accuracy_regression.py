import pytest
import numpy as np
import cv2
import math
from app.services.face_shape import face_shape_estimator, FaceShapeEstimator
from app.services.skin_tone import skin_tone_analyzer, SkinToneAnalyzer
from app.services.recommendation_engine import recommendation_engine, RecommendationEngine

def generate_mock_landmarks(height=380.0, cheek_w=290.0, forehead_w=245.0, jaw_w=235.0, roll_deg=0.0):
    """
    Generate synthetic 468 MediaPipe FaceMesh landmarks with controllable anthropometric proportions and head roll.
    """
    cx, cy = 300.0, 300.0
    rad = math.radians(roll_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)

    def rot(x, y):
        rx = x * cos_a - y * sin_a + cx
        ry = x * sin_a + y * cos_a + cy
        return {"x": rx, "y": ry, "z": 0.0, "norm_x": rx / 600.0, "norm_y": ry / 600.0}

    landmarks = [{"x": cx, "y": cy, "z": 0.0, "norm_x": 0.5, "norm_y": 0.5} for _ in range(468)]
    
    # Trichion (10) and Menton (152)
    landmarks[10] = rot(0, -height / 2.0)
    landmarks[152] = rot(0, height / 2.0)

    # Zygomatic arches (234, 454)
    landmarks[234] = rot(-cheek_w / 2.0, 0)
    landmarks[454] = rot(cheek_w / 2.0, 0)

    # Temples / Bitemporal (54, 284)
    landmarks[54] = rot(-forehead_w / 2.0, -height * 0.28)
    landmarks[284] = rot(forehead_w / 2.0, -height * 0.28)

    # Mandibular gonion angles (58, 288)
    landmarks[58] = rot(-jaw_w / 2.0, height * 0.28)
    landmarks[288] = rot(jaw_w / 2.0, height * 0.28)

    # Eyes outer corners (33, 263) for roll detection
    landmarks[33] = rot(-75.0, -30.0)
    landmarks[263] = rot(75.0, -30.0)

    # Nose tip (1)
    landmarks[1] = rot(0, 10.0)

    return landmarks

def test_head_roll_invariance():
    """Verify that head-roll normalization eliminates tilt distortion."""
    # Frontal upright oval face
    lms_upright = generate_mock_landmarks(height=390.0, cheek_w=288.0, forehead_w=245.0, jaw_w=230.0, roll_deg=0.0)
    res_upright = face_shape_estimator.estimate_shape(lms_upright)

    # Same face tilted by 12 degrees
    lms_tilted = generate_mock_landmarks(height=390.0, cheek_w=288.0, forehead_w=245.0, jaw_w=230.0, roll_deg=12.0)
    res_tilted = face_shape_estimator.estimate_shape(lms_tilted)

    assert res_upright["face_shape"] == res_tilted["face_shape"]
    assert abs(res_upright["ratios"]["face_aspect_ratio"] - res_tilted["ratios"]["face_aspect_ratio"]) < 0.02
    assert abs(res_upright["ratios"]["jaw_to_cheek_ratio"] - res_tilted["ratios"]["jaw_to_cheek_ratio"]) < 0.02
    assert "Head tilt detected" in res_tilted["limitations"]

def test_geometric_face_shapes_differentiation():
    """Verify that distinct anthropometric proportions produce distinct shape classifications."""
    # Oval: balanced (aspect ~1.35, jaw/cheek ~0.80)
    oval_lms = generate_mock_landmarks(height=390.0, cheek_w=288.0, forehead_w=245.0, jaw_w=230.0)
    res_oval = face_shape_estimator.estimate_shape(oval_lms)
    assert res_oval["face_shape"] == "oval"

    # Oblong: elongated (aspect ~1.55)
    oblong_lms = generate_mock_landmarks(height=450.0, cheek_w=288.0, forehead_w=242.0, jaw_w=230.0)
    res_oblong = face_shape_estimator.estimate_shape(oblong_lms)
    assert res_oblong["face_shape"] == "oblong"

    # Round: compact/equal (aspect ~1.12)
    round_lms = generate_mock_landmarks(height=320.0, cheek_w=290.0, forehead_w=245.0, jaw_w=235.0)
    res_round = face_shape_estimator.estimate_shape(round_lms)
    assert res_round["face_shape"] == "round"

    # Square: wide angular jaw (jaw/cheek ~0.91)
    square_lms = generate_mock_landmarks(height=355.0, cheek_w=290.0, forehead_w=258.0, jaw_w=264.0)
    res_square = face_shape_estimator.estimate_shape(square_lms)
    assert res_square["face_shape"] == "square"

def test_makeup_scoring_avoids_identical_saturation():
    """Verify that individuals with different skin Lab values get distinct, personalized scores without flat 98.0 capping."""
    skin_a = {"L": 70.0, "a": 11.0, "b": 17.0}
    skin_b = {"L": 62.0, "a": 15.0, "b": 23.0}

    recs_a = recommendation_engine.get_makeup_recommendations("Warm", "Spring Light", skin_a)
    recs_b = recommendation_engine.get_makeup_recommendations("Warm", "Spring Light", skin_b)

    # Scores should not all be 98.0
    scores_a = [r["match_score"] for r in recs_a[:5]]
    assert len(set(scores_a)) > 1, f"All top scores are identical: {scores_a}"

    # Rankings and individual scores should differ between skin A and skin B
    scores_b = [r["match_score"] for r in recs_b[:5]]
    assert scores_a != scores_b

def test_lighting_compensation_preserves_neutral_undertone():
    """Verify that warm ambient lighting does not falsely force a neutral skin tone into Warm."""
    # Neutral skin tone (daylight)
    neutral_bgr = np.full((150, 150, 3), (160, 180, 220), dtype=np.uint8)
    res_daylight = skin_tone_analyzer.analyze(neutral_bgr, [])
    assert res_daylight["undertone"] == "Neutral"

    # Same skin under warm indoor bulb (R increased, B decreased: R/B ~ 1.76)
    warm_lamp_bgr = np.full((150, 150, 3), (120, 180, 235), dtype=np.uint8)
    res_lamp = skin_tone_analyzer.analyze(warm_lamp_bgr, [])
    assert res_lamp["undertone"] in ["Neutral", "Cool"], f"Warm lamp falsely classified as: {res_lamp['undertone']}"
    assert res_lamp["color_analysis_warning"] is not None
    assert "Warm/yellow lighting cast" in res_lamp["color_analysis_warning"]
