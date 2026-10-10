'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'

export default function Home() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('lumiface_token')
    if (!token) {
      router.push('/login')
    } else {
      setIsAuthenticated(true)
      setIsCheckingAuth(false)
    }
  }, [router])

  if (isCheckingAuth || !isAuthenticated) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <div className="animate-spin w-8 h-8 border-4 border-[#7D2E3B] border-t-transparent rounded-full" />
        <p className="text-xs text-gray-500 font-medium">Verifying LumiFace authentication status...</p>
      </div>
    )
  }

  return (
    <div className="space-y-24 pb-20">
      
      {/* Hero Section */}
      <section className="relative pt-12 lg:pt-16 pb-12 overflow-hidden">
        
        {/* Soft luxury background glow accents */}
        <div className="absolute top-12 left-1/2 -translate-x-1/2 w-[700px] h-[450px] bg-[#F8E7EA]/40 blur-[130px] rounded-full pointer-events-none -z-10" />
        <div className="absolute top-1/3 right-4 w-[380px] h-[380px] bg-[#E5D9F2]/30 blur-[110px] rounded-full pointer-events-none -z-10" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Column Text Content */}
            <div className="lg:col-span-7 space-y-8 text-left">
              
              <div className="lumi-badge">
                <span className="w-1.5 h-1.5 rounded-full bg-[#7D2E3B]" />
                <span>Korean Beauty Diagnostics Platform</span>
              </div>

              <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-gray-900 font-outfit leading-[1.12]">
                Your Beauty, <br />
                <span className="lumi-text-gradient">Scientifically Understood.</span>
              </h1>

              <p className="text-base sm:text-lg text-[#6B6565] max-w-2xl font-normal leading-relaxed">
                Unlock your unique facial geometry, ITA° skin tone spectrum, and curated Korean beauty recommendations. Powered by 3D landmark analysis and standardized CIE L*a*b* color science.
              </p>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-2">
                <Link href="/analyze" className="lumi-btn-primary text-base px-8 py-4 shadow-md">
                  <span>Start My Beauty Analysis</span>
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </Link>

                <a href="#how-it-works" className="lumi-btn-secondary text-base px-8 py-4">
                  Explore Methodology
                </a>
              </div>

              {/* Trust Attributes */}
              <div className="pt-6 border-t border-[#F0E6E6] grid grid-cols-3 gap-4 text-xs text-[#6B6565]">
                <div>
                  <span className="font-bold text-gray-900 block font-outfit text-sm">468 Points</span>
                  3D Face Mesh Mapping
                </div>
                <div>
                  <span className="font-bold text-gray-900 block font-outfit text-sm">ITA° Matrix</span>
                  CIE L*a*b* Tone Science
                </div>
                <div>
                  <span className="font-bold text-gray-900 block font-outfit text-sm">PDF Report</span>
                  Downloadable Diagnostics
                </div>
              </div>

            </div>

            {/* Right Column Editorial Image */}
            <div className="lg:col-span-5 relative">
              <div className="relative mx-auto max-w-md lg:max-w-none rounded-2xl overflow-hidden border border-[#EADCDC] shadow-xl">
                <Image
                  src="/images/hero_portrait.jpg"
                  alt="LumiFace Editorial Model Portrait"
                  width={800}
                  height={1000}
                  priority
                  className="w-full h-auto object-cover transform hover:scale-102 transition-transform duration-700"
                />
                
                {/* Floating Aesthetic Overlay Card */}
                <div className="absolute bottom-6 left-6 right-6 lumi-card p-4 bg-white/90 backdrop-blur-md border border-white/80 space-y-1">
                  <div className="flex items-center justify-between text-xs font-bold text-gray-900 font-outfit">
                    <span>Sample Match Result</span>
                    <span className="text-[#7D2E3B]">98.4% Confidence</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-[#6B6565]">
                    <span className="px-2 py-0.5 rounded-full bg-[#FDF2F4] text-[#7D2E3B] font-semibold text-[10px] uppercase">Oval Face</span>
                    <span>•</span>
                    <span className="px-2 py-0.5 rounded-full bg-[#F5EFFB] text-purple-800 font-semibold text-[10px] uppercase">Summer Cool</span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Feature Section: 3 Pillars */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="text-center space-y-3">
          <div className="lumi-badge">Comprehensive Analysis Engine</div>
          <h2 className="text-3xl sm:text-4xl font-extrabold font-outfit text-gray-900">
            Three Pillars of LumiFace Diagnostics
          </h2>
          <p className="text-[#6B6565] max-w-2xl mx-auto text-sm sm:text-base">
            Engineered using precise computer vision models and curated Korean color theory to eliminate guesswork.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Card 1 */}
          <div className="lumi-card p-8 space-y-4 relative group">
            <div className="w-12 h-12 rounded-xl bg-[#FDF2F4] border border-[#F5DDE1] text-[#7D2E3B] flex items-center justify-center font-bold text-xl font-outfit">
              01
            </div>
            <h3 className="font-bold text-xl text-gray-900 font-outfit">Facial Shape Geometry</h3>
            <p className="text-xs sm:text-sm text-[#6B6565] leading-relaxed">
              Maps 468 3D landmark points across forehead, cheekbones, jawline, and chin. Calculates precise aspect ratios to classify Oval, Round, Square, Heart, Oblong, and Diamond face shapes.
            </p>
            <div className="pt-2 text-xs font-semibold text-[#7D2E3B] flex items-center gap-1 group-hover:translate-x-1 transition-transform">
              <span>View Face Ratios Engine</span> →
            </div>
          </div>

          {/* Card 2 */}
          <div className="lumi-card p-8 space-y-4 relative group">
            <div className="w-12 h-12 rounded-xl bg-[#F5EFFB] border border-[#E5D9F2] text-purple-900 flex items-center justify-center font-bold text-xl font-outfit">
              02
            </div>
            <h3 className="font-bold text-xl text-gray-900 font-outfit">ITA° Skin Spectrum</h3>
            <p className="text-xs sm:text-sm text-[#6B6565] leading-relaxed">
              Converts cheek and forehead regions into CIE L*a*b* color space. Evaluates Individual Typology Angle (ITA°) and a*/b* ratios to diagnose skin shade depth and warm/cool undertones.
            </p>
            <div className="pt-2 text-xs font-semibold text-purple-900 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
              <span>Explore Color Science</span> →
            </div>
          </div>

          {/* Card 3 */}
          <div className="lumi-card p-8 space-y-4 relative group">
            <div className="w-12 h-12 rounded-xl bg-[#FAF0E6] border border-[#E8D9C5] text-amber-900 flex items-center justify-center font-bold text-xl font-outfit">
              03
            </div>
            <h3 className="font-bold text-xl text-gray-900 font-outfit">K-Beauty Recommendations</h3>
            <p className="text-xs sm:text-sm text-[#6B6565] leading-relaxed">
              Curates flattering lipstick tints (velvet, glossy MLBB), cheek blushes, eyewear frames, and seasonal wardrobe palettes tailored specifically to your facial symmetry and skin temperature.
            </p>
            <div className="pt-2 text-xs font-semibold text-amber-900 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
              <span>Browse Catalog Matches</span> →
            </div>
          </div>

        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="bg-[#FAF0F2]/50 border-y border-[#F0E6E6] py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          
          <div className="text-center space-y-3">
            <div className="lumi-badge">Seamless Workflow</div>
            <h2 className="text-3xl sm:text-4xl font-extrabold font-outfit text-gray-900">
              How Your Analysis Works
            </h2>
            <p className="text-[#6B6565] max-w-xl mx-auto text-sm">
              Three simple steps to unlock your scientific beauty report in seconds.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            
            <div className="lumi-card p-6 space-y-3 bg-white">
              <div className="w-10 h-10 rounded-full bg-[#7D2E3B] text-white font-bold text-base flex items-center justify-center mx-auto font-outfit">
                1
              </div>
              <h3 className="font-bold text-lg text-gray-900 font-outfit">Capture or Upload</h3>
              <p className="text-xs text-[#6B6565] leading-relaxed">
                Take a photo using your camera or upload a clear, well-lit front portrait photo.
              </p>
            </div>

            <div className="lumi-card p-6 space-y-3 bg-white">
              <div className="w-10 h-10 rounded-full bg-[#7D2E3B] text-white font-bold text-base flex items-center justify-center mx-auto font-outfit">
                2
              </div>
              <h3 className="font-bold text-lg text-gray-900 font-outfit">AI Processing</h3>
              <p className="text-xs text-[#6B6565] leading-relaxed">
                MediaPipe extracts 3D landmarks while OpenCV measures lighting quality and CIE L*a*b* coordinates.
              </p>
            </div>

            <div className="lumi-card p-6 space-y-3 bg-white">
              <div className="w-10 h-10 rounded-full bg-[#7D2E3B] text-white font-bold text-base flex items-center justify-center mx-auto font-outfit">
                3
              </div>
              <h3 className="font-bold text-lg text-gray-900 font-outfit">Get Recommendations</h3>
              <p className="text-xs text-[#6B6565] leading-relaxed">
                View your complete face shape breakdown, shade matches, and download a styled PDF report.
              </p>
            </div>

          </div>

          <div className="text-center pt-4">
            <Link href="/analyze" className="lumi-btn-primary px-8 py-3.5 text-sm">
              Start Free Analysis Now
            </Link>
          </div>

        </div>
      </section>

      {/* Sample Beauty Report Preview Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          
          <div className="space-y-6">
            <div className="lumi-badge">Precision Output</div>
            <h2 className="text-3xl sm:text-4xl font-extrabold font-outfit text-gray-900 leading-tight">
              Comprehensive Personal Beauty Report
            </h2>
            <p className="text-sm text-[#6B6565] leading-relaxed">
              Every analysis generates a downloadable, high-resolution PDF report complete with your annotated 3D landmark mesh, exact geometric ratios, ITA° skin shade classification, and personalized product lists.
            </p>

            <ul className="space-y-3 text-xs text-[#6B6565]">
              <li className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-[10px]">✓</span>
                <span>Annotated facial landmark contour map</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-[10px]">✓</span>
                <span>ITA° angle and L*a*b* color coordinate breakdown</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-[10px]">✓</span>
                <span>Curated K-Beauty lipsticks, blushes & eyewear frames</span>
              </li>
            </ul>

            <div className="pt-2">
              <Link href="/analyze" className="lumi-btn-secondary py-3 px-6 text-xs">
                Generate My Personal PDF Report
              </Link>
            </div>
          </div>

          {/* Report Mockup Card */}
          <div className="lumi-card p-6 bg-white border border-[#EADCDC] space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-[#F0E6E6] pb-3">
              <div>
                <span className="font-bold text-gray-900 font-outfit text-sm">LumiFace Diagnostic Summary</span>
                <span className="block text-[10px] text-gray-400">Document Ref: #LF-84920</span>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-bold">VERIFIED ANALYSIS</span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-[#FAF7F2] border border-[#F0E6E6]">
                <span className="text-gray-400 block text-[10px]">FACE SHAPE</span>
                <span className="font-bold text-[#7D2E3B]">Oval (High Harmony)</span>
              </div>
              <div className="p-3 rounded-lg bg-[#FAF7F2] border border-[#F0E6E6]">
                <span className="text-gray-400 block text-[10px]">PERSONAL COLOR</span>
                <span className="font-bold text-purple-900">Summer Cool Hydrangea</span>
              </div>
            </div>

            <div className="space-y-2 pt-1">
              <span className="text-[11px] font-bold text-gray-800 uppercase tracking-wider block">Recommended Lip Shades</span>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 rounded-md bg-[#FDF2F4] border border-[#F5DDE1] flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-[#C86D7C]" />
                  <span className="font-medium text-gray-800 text-[11px]">Rosy Nude MLBB</span>
                </div>
                <div className="p-2 rounded-md bg-[#F5EFFB] border border-[#E5D9F2] flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-[#8A1C48]" />
                  <span className="font-medium text-gray-800 text-[11px]">Deep Berry Tint</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* Verified Customer Experiences */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center space-y-2">
          <div className="lumi-badge">User Experiences</div>
          <h2 className="text-3xl font-extrabold font-outfit text-gray-900">
            Trusted by K-Beauty Enthusiasts
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="lumi-card p-6 space-y-3">
            <div className="flex items-center gap-1 text-amber-500 text-sm">★★★★★</div>
            <p className="text-xs text-[#6B6565] leading-relaxed italic">
              "LumiFace accurately identified my cool undertone and recommended lip tints that perfectly match my Summer Cool seasonal palette. Highly scientific!"
            </p>
            <div className="text-xs font-bold text-gray-900 font-outfit pt-2 border-t border-[#F0E6E6]">
              Min-ji K. <span className="text-gray-400 font-normal">• Verified User</span>
            </div>
          </div>

          <div className="lumi-card p-6 space-y-3">
            <div className="flex items-center gap-1 text-amber-500 text-sm">★★★★★</div>
            <p className="text-xs text-[#6B6565] leading-relaxed italic">
              "The face shape analysis explained why certain eyewear frames never looked right on me. Switching to cat-eye frames made a huge difference."
            </p>
            <div className="text-xs font-bold text-gray-900 font-outfit pt-2 border-t border-[#F0E6E6]">
              Sophia L. <span className="text-gray-400 font-normal">• Verified User</span>
            </div>
          </div>

          <div className="lumi-card p-6 space-y-3">
            <div className="flex items-center gap-1 text-amber-500 text-sm">★★★★★</div>
            <p className="text-xs text-[#6B6565] leading-relaxed italic">
              "The PDF beauty report is so detailed. Having exact HEX codes for clothing and makeup shades saved me so much time when shopping."
            </p>
            <div className="text-xs font-bold text-gray-900 font-outfit pt-2 border-t border-[#F0E6E6]">
              Eun-ji S. <span className="text-gray-400 font-normal">• Verified User</span>
            </div>
          </div>
        </div>
      </section>

      {/* Call To Action Banner */}
      <section className="max-w-5xl mx-auto px-4">
        <div className="lumi-card p-10 text-center space-y-6 bg-gradient-to-br from-[#FAF0F2] via-white to-[#F5EFFB] border-[#EADCDC]">
          <h2 className="text-3xl font-extrabold font-outfit text-gray-900">
            Ready to Discover Your Personal Beauty Profile?
          </h2>
          <p className="text-xs sm:text-sm text-[#6B6565] max-w-lg mx-auto leading-relaxed">
            Begin your scientific facial geometry and skin spectrum analysis in seconds.
          </p>
          <Link href="/analyze" className="lumi-btn-primary px-8 py-3.5 text-sm">
            Launch LumiFace Analysis
          </Link>
        </div>
      </section>

    </div>
  )
}
