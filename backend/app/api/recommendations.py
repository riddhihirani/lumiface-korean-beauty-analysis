from fastapi import APIRouter
from app.services.recommendation_engine import recommendation_engine

router = APIRouter()

@router.get("/catalog/makeup")
def get_all_makeup_catalog():
    return recommendation_engine.makeup_shades

@router.get("/catalog/eyewear")
def get_all_eyewear_catalog():
    return recommendation_engine.eyewear_catalog

@router.get("/catalog/palettes")
def get_all_color_palettes():
    return recommendation_engine.color_palettes
