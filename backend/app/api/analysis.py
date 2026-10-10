from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from app.services.face_analyzer import face_analyzer_service
from app.services.face_shape import face_shape_estimator
from app.services.skin_tone import skin_tone_analyzer
from app.services.recommendation_engine import recommendation_engine
from app.models.schemas import FullBeautyAnalysisResponse
from app.core.config import settings
from app.api.auth import get_authenticated_user_email
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/analyze", response_model=FullBeautyAnalysisResponse)
async def analyze_face_image(
    file: UploadFile = File(...),
    user_email: str = Depends(get_authenticated_user_email)
):
    # 1. Validate file format
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported image format '{file.content_type}'. Allowed formats: JPEG, PNG, WEBP."
        )

    contents = await file.read()
    if len(contents) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail=f"File size exceeds the maximum allowed limit of {settings.MAX_IMAGE_SIZE_MB}MB."
        )

    try:
        img_bgr = face_analyzer_service.decode_image(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Evaluate lighting & blur quality
    lighting = face_analyzer_service.evaluate_lighting(img_bgr)
    if not lighting["is_valid"]:
        raise HTTPException(status_code=400, detail=lighting["warning"])

    # 3. Process 3D facial landmarks with MediaPipe
    landmarks, annotated_img, num_faces, detection_warning = face_analyzer_service.process_face_landmarks(img_bgr)
    
    if num_faces == 0:
        raise HTTPException(
            status_code=422, 
            detail="No usable face detected in the image. Please provide a clear, front-facing portrait photo."
        )

    detection_status = "face_detected" if num_faces == 1 else "multiple_faces_detected"

    # 4. Estimate Face Shape with normalized measurements & documented geometric reasoning
    face_shape_res = face_shape_estimator.estimate_shape(landmarks, blur_score=lighting["blur_score"])

    # 5. Analyze Skin Tone & Undertone (CIE L*a*b* / ITA°)
    skin_tone_res = skin_tone_analyzer.analyze(img_bgr, landmarks)

    # 6. Recommendation Engine Output (CIE L*a*b* Delta E & Eyewear Geometry Rules)
    color_palette_res = recommendation_engine.get_color_palette(skin_tone_res["seasonal_palette"])
    makeup_recs = recommendation_engine.get_makeup_recommendations(
        undertone=skin_tone_res["undertone"], 
        season=skin_tone_res["seasonal_palette"],
        skin_lab=skin_tone_res["lab_values"]
    )
    eyewear_recs = recommendation_engine.get_eyewear_recommendations(
        face_shape=face_shape_res["face_shape"],
        ratios=face_shape_res["ratios"],
        season=skin_tone_res["seasonal_palette"]
    )

    # 7. Encode annotated landmark image
    annotated_base64 = face_analyzer_service.encode_image_base64(annotated_img)

    analysis_id = str(uuid.uuid4())

    return FullBeautyAnalysisResponse(
        success=True,
        analysis_id=analysis_id,
        detection_status=detection_status,
        detection_warning=detection_warning,
        lighting=lighting,
        face_shape=face_shape_res,
        skin_tone=skin_tone_res,
        color_palette=color_palette_res,
        makeup_recommendations=makeup_recs,
        eyewear_recommendations=eyewear_recs,
        annotated_image_base64=annotated_base64,
        created_at=datetime.utcnow().isoformat()
    )
