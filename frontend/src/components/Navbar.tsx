'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { getApiUrl } from '@/lib/api'

export default function Navbar() {
  const [apiHealth, setApiHealth] = useState<'online' | 'offline' | 'checking'>('checking')
  const [authToken, setAuthToken] = useState<string | null>(null)
  const [userFullName, setUserFullName] = useState<string | null>(null)
  const pathname = usePathname()
  const router = useRouter()

  const syncAuth = () => {
    const token = localStorage.getItem('lumiface_token')
    setAuthToken(token)
    const userStr = localStorage.getItem('lumiface_user')
    if (userStr) {
      try {
        const u = JSON.parse(userStr)
        setUserFullName(u.full_name || u.email)
      } catch {
        setUserFullName(null)
      }
    } else {
      setUserFullName(null)
    }
  }

  useEffect(() => {
    syncAuth()

    async function checkHealth() {
      try {
        const res = await fetch(getApiUrl('/api/health'), { cache: 'no-store' })
        if (res.ok) {
          const data = await res.json()
          if (data.status === 'healthy') {
            setApiHealth('online')
            return
          }
        }
        setApiHealth('offline')
      } catch (err) {
        setApiHealth('offline')
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 20000)

    window.addEventListener('lumiface_auth_change', syncAuth)
    return () => {
      clearInterval(interval)
      window.removeEventListener('lumiface_auth_change', syncAuth)
    }
  }, [pathname])

  const handleLogout = () => {
    localStorage.removeItem('lumiface_token')
    localStorage.removeItem('lumiface_user')
    window.dispatchEvent(new Event('lumiface_auth_change'))
    syncAuth()
    router.push('/login')
  }

  return (
    <header className="sticky top-0 z-50 bg-[#FAF7F2]/90 backdrop-blur-md border-b border-[#F0E6E6]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-[#7D2E3B] to-[#C86D7C] flex items-center justify-center text-white font-outfit font-bold text-lg shadow-xs group-hover:scale-105 transition-transform">
            L
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-bold tracking-tight text-gray-900 font-outfit">
              Lumi<span className="text-[#7D2E3B]">Face</span>
            </span>
            <span className="text-[9px] uppercase tracking-[0.2em] text-[#A44A59] font-medium -mt-1">
              Beauty Diagnostics
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-8">
          <Link 
            href="/" 
            className={`text-sm font-medium transition-colors ${pathname === '/' ? 'text-[#7D2E3B] font-semibold' : 'text-gray-600 hover:text-[#7D2E3B]'}`}
          >
            Home
          </Link>
          <Link 
            href="/#features" 
            className="text-sm font-medium text-gray-600 hover:text-[#7D2E3B] transition-colors"
          >
            Discover
          </Link>
          <Link 
            href="/#how-it-works" 
            className="text-sm font-medium text-gray-600 hover:text-[#7D2E3B] transition-colors"
          >
            How It Works
          </Link>
          <Link 
            href="/analyze" 
            className={`text-sm font-medium transition-colors ${pathname === '/analyze' ? 'text-[#7D2E3B] font-semibold' : 'text-gray-600 hover:text-[#7D2E3B]'}`}
          >
            AI Analysis
          </Link>
          {authToken && (
            <Link 
              href="/profile" 
              className={`text-sm font-medium transition-colors ${pathname === '/profile' ? 'text-[#7D2E3B] font-semibold' : 'text-gray-600 hover:text-[#7D2E3B]'}`}
            >
              My Profile
            </Link>
          )}
        </nav>

        {/* Action Controls & Health Status */}
        <div className="flex items-center gap-4">
          
          {/* API Status Badge */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-white border border-[#EADCDC] text-[11px] font-medium">
            <span className="text-gray-400">Engine:</span>
            {apiHealth === 'checking' && (
              <span className="text-amber-600 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" /> Connecting
              </span>
            )}
            {apiHealth === 'online' && (
              <span className="text-emerald-700 font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Online
              </span>
            )}
            {apiHealth === 'offline' && (
              <span className="text-rose-600 font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500" /> Offline
              </span>
            )}
          </div>

          {authToken ? (
            <div className="flex items-center gap-3">
              <Link
                href="/profile"
                className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#FDF2F4] border border-[#F5DDE1] text-xs font-bold text-[#7D2E3B] hover:bg-[#F5EFFB] transition-colors"
              >
                <span className="w-2 h-2 rounded-full bg-[#7D2E3B]" />
                <span className="truncate max-w-[120px]">{userFullName || 'Profile'}</span>
              </Link>
              <button 
                onClick={handleLogout}
                className="text-xs font-semibold text-gray-500 hover:text-[#7D2E3B] underline"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link 
                href="/login" 
                className="text-sm font-medium text-gray-700 hover:text-[#7D2E3B] transition-colors px-2 py-1"
              >
                Sign In
              </Link>
              <Link 
                href="/analyze" 
                className="lumi-btn-primary text-xs !py-2.5 !px-5"
              >
                Start Analysis
              </Link>
            </div>
          )}

        </div>
      </div>
    </header>
  )
}
