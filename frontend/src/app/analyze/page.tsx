'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'

interface LightingInfo {
  is_valid: boolean
  brightness: number
  contrast: number
  blur_score: number
  warning?: string
}

interface FaceShapeInfo {
  face_shape: string
  ratios: Record<string, number>
  measurements: Record<string, number>
  reasoning: string
  description: string
  styling_tips: string[]
  limitations: string
  uncertainty_level: string
}

interface SkinToneInfo {
  shade: string
  undertone: string
  ita_angle: number
  lab_values: Record<string, number>
  seasonal_palette: string
  description: string
  color_analysis_warning?: string
  undertone_confidence: string
}

interface ColorSwatch {
  name: string
  hex: string
  category: string
}

interface PersonalColorPalette {
  season: string
  title: string
  description: string
  best_colors: ColorSwatch[]
  worst_colors: ColorSwatch[]
}

interface ProductRecommendation {
  id: string
  name: string
  brand: string
  category: string
  shade_name: string
  hex_code: string
  match_score: number
  reason: string
  compatibility_label?: string
  delta_e?: number
}

interface EyewearRecommendation {
  id?: string
  frame_style: string
  category?: string
  description: string
  recommended_colors?: string[]
  color_hex_swatches?: Record<string, string>
  match_score: number
  suitability: string
  compatibility_label?: string
  reasoning?: string
}

interface AnalysisResult {
  success: boolean
  analysis_id: string
  detection_status: string
  detection_warning?: string
  lighting: LightingInfo
  face_shape: FaceShapeInfo
  skin_tone: SkinToneInfo
  color_palette: PersonalColorPalette
  makeup_recommendations: ProductRecommendation[]
  eyewear_recommendations: EyewearRecommendation[]
  annotated_image_base64?: string
  created_at: string
}

export default function AnalysisPage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)

  const [activeTab, setActiveTab] = useState<'upload' | 'camera'>('upload')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analyzingStep, setAnalyzingStep] = useState(0)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false)

  // Camera state
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [isCameraActive, setIsCameraActive] = useState(false)
  const [isVideoReady, setIsVideoReady] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('lumiface_token')
    if (!token) {
      router.push('/login')
    } else {
      setIsAuthenticated(true)
      setIsCheckingAuth(false)
    }
  }, [router])

  useEffect(() => {
    stopCamera()
    setErrorMsg(null)
  }, [activeTab])

  const startCamera = async () => {
    try {
      setErrorMsg(null)
      setIsVideoReady(false)
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720, facingMode: 'user' }
      })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play()
        setIsCameraActive(true)
      }
    } catch (err) {
      setErrorMsg('Could not access webcam. Please check camera permissions in your browser or upload a portrait file.')
      setIsCameraActive(false)
      setIsVideoReady(false)
    }
  }

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream
      stream.getTracks().forEach(track => track.stop())
      videoRef.current.srcObject = null
    }
    setIsCameraActive(false)
    setIsVideoReady(false)
  }

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return
    const video = videoRef.current
    const canvas = canvasRef.current

    if (!isCameraActive || video.readyState < 2 || video.videoWidth === 0) {
      setErrorMsg('Camera stream is still initializing. Please wait a moment before capturing.')
      return
    }

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'camera_portrait.jpg', { type: 'image/jpeg' })
          setSelectedFile(file)
          const dataUrl = canvas.toDataURL('image/jpeg')
          setImagePreview(dataUrl)
          stopCamera()
        } else {
          setErrorMsg('Failed to process captured camera image. Please try again.')
        }
      }, 'image/jpeg', 0.95)
    }
  }

  const retakePhoto = () => {
    if (imagePreview && imagePreview.startsWith('blob:')) {
      URL.revokeObjectURL(imagePreview)
    }
    setImagePreview(null)
    setSelectedFile(null)
    setErrorMsg(null)
    if (activeTab === 'camera') {
      startCamera()
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMsg(null)
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.size > 10 * 1024 * 1024) {
        setErrorMsg('File size exceeds the 10MB limit. Please upload a smaller image.')
        return
      }
      setSelectedFile(file)
      setImagePreview(URL.createObjectURL(file))
    }
  }

  const runAnalysis = async () => {
    if (!selectedFile) {
      setErrorMsg('Please upload a photo or capture a camera image first.')
      return
    }

    const token = localStorage.getItem('lumiface_token')
    if (!token) {
      router.push('/login')
      return
    }

    setResult(null)
    setIsAnalyzing(true)
    setErrorMsg(null)
    setAnalyzingStep(1)

    const t1 = setTimeout(() => setAnalyzingStep(2), 1200)
    const t2 = setTimeout(() => setAnalyzingStep(3), 2400)

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const res = await fetch('http://127.0.0.1:8000/api/analysis/analyze', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      })

      if (res.status === 401) {
        localStorage.removeItem('lumiface_token')
        localStorage.removeItem('lumiface_user')
        window.dispatchEvent(new Event('lumiface_auth_change'))
        router.push('/login')
        throw new Error('Your authentication session has expired. Please sign in again.')
      }

      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || 'Analysis request failed.')
      }

      const data: AnalysisResult = await res.json()
      setResult(data)
    } catch (err: any) {
      setErrorMsg(err.message || 'Unable to connect to analysis engine at http://127.0.0.1:8000.')
    } finally {
      clearTimeout(t1)
      clearTimeout(t2)
      setIsAnalyzing(false)
      setAnalyzingStep(0)
    }
  }

  const downloadPdfReport = async () => {
    if (!result) return
    const token = localStorage.getItem('lumiface_token')
    if (!token) {
      router.push('/login')
      return
    }

    setIsDownloadingPdf(true)
    try {
      let userName = 'Valued Client'
      const userStr = localStorage.getItem('lumiface_user')
      if (userStr) {
        try {
          const u = JSON.parse(userStr)
          if (u.full_name) userName = u.full_name
        } catch {}
      }

      const payload = {
        analysis_data: {
          ...result,
          user_full_name: userName
        },
        face_image_base64: result.annotated_image_base64 || imagePreview
      }

      const res = await fetch('http://127.0.0.1:8000/api/report/generate', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })

      if (res.status === 401) {
        localStorage.removeItem('lumiface_token')
        localStorage.removeItem('lumiface_user')
        window.dispatchEvent(new Event('lumiface_auth_change'))
        router.push('/login')
        throw new Error('Your authentication session has expired. Please sign in again.')
      }

      if (!res.ok) throw new Error('Failed to generate PDF report.')

      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `LumiFace_Blueprint_${result.analysis_id.slice(0, 8)}.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
    } catch (err: any) {
      alert(`Report Download Error: ${err.message}`)
    } finally {
      setIsDownloadingPdf(false)
    }
  }

  if (isCheckingAuth || !isAuthenticated) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <div className="animate-spin w-8 h-8 border-4 border-[#7D2E3B] border-t-transparent rounded-full" />
        <p className="text-xs text-gray-500 font-medium">Verifying LumiFace authentication status...</p>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      
      {/* Page Title */}
      <div className="text-center space-y-3">
        <div className="lumi-badge">Scientific Personal Beauty Diagnostics</div>
        <h1 className="text-3xl sm:text-5xl font-extrabold font-outfit text-gray-900 tracking-tight">
          LumiFace AI Diagnostics
        </h1>
        <p className="text-xs sm:text-base text-[#6B6565] max-w-xl mx-auto">
          Capture or upload your front-facing portrait to analyze 3D facial geometry, ITA° skin tone spectrum, and curated K-beauty recommendations.
        </p>
      </div>

      {/* Step Progress Guide Bar */}
      <div className="max-w-3xl mx-auto grid grid-cols-3 gap-2 text-center text-xs">
        <div className={`p-2.5 rounded-xl border ${result ? 'bg-[#FDF2F4] border-[#F5DDE1] text-[#7D2E3B] font-bold' : 'bg-white border-[#EADCDC] text-gray-900 font-semibold'}`}>
          1. Photo Input
        </div>
        <div className={`p-2.5 rounded-xl border ${isAnalyzing ? 'bg-amber-50 border-amber-200 text-amber-900 font-bold' : 'bg-white border-[#EADCDC] text-gray-500'}`}>
          2. Geometry & Skin Scan
        </div>
        <div className={`p-2.5 rounded-xl border ${result ? 'bg-emerald-50 border-emerald-200 text-emerald-800 font-bold' : 'bg-white border-[#EADCDC] text-gray-500'}`}>
          3. K-Beauty Report
        </div>
      </div>

      {/* Main Analysis Input Card */}
      <div className="max-w-3xl mx-auto lumi-card p-6 sm:p-10 space-y-6">
        
        {/* Input Option Toggle */}
        <div className="flex rounded-full bg-[#FAF7F2] p-1 border border-[#EADCDC]">
          <button
            onClick={() => { setActiveTab('upload'); stopCamera(); }}
            className={`flex-1 py-2.5 text-xs font-semibold rounded-full transition-all ${
              activeTab === 'upload' ? 'bg-white text-[#7D2E3B] shadow-xs' : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            Upload Portrait
          </button>
          <button
            onClick={() => { setActiveTab('camera'); startCamera(); }}
            className={`flex-1 py-2.5 text-xs font-semibold rounded-full transition-all ${
              activeTab === 'camera' ? 'bg-white text-[#7D2E3B] shadow-xs' : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            Use Live Camera
          </button>
        </div>

        {/* Positioning & Quality Instructions */}
        <div className="p-3.5 rounded-xl bg-[#FAF7F2] border border-[#F0E6E6] text-xs text-[#6B6565] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#7D2E3B]" />
            <span>Optimal results: Front-facing light, neutral expression, forehead & jawline visible.</span>
          </div>
          <span className="text-[11px] text-gray-400 font-medium">Remove sunglasses</span>
        </div>

        {/* Tab Content: Upload */}
        {activeTab === 'upload' && (
          <div className="space-y-4 text-center">
            <label className="border-2 border-dashed border-[#EADCDC] hover:border-[#C86D7C] rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer transition-colors bg-white/60 hover:bg-[#FDF2F4]/30">
              <div className="w-12 h-12 rounded-full bg-[#FDF2F4] text-[#7D2E3B] flex items-center justify-center text-xl mb-3">
                📷
              </div>
              <span className="text-xs sm:text-sm font-semibold text-gray-800">
                Click to upload portrait photo or drag & drop file
              </span>
              <span className="text-[11px] text-gray-400 mt-1">
                Supports JPG, PNG, WEBP (Max 10MB)
              </span>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleFileSelect}
                className="hidden"
              />
            </label>

            {imagePreview && (
              <div className="relative w-56 h-64 mx-auto rounded-2xl overflow-hidden border border-[#EADCDC] shadow-md group">
                <img src={imagePreview} alt="Selected portrait preview" className="w-full h-full object-cover" />
                {/* Face positioning guide overlay outline */}
                <div className="absolute inset-0 border-2 border-dashed border-[#D4AF37]/70 rounded-[50%] m-6 pointer-events-none face-guide-oval flex items-center justify-center">
                  <span className="text-[10px] text-[#D4AF37] font-bold uppercase tracking-wider bg-black/50 px-2 py-0.5 rounded-full">
                    Face Guide
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab Content: Camera */}
        {activeTab === 'camera' && (
          <div className="space-y-4 text-center">
            {imagePreview ? (
              /* Display captured image preview immediately */
              <div className="space-y-4">
                <div className="relative w-56 h-64 mx-auto rounded-2xl overflow-hidden border border-[#EADCDC] shadow-md group">
                  <img src={imagePreview} alt="Captured camera portrait preview" className="w-full h-full object-cover" />
                  <div className="absolute inset-0 border-2 border-dashed border-[#D4AF37]/70 rounded-[50%] m-6 pointer-events-none face-guide-oval flex items-center justify-center">
                    <span className="text-[10px] text-[#D4AF37] font-bold uppercase tracking-wider bg-black/50 px-2 py-0.5 rounded-full">
                      Face Guide
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-center gap-3">
                  <button onClick={retakePhoto} className="lumi-btn-secondary px-5 py-2 text-xs">
                    🔄 Retake Photo
                  </button>
                  <span className="text-xs text-emerald-700 font-semibold flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" /> Photo Ready for Analysis
                  </span>
                </div>
              </div>
            ) : (
              /* Live Camera Stream */
              <div className="space-y-4">
                <div className="relative w-full max-w-md mx-auto aspect-[4/3] bg-black rounded-2xl overflow-hidden shadow-md">
                  <video 
                    ref={videoRef} 
                    onCanPlay={() => setIsVideoReady(true)}
                    onLoadedMetadata={() => setIsVideoReady(true)}
                    className="w-full h-full object-cover" 
                    playsInline 
                    muted 
                  />
                  <canvas ref={canvasRef} className="hidden" />
                  
                  {/* Face Guide Overlay */}
                  {isCameraActive && (
                    <div className="absolute inset-0 border-2 border-dashed border-[#D4AF37]/80 rounded-[50%] m-8 pointer-events-none face-guide-oval flex items-center justify-center">
                      <span className="text-[10px] text-[#D4AF37] font-bold uppercase tracking-wider bg-black/60 px-2.5 py-1 rounded-full">
                        Align Face Here
                      </span>
                    </div>
                  )}
                </div>

                {isCameraActive && (
                  <button 
                    onClick={capturePhoto} 
                    disabled={!isVideoReady}
                    className="lumi-btn-primary px-6 py-2.5 text-xs disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                  >
                    {isVideoReady ? '📷 Take Photo Capture' : 'Initializing Camera Feed...'}
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {/* Error Alert Banner */}
        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium space-y-1">
            <div className="font-bold">Analysis Detection Warning</div>
            <div>{errorMsg}</div>
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={runAnalysis}
          disabled={!selectedFile || isAnalyzing}
          className="w-full lumi-btn-primary py-4 text-sm font-semibold shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAnalyzing ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              {analyzingStep === 1 && '1/3 Extracting 468 MediaPipe facial landmarks...'}
              {analyzingStep === 2 && '2/3 Measuring ratios & ITA° skin spectrum...'}
              {analyzingStep === 3 && '3/3 Matching K-beauty catalog recommendations...'}
              {analyzingStep === 0 && 'Processing Image Geometry...'}
            </span>
          ) : (
            'Run LumiFace AI Diagnostics ✨'
          )}
        </button>

      </div>

      {/* Diagnostics Results Section */}
      {result && (
        <div id="results" className="space-y-10 pt-8 border-t border-[#F0E6E6]">
          
          {/* Action & Detection Status Header */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 lumi-card bg-white">
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <div className="lumi-badge">Diagnostic Report Ready</div>
                {result.detection_warning && (
                  <span className="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px] font-bold">
                    ⚠️ {result.detection_warning}
                  </span>
                )}
                {result.skin_tone.color_analysis_warning && (
                  <span className="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-900 text-[10px] font-bold">
                    ⚠️ {result.skin_tone.color_analysis_warning}
                  </span>
                )}
              </div>
              <h2 className="text-2xl font-bold font-outfit text-gray-900 mt-1">
                Your Personal Beauty Analysis
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Analysis ID: {result.analysis_id.slice(0, 18)}... • Calculated at {new Date(result.created_at).toLocaleTimeString()}
              </p>
            </div>

            <button
              onClick={downloadPdfReport}
              disabled={isDownloadingPdf}
              className="lumi-btn-secondary py-2.5 px-6 text-xs"
            >
              {isDownloadingPdf ? 'Generating PDF...' : '📥 Download PDF Report'}
            </button>
          </div>

          {/* 3 Column Grid: Landmark Mesh, Face Shape, Skin Tone */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* 3D Facial Landmark Mesh */}
            <div className="lumi-card p-6 space-y-4 text-center">
              <h3 className="font-bold text-gray-900 font-outfit text-base">MediaPipe 3D Landmark Mesh</h3>
              <div className="relative rounded-2xl overflow-hidden border border-[#EADCDC] shadow-xs max-h-[360px] mx-auto bg-black/5">
                {result.annotated_image_base64 ? (
                  <img src={result.annotated_image_base64} alt="Annotated 3D Landmark Mesh" className="w-full h-auto object-cover" />
                ) : (
                  <div className="p-12 text-gray-400 text-xs">Landmark visualization</div>
                )}
              </div>
              <p className="text-[11px] text-gray-500 bg-[#FAF7F2] p-3 rounded-xl border border-[#F0E6E6] text-left">
                MediaPipe 468 3D landmark points mapping zygomatic cheekbones, gonion jawline, forehead hairline, and chin point.
              </p>
            </div>

            {/* Face Shape Breakdown & Geometric Measurements */}
            <div className="lumi-card p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-gray-900 font-outfit text-base">Facial Geometry Measurements</h3>
                <span className="px-3 py-1 rounded-full bg-[#FDF2F4] text-[#7D2E3B] text-xs font-bold uppercase tracking-wider">
                  {result.face_shape.face_shape}
                </span>
              </div>

              {/* Measured Pixel Dimensions */}
              <div className="grid grid-cols-2 gap-2 text-xs p-3 rounded-xl bg-[#FAF7F2] border border-[#F0E6E6]">
                <div>
                  <span className="text-gray-400 text-[10px] block">FACE LENGTH</span>
                  <span className="font-bold text-gray-900">{result.face_shape.measurements?.face_length_px} px</span>
                </div>
                <div>
                  <span className="text-gray-400 text-[10px] block">CHEEKBONE WIDTH</span>
                  <span className="font-bold text-gray-900">{result.face_shape.measurements?.cheekbone_width_px} px</span>
                </div>
                <div>
                  <span className="text-gray-400 text-[10px] block">FOREHEAD WIDTH</span>
                  <span className="font-bold text-gray-900">{result.face_shape.measurements?.forehead_width_px} px</span>
                </div>
                <div>
                  <span className="text-gray-400 text-[10px] block">JAW WIDTH</span>
                  <span className="font-bold text-gray-900">{result.face_shape.measurements?.jaw_width_px} px</span>
                </div>
              </div>

              {/* Ratios */}
              <div className="space-y-1.5 text-xs border-t border-[#F0E6E6] pt-3">
                <div className="flex justify-between text-gray-600">
                  <span>Aspect Ratio (Length / Cheek Width):</span>
                  <span className="font-bold text-gray-900">{result.face_shape.ratios.face_aspect_ratio}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Jaw to Cheek Ratio:</span>
                  <span className="font-bold text-gray-900">{result.face_shape.ratios.jaw_to_cheek_ratio}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Forehead to Cheek Ratio:</span>
                  <span className="font-bold text-gray-900">{result.face_shape.ratios.forehead_to_cheek_ratio}</span>
                </div>
              </div>

              {/* Documented Geometric Reasoning */}
              <div className="space-y-1 text-xs border-t border-[#F0E6E6] pt-3">
                <span className="font-bold text-gray-800 uppercase tracking-wider text-[10px]">Geometric Reasoning:</span>
                <p className="text-gray-600 leading-relaxed italic">
                  "{result.face_shape.reasoning}"
                </p>
              </div>

              {/* Uncertainty & Limitations */}
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-gray-500 space-y-1">
                <div className="flex items-center justify-between font-bold text-gray-700">
                  <span>Uncertainty Indicator:</span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] ${
                    result.face_shape.uncertainty_level === 'Low' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                  }`}>
                    {result.face_shape.uncertainty_level} Uncertainty
                  </span>
                </div>
                <p className="text-[10px] text-gray-400 leading-normal">
                  {result.face_shape.limitations}
                </p>
              </div>
            </div>

            {/* ITA° Skin Tone & Undertone */}
            <div className="lumi-card p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-gray-900 font-outfit text-base">Skin Tone & Undertone</h3>
                <span className="px-3 py-1 rounded-full bg-[#F5EFFB] text-purple-900 text-xs font-bold uppercase tracking-wider">
                  {result.skin_tone.seasonal_palette}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-center">
                <div className="p-3 rounded-xl bg-[#FDF2F4] border border-[#F5DDE1]">
                  <div className="text-[10px] text-gray-500 uppercase font-semibold">Shade Category</div>
                  <div className="font-bold text-[#7D2E3B] text-sm mt-0.5">{result.skin_tone.shade}</div>
                </div>
                <div className="p-3 rounded-xl bg-[#F5EFFB] border border-[#E5D9F2]">
                  <div className="text-[10px] text-gray-500 uppercase font-semibold">Undertone</div>
                  <div className="font-bold text-purple-900 text-sm mt-0.5">{result.skin_tone.undertone}</div>
                </div>
              </div>

              <div className="space-y-2 text-xs text-gray-600 border-t border-[#F0E6E6] pt-3">
                <div className="flex justify-between">
                  <span>ITA° Angle (Individual Typology Angle):</span>
                  <span className="font-bold text-gray-900">{result.skin_tone.ita_angle}°</span>
                </div>
                <div className="flex justify-between">
                  <span>CIE L* (Luminance Coordinate):</span>
                  <span className="font-semibold text-gray-900">{result.skin_tone.lab_values.L}</span>
                </div>
                <div className="flex justify-between">
                  <span>CIE a* (Red-Green balance):</span>
                  <span className="font-semibold text-gray-900">{result.skin_tone.lab_values.a}</span>
                </div>
                <div className="flex justify-between">
                  <span>CIE b* (Yellow-Blue balance):</span>
                  <span className="font-semibold text-gray-900">{result.skin_tone.lab_values.b}</span>
                </div>
              </div>

              <div className="border-t border-[#F0E6E6] pt-3 space-y-1.5">
                <p className="text-xs text-gray-600 leading-relaxed">
                  {result.skin_tone.description}
                </p>
                <div className="text-[10px] text-gray-400 font-medium">
                  Confidence: {result.skin_tone.undertone_confidence}
                </div>
              </div>
            </div>

          </div>

          {/* Seasonal Wardrobe Palette */}
          <div className="lumi-card p-6 sm:p-8 space-y-6">
            <div>
              <div className="lumi-badge">Seasonal Color Analysis</div>
              <h3 className="font-bold text-gray-900 font-outfit text-xl mt-1">
                Personal Wardrobe Palette — {result.color_palette.season}
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">{result.color_palette.description}</p>
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="text-xs font-bold text-emerald-800 uppercase tracking-wider mb-2.5">Recommended Best Hues</h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                  {result.color_palette.best_colors.map((c, i) => (
                    <div key={i} className="flex items-center gap-2.5 p-2.5 rounded-xl bg-white border border-[#EADCDC]">
                      <div className="w-8 h-8 rounded-lg shadow-xs border border-black/10 shrink-0" style={{ backgroundColor: c.hex }} />
                      <div className="min-w-0">
                        <div className="text-xs font-bold text-gray-800 truncate">{c.name}</div>
                        <div className="text-[10px] text-gray-400 font-mono uppercase">{c.hex}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-rose-800 uppercase tracking-wider mb-2.5">Colors To Avoid</h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {result.color_palette.worst_colors.map((c, i) => (
                    <div key={i} className="flex items-center gap-2.5 p-2.5 rounded-xl bg-white border border-[#EADCDC]">
                      <div className="w-8 h-8 rounded-lg shadow-xs border border-black/10 shrink-0" style={{ backgroundColor: c.hex }} />
                      <div className="min-w-0">
                        <div className="text-xs font-bold text-gray-800 truncate">{c.name}</div>
                        <div className="text-[10px] text-gray-400 font-mono uppercase">{c.hex}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Curated K-Beauty Makeup Shades */}
          <div className="space-y-4">
            <div>
              <div className="lumi-badge">Curated Products</div>
              <h3 className="font-bold text-gray-900 font-outfit text-2xl mt-1">
                K-Beauty Lipstick, Blush & Eye Shade Matches
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                Estimated Compatibility calculated via CIE L*a*b* Euclidean Delta E color distance matrix.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {result.makeup_recommendations.map((item) => (
                <div key={item.id} className="lumi-card p-5 space-y-3 bg-white">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-[#FDF2F4] text-[#7D2E3B]">
                      {item.category}
                    </span>
                    <div className="text-right">
                      <span className="text-xs font-bold text-emerald-700 block">
                        {item.match_score}% Score
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full shadow-md shrink-0 border border-black/10" style={{ backgroundColor: item.hex_code }} />
                    <div className="min-w-0">
                      <h4 className="font-bold text-gray-900 text-xs sm:text-sm truncate">{item.name}</h4>
                      <p className="text-xs text-gray-500">{item.brand}</p>
                    </div>
                  </div>

                  <p className="text-xs text-gray-600 border-t border-[#F0E6E6] pt-2.5 leading-relaxed">
                    {item.reason}
                  </p>
                  
                  {item.delta_e !== undefined && (
                    <div className="text-[10px] text-gray-400 font-mono">
                      Delta E (Lab distance): {item.delta_e}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Eyewear Frame Recommendations */}
          <div className="space-y-4">
            <div>
              <div className="lumi-badge">Personalized Facial Framing</div>
              <h3 className="font-bold text-gray-900 font-outfit text-2xl mt-1">
                Curated Eyewear Frame Recommendations ({result.face_shape.face_shape.toUpperCase()})
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                Transparent compatibility estimated from 3D facial proportions, jaw structure, and {result.skin_tone.seasonal_palette} personal color palette.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {result.eyewear_recommendations.map((frame, i) => (
                <div key={i} className="lumi-card p-5 space-y-3 bg-white flex flex-col justify-between">
                  <div className="space-y-3">
                    
                    {/* Header Badges */}
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-[#FAF7F2] text-[#7D2E3B] border border-[#EADCDC]">
                        {frame.category || frame.frame_style}
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        frame.suitability === 'Highly Recommended' 
                          ? 'bg-emerald-100 text-emerald-800'
                          : frame.suitability === 'Flattering Accent'
                          ? 'bg-purple-100 text-purple-800'
                          : 'bg-slate-100 text-slate-700'
                      }`}>
                        {frame.suitability}
                      </span>
                    </div>

                    {/* Title & Score */}
                    <div className="flex items-baseline justify-between pt-1">
                      <h4 className="font-bold font-outfit text-gray-900 text-base">{frame.frame_style}</h4>
                      <span className="text-sm font-extrabold text-[#7D2E3B]">{frame.match_score}% Score</span>
                    </div>

                    <p className="text-xs text-gray-600 leading-relaxed">
                      {frame.description}
                    </p>

                    {/* Geometric Reasoning */}
                    {frame.reasoning && (
                      <div className="p-3 rounded-xl bg-[#FAF7F2] border border-[#F0E6E6] text-[11px] text-gray-600 leading-normal space-y-1">
                        <span className="font-bold text-[10px] uppercase tracking-wider text-[#7D2E3B] block">Geometric Harmony:</span>
                        <p>{frame.reasoning}</p>
                      </div>
                    )}

                    {/* Recommended Color Swatches */}
                    {frame.recommended_colors && frame.recommended_colors.length > 0 && (
                      <div className="space-y-1.5 border-t border-[#F0E6E6] pt-3">
                        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">
                          Recommended Colors ({result.skin_tone.seasonal_palette}):
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {frame.recommended_colors.map((colorName, idx) => {
                            const hex = frame.color_hex_swatches?.[colorName] || '#6B6565'
                            return (
                              <div key={idx} className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-white border border-[#EADCDC] text-[11px] text-gray-700">
                                <span className="w-3 h-3 rounded-full border border-black/15 shadow-2xs shrink-0" style={{ backgroundColor: hex }} />
                                <span className="font-medium text-[10px]">{colorName}</span>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Compatibility Label Note */}
                  <div className="text-[9px] text-gray-400 font-medium border-t border-[#F0E6E6] pt-2 text-right">
                    {frame.compatibility_label || 'Estimated Compatibility Score'}
                  </div>

                </div>
              ))}
            </div>
          </div>

        </div>
      )}

    </div>
  )
}
