# LumiFace — Korean Beauty Diagnostics & Personal Color Science Platform

**Your Beauty, Scientifically Understood.**

LumiFace is a luxury Korean beauty-tech platform designed to eliminate beauty guesswork through 3D facial landmark mesh analysis, CIE L\*a\*b\* skin tone colorimetry, seasonal color theory, and personalized product recommendations.

---

## ✨ Features

### 1. 3D Facial Landmark Mesh & Face Geometry Analysis
- **468 3D Landmark Point Mapping**: Powered by MediaPipe 3D Face Mesh landmarker solution.
- **Normalized Aspect Ratios**: Evaluates face length, cheekbone width, forehead width, jaw width, and aspect ratios.
- **Dynamic Face Shape Classification**: Classifies Oval, Round, Square, Heart, Oblong, and Diamond face shapes with documented geometric reasoning and uncertainty indicators.

### 2. CIE L\*a\*b\* & ITA° Skin Spectrum Analysis
- **Scientific Undertone Matrix**: Measures Individual Typology Angle ($ITA^\circ$) and CIE L\*a\*b\* color space coordinates from forehead and cheek sampling regions.
- **Seasonal Color Palette Assignment**: Matches skin spectrum to **Spring Light**, **Summer Cool**, **Autumn Warm**, or **Winter Vivid**.
- **Lighting & Color-Cast Check**: Evaluates mean image luminance, contrast, blur score, and color balance to warn users of improper lighting conditions.

### 3. Personalized K-Beauty Recommendations
- **Lipstick, Blush & Eyeshadow Edits**: Tailored K-Beauty product matches scored using CIE L\*a\*b\* Euclidean Delta E ($\Delta E$) color distance matrices.
- **7 Eyewear Frame Categories**: Tailored recommendations across Round, Oval, Square, Rectangular, Cat-Eye, Aviator, and Geometric frames with transparent suitability scores and seasonal frame color swatches.
- **Personal Wardrobe Hues**: HEX color swatches for recommended clothing colors and shades to avoid.

### 4. "Your Personal Beauty Blueprint" Downloadable PDF Report
- High-resolution, multi-page ReportLab PDF document containing the annotated 3D landmark mesh, pixel dimensions, geometric reasoning, skin metrics, product matches, eyewear frame compatibility, and personal beauty summary.

### 5. Secure Authentication & User Consultation Profile
- **Persistent Account Storage**: SQLite database (`backend/data/lumiface.db`) with PBKDF2-HMAC-SHA256 password hashing (100,000 iterations).
- **Session Tokens**: Signed 7-day HMAC-SHA256 JWT tokens.
- **Protected Routes**: Client-side auth gates and FastAPI dependency authorization (`Depends(get_authenticated_user_email)`).

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 16 (App Router with Webpack)
- **UI & Logic**: React 19 & TypeScript
- **Styling**: TailwindCSS v4, Custom Luxury CSS Design Tokens (`#FAF7F2` Ivory, `#7D2E3B` Garnet, `#C86D7C` Rose, `#D4AF37` Gold)
- **Typography**: Outfit & Plus Jakarta Sans (Google Fonts)

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Computer Vision**: OpenCV & MediaPipe 3D Face Mesh
- **Colorimetry & Math**: NumPy & SciPy
- **PDF Generation**: ReportLab
- **Database & Auth**: SQLite, hashlib (PBKDF2-HMAC-SHA256), HMAC-SHA256 JWT
- **Testing**: Pytest & FastAPI TestClient

---

## 📁 Repository Structure

```text
korean-beauty-analysis/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI API routes (analysis, auth, report, health)
│   │   ├── core/            # Security, password hashing & JWT token logic
│   │   ├── db/              # SQLite database initialization & connection
│   │   ├── models/          # Pydantic schema models
│   │   └── services/        # OpenCV, MediaPipe, Skin Tone & PDF Report generators
│   ├── data/                # Catalog JSON files (eyewear, makeup, palettes)
│   ├── tests/               # 25 backend pytest test modules
│   ├── .env.example         # Backend environment template
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages (/, /analyze, /login, /register, /profile)
│   │   └── components/      # Navbar & UI components
│   ├── next.config.ts       # Next.js configuration & API proxy rewrites
│   └── package.json         # Frontend Node dependencies
├── .env.example             # Root environment template
├── .gitignore               # Comprehensive Git ignore rules
└── README.md                # Project documentation
```

---

## 🚀 Setup & Local Installation

### 1. Prerequisites
- **Python**: Version 3.11 or higher
- **Node.js**: Version 20.0 or higher
- **npm**: Version 10.0 or higher

### 2. Backend Setup
1. Open a terminal and navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment variables template:
   ```bash
   cp .env.example .env
   ```
5. Run the FastAPI development server:
   ```bash
   PYTHONPATH=. python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   The backend will start at `http://127.0.0.1:8000`.

### 3. Frontend Setup
1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open `http://localhost:3000` in your web browser.

---

## 🧪 Running Tests

Execute the backend automated unit & integration test suite:

```bash
cd backend
PYTHONPATH=. pytest tests/ -v
```

All 25 unit tests validate face landmark processing, CIE L\*a\*b\* skin calculations, eyewear recommendation logic, PDF generation, and PBKDF2 authentication flows.

---

## 🔒 Security & Git Hygiene

- **Database Privacy**: The local SQLite database (`backend/data/lumiface.db`) contains user account data and is excluded from version control via `.gitignore`.
- **Environment Variables**: Secret keys and environment-specific configs are managed via `.env` files and omitted from version control. Always copy `.env.example` to create your local `.env`.
- **No Secret Leaks**: Passwords, hashes, and session tokens are never logged or committed to the repository.
