from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class HealthResponse(BaseModel):
    status: str
    version: str
    service: str

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: str

class UserProfileUpdate(BaseModel):
    full_name: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ForgotPasswordResponse(BaseModel):
    message: str
    status: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse

class LightingQuality(BaseModel):
    is_valid: bool
    brightness: float
    contrast: float
    blur_score: float
    warning: Optional[str] = None

class FaceShapeResult(BaseModel):
    face_shape: str # oval, round, square, heart, oblong, diamond
    ratios: Dict[str, float]
    measurements: Dict[str, float]
    reasoning: str
    description: str
    styling_tips: List[str]
    limitations: str
    uncertainty_level: str # Low, Moderate, High

class SkinToneResult(BaseModel):
    shade: str # Very Light, Light/Fair, Medium, Tan, Deep
    undertone: str # Cool, Warm, Neutral
    ita_angle: float
    lab_values: Dict[str, float]
    seasonal_palette: str # Spring Light, Summer Cool, Autumn Warm, Winter Vivid
    description: str
    color_analysis_warning: Optional[str] = None
    undertone_confidence: str

class ProductRecommendation(BaseModel):
    id: str
    name: str
    brand: str
    category: str # lipstick, blush, eyeshadow, hair_color
    shade_name: str
    hex_code: str
    match_score: float
    reason: str
    compatibility_label: Optional[str] = None
    delta_e: Optional[float] = None

class EyewearRecommendation(BaseModel):
    id: str
    frame_style: str
    category: str # round, oval, square, rectangular, cat-eye, aviator, geometric
    description: str
    recommended_colors: List[str]
    color_hex_swatches: List[str]
    match_score: float
    suitability: str
    compatibility_label: str
    reasoning: str

class ColorSwatch(BaseModel):
    name: str
    hex: str
    category: str # best, avoid

class PersonalColorPalette(BaseModel):
    season: str
    title: str
    description: str
    best_colors: List[ColorSwatch]
    worst_colors: List[ColorSwatch]

class FullBeautyAnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    detection_status: str # face_detected, multiple_faces_detected
    detection_warning: Optional[str] = None
    lighting: LightingQuality
    face_shape: FaceShapeResult
    skin_tone: SkinToneResult
    color_palette: PersonalColorPalette
    makeup_recommendations: List[ProductRecommendation]
    eyewear_recommendations: List[EyewearRecommendation]
    annotated_image_base64: Optional[str] = None
    created_at: str
