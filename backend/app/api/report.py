from fastapi import APIRouter, Response, HTTPException, Body, Depends
from app.services.pdf_generator import pdf_report_generator
from app.api.auth import get_authenticated_user_email
from app.db.database import get_db_connection
from typing import Dict, Any

router = APIRouter()

@router.post("/generate")
def generate_pdf_report(
    payload: Dict[str, Any] = Body(...),
    user_email: str = Depends(get_authenticated_user_email)
):
    """
    Generate downloadable PDF report from analysis payload data.
    Requires authentication. Automatically injects verified user full name.
    """
    analysis_data = payload.get("analysis_data")
    face_image_base64 = payload.get("face_image_base64")

    if not analysis_data:
        raise HTTPException(status_code=400, detail="Missing analysis_data in request body.")

    # Securely retrieve user's registered name from database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT full_name FROM users WHERE email = ?", (user_email,))
        row = cursor.fetchone()
        conn.close()
        if row and row["full_name"]:
            analysis_data["user_full_name"] = row["full_name"]
    except Exception:
        pass

    try:
        pdf_bytes = pdf_report_generator.generate(analysis_data, face_image_base64)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=Korean_Beauty_Analysis_Report.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")
