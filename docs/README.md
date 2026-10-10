# Korean Beauty Analysis — AI-Powered Personal Beauty Recommendation

A full-stack AI-powered personal beauty recommendation web application built with a modern Korean aesthetic (blush pink, cream, lavender, muted rose).

## Features
1. **3D Face Mesh & Geometric Landmark Extraction**: MediaPipe 468 facial 3D landmark extraction for precise face shape classification (Oval, Round, Square, Heart, Oblong, Diamond).
2. **CIE L\*a\*b\* Skin Diagnostics**: Individual Typology Angle (ITA°) skin shade calculation and undertone temperature determination (Cool, Warm, Neutral).
3. **Seasonal Color Analysis**: Automatic mapping to K-Beauty seasonal palettes (Spring Light, Summer Cool, Autumn Warm, Winter Vivid).
4. **K-Beauty Shade & Eyewear Matching**: Curated lipstick tints, blushes, eyeshadows, and eyewear frames tailored to facial geometry.
5. **Downloadable PDF Beauty Diagnostics Report**: High-resolution PDF report generated on-demand using ReportLab containing facial landmark overlays and diagnostic summaries.

---

## Project Architecture

```
korean-beauty-analysis/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routers (health, analysis, auth, recommendations, report)
│   │   ├── core/            # Configuration & security settings
│   │   ├── models/          # Data schemas & validation models
│   │   ├── services/        # Face analyzer, Face shape, Skin tone, Recommendation engine, PDF generator
│   │   └── main.py          # FastAPI application entrypoint
│   ├── data/                # Curated JSON databases for palettes, makeup, eyewear
│   ├── tests/               # Pytest suite
│   └── requirements.txt
├── frontend/                # Next.js App Router (TypeScript + Tailwind CSS)
│   ├── src/
│   │   ├── app/             # Pages (Landing page, AI Analysis workflow)
│   │   └── components/      # UI components (Navbar, Footer)
│   ├── package.json
│   └── tailwind.config.ts
└── docs/
    └── README.md
```

---

## Setup & Running Locally

### 1. Run the Backend API Server
Navigate to the root directory and start the FastAPI server using Uvicorn:

```bash
# Start FastAPI backend server on port 8000
PYTHONPATH=backend python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Check Endpoint: `http://localhost:8000/api/health`

### 2. Run the Next.js Frontend App
In a separate terminal, navigate to the `frontend/` folder and start the dev server:

```bash
cd frontend
npm run dev
```
- Frontend Web App: `http://localhost:3000`
