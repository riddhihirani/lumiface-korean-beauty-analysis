import pytest
import numpy as np
from app.services.skin_tone import skin_tone_analyzer
from app.services.recommendation_engine import recommendation_engine

def test_cielab_and_ita_calculation():
    # Synthetic warm golden-skin image sample (BGR: B=130, G=175, R=230)
    img_warm = np.full((300, 300, 3), (130, 175, 230), dtype=np.uint8)
    dummy_landmarks = [] # Empty landmarks will trigger fallback oval ROI

    res = skin_tone_analyzer.analyze(img_warm, dummy_landmarks)
    assert "shade" in res
    assert "undertone" in res
    assert "ita_angle" in res
    assert "lab_values" in res
    assert res["undertone"] == "Warm"
    assert res["seasonal_palette"] in ["Spring Light", "Autumn Warm"]

def test_cool_skin_sample():
    # Synthetic cool rosy skin sample (BGR: B=190, G=170, R=215)
    img_cool = np.full((300, 300, 3), (190, 170, 215), dtype=np.uint8)
    res = skin_tone_analyzer.analyze(img_cool, [])
    assert res["undertone"] in ["Cool", "Neutral"]

def test_lighting_color_cast_warning():
    # Severe warm yellow light cast (BGR: B=80, G=180, R=240 -> R/B > 1.75)
    img_cast = np.full((300, 300, 3), (80, 180, 240), dtype=np.uint8)
    res = skin_tone_analyzer.analyze(img_cast, [])
    assert res["color_analysis_warning"] is not None
    assert "Warm/yellow lighting cast" in res["color_analysis_warning"]

def test_delta_e_recommendation_scoring():
    # Test Lab distance matching algorithm
    warm_skin_lab = {"L": 70.0, "a": 12.0, "b": 18.0}
    recs_warm = recommendation_engine.get_makeup_recommendations("Warm", "Spring Light", warm_skin_lab)
    
    assert len(recs_warm) > 0
    top_rec = recs_warm[0]
    assert "match_score" in top_rec
    assert "compatibility_label" in top_rec
    assert top_rec["compatibility_label"] == "Estimated Compatibility Score (Lab Distance Matrix)"

    # Cool skin lab should yield different top recommendation score ordering
    cool_skin_lab = {"L": 65.0, "a": 16.0, "b": 6.0}
    recs_cool = recommendation_engine.get_makeup_recommendations("Cool", "Summer Cool", cool_skin_lab)
    
    # Top shade for cool skin should differ or have different Delta E score
    assert recs_cool[0]["id"] != recs_warm[0]["id"] or recs_cool[0]["match_score"] != recs_warm[0]["match_score"]
