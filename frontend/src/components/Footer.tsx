import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="bg-white border-t border-[#F0E6E6] pt-14 pb-10 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          
          {/* Brand Info */}
          <div className="space-y-3 md:col-span-2">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#7D2E3B] to-[#C86D7C] flex items-center justify-center text-white font-outfit font-bold text-base">
                L
              </div>
              <span className="text-xl font-bold font-outfit text-gray-900">
                Lumi<span className="text-[#7D2E3B]">Face</span>
              </span>
            </div>
            <p className="text-xs text-gray-500 max-w-md leading-relaxed">
              Precision 3D facial landmark geometry, CIE L*a*b* Individual Typology Angle diagnostics, and curated Korean personal beauty recommendations.
            </p>
          </div>

          {/* Quick Links */}
          <div className="space-y-2 text-xs">
            <h4 className="font-bold text-gray-900 uppercase tracking-wider font-outfit text-[11px]">Diagnostics</h4>
            <ul className="space-y-1.5 text-gray-600">
              <li><Link href="/analyze" className="hover:text-[#7D2E3B]">Face Shape Geometry</Link></li>
              <li><Link href="/analyze" className="hover:text-[#7D2E3B]">ITA° Skin Tone Analysis</Link></li>
              <li><Link href="/analyze" className="hover:text-[#7D2E3B]">Seasonal Color Swatches</Link></li>
              <li><Link href="/analyze" className="hover:text-[#7D2E3B]">K-Beauty Makeup Catalog</Link></li>
            </ul>
          </div>

          {/* Technology & Privacy */}
          <div className="space-y-2 text-xs">
            <h4 className="font-bold text-gray-900 uppercase tracking-wider font-outfit text-[11px]">Privacy & Trust</h4>
            <ul className="space-y-1.5 text-gray-500">
              <li>Local facial processing</li>
              <li>Zero external image uploads</li>
              <li>Standardized Lab color space</li>
              <li>MediaPipe 468 3D Mesh</li>
            </ul>
          </div>

        </div>

        <div className="border-t border-[#F0E6E6] pt-6 flex flex-col sm:flex-row items-center justify-between text-[11px] text-gray-400 gap-2">
          <p>© 2026 LumiFace Diagnostics Inc. All rights reserved.</p>
          <p className="font-outfit">Your Beauty, Scientifically Understood.</p>
        </div>
      </div>
    </footer>
  )
}
