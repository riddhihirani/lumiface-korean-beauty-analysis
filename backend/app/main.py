from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import health, analysis, auth, recommendations, report

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["Beauty Analysis"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(recommendations.router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["Recommendations"])
app.include_router(report.router, prefix=f"{settings.API_V1_STR}/report", tags=["PDF Report"])

@app.get("/")
def root():
    return {
        "message": "Welcome to Korean Beauty Analysis API",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
