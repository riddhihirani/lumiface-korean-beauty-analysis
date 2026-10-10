import pytest
from app.services.recommendation_engine import recommendation_engine

def test_eyewear_categories_coverage():
    """Verify that all 7 frame categories are present in the catalog recommendations."""
    recs = recommendation_engine.get_eyewear_recommendations("oval", {"face_aspect_ratio": 1.35}, "Spring Light")
    assert len(recs) >= 7
    categories = {r["category"] for r in recs}
    expected_categories = {"round", "oval", "square", "rectangular", "cat-eye", "aviator", "geometric"}
    assert expected_categories.issubset(categories)

def test_eyewear_face_shape_differentiation_and_ranking():
    """Verify that distinct face shapes receive different top recommendations and different dynamic rankings."""
    # Round face shape (low aspect ratio 1.20)
    recs_round = recommendation_engine.get_eyewear_recommendations("round", {"face_aspect_ratio": 1.20, "jaw_to_cheek_ratio": 0.85}, "Summer Cool")
    # Square face shape (angular jaw 0.86)
    recs_square = recommendation_engine.get_eyewear_recommendations("square", {"face_aspect_ratio": 1.32, "jaw_to_cheek_ratio": 0.86}, "Autumn Warm")
    # Oblong face shape (high aspect ratio 1.50)
    recs_oblong = recommendation_engine.get_eyewear_recommendations("oblong", {"face_aspect_ratio": 1.50, "jaw_to_cheek_ratio": 0.78}, "Winter Vivid")

    # Round face top recommendation should be rectangular or square (angular structure)
    assert recs_round[0]["category"] in ["rectangular", "square", "geometric"]
    # Round face lowest recommendation should be round (curved)
    assert recs_round[-1]["category"] in ["round", "oval"]

    # Square face top recommendation should be round, oval, or cat-eye (softening curves)
    assert recs_square[0]["category"] in ["round", "oval", "cat-eye"]
    # Square face lowest recommendation should be square or rectangular
    assert recs_square[-1]["category"] in ["square", "rectangular"]

    # Oblong face top recommendation should be oversized square or geometric (horizontal balance)
    assert recs_oblong[0]["category"] in ["square", "geometric", "round"]

    # Ensure ranking orders are distinct across round, square, and oblong shapes
    round_order = [r["id"] for r in recs_round]
    square_order = [r["id"] for r in recs_square]
    assert round_order != square_order

def test_eyewear_dynamic_reasoning_includes_measurements():
    """Verify that geometric reasoning dynamically embeds measured ratios and custom shape explanations."""
    recs = recommendation_engine.get_eyewear_recommendations(
        "square", 
        {"face_aspect_ratio": 1.32, "jaw_to_cheek_ratio": 0.86, "forehead_to_cheek_ratio": 0.82}, 
        "Spring Light"
    )
    top_rec = recs[0]
    assert "0.86" in top_rec["reasoning"] or "jaw" in top_rec["reasoning"].lower()
    assert top_rec["match_score"] >= 88.0

def test_eyewear_missing_or_uncertain_input_handling():
    """Verify that missing/None face shape indicates neutral baseline limitations rather than silently defaulting to oval."""
    recs = recommendation_engine.get_eyewear_recommendations(None, None, "Summer Cool")
    assert len(recs) >= 7
    top_rec = recs[0]
    assert top_rec["suitability"] == "General Recommendation"
    assert "Unverified" in top_rec["compatibility_label"] or "Neutral" in top_rec["compatibility_label"]
    assert "unverified" in top_rec["reasoning"].lower()

def test_eyewear_seasonal_color_matching():
    """Verify frame color suggestions change according to the user's analyzed personal color season."""
    recs_spring = recommendation_engine.get_eyewear_recommendations("square", {"jaw_to_cheek_ratio": 0.86}, "Spring Light")
    recs_winter = recommendation_engine.get_eyewear_recommendations("square", {"jaw_to_cheek_ratio": 0.86}, "Winter Vivid")

    spring_top_colors = recs_spring[0]["recommended_colors"]
    winter_top_colors = recs_winter[0]["recommended_colors"]
    
    assert len(spring_top_colors) > 0
    assert len(winter_top_colors) > 0
    assert spring_top_colors != winter_top_colors
