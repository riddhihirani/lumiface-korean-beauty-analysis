'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [forgotMsg, setForgotMsg] = useState<string | null>(null)
  const [isForgotOpen, setIsForgotOpen] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setErrorMsg('Please enter both email address and password.')
      return
    }

    setIsLoading(true)
    setErrorMsg(null)

    try {
      let res: Response
      try {
        res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email.trim(), password }),
        })
      } catch {
        res = await fetch('http://127.0.0.1:8000/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email.trim(), password }),
        })
      }

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Authentication failed. Please check credentials.')
      }

      const data = await res.json()
      localStorage.setItem('lumiface_token', data.access_token)
      if (data.user) {
        localStorage.setItem('lumiface_user', JSON.stringify(data.user))
      }
      window.dispatchEvent(new Event('lumiface_auth_change'))
      router.push('/analyze')
    } catch (err: any) {
      setErrorMsg(err.message || 'Login request error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleForgotPassword = async () => {
    if (!email || !email.includes('@')) {
      setErrorMsg('Please enter a valid email address first to request a password reset.')
      return
    }

    try {
      let res: Response
      try {
        res = await fetch('/api/auth/forgot-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email.trim() }),
        })
      } catch {
        res = await fetch('http://127.0.0.1:8000/api/auth/forgot-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email.trim() }),
        })
      }
      const data = await res.json()
      setForgotMsg(data.message)
      setIsForgotOpen(true)
    } catch (err: any) {
      setForgotMsg('Password reset request error.')
      setIsForgotOpen(true)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md lumi-card p-8 sm:p-10 space-y-6 bg-white">
        
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-[#7D2E3B] to-[#C86D7C] flex items-center justify-center text-white font-outfit font-bold text-xl mx-auto mb-2 shadow-md">
            L
          </div>
          <h1 className="text-2xl font-bold font-outfit text-gray-900 tracking-tight">
            Welcome to LumiFace
          </h1>
          <p className="text-xs text-gray-500">
            Sign in to access your personal beauty consultation blueprint.
          </p>
        </div>

        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium space-y-2">
            <div>⚠️ {errorMsg}</div>
            {errorMsg.includes('Incorrect email or password') && (
              <div className="pt-2 border-t border-rose-200/60 flex items-center justify-between text-[11px]">
                <span className="text-gray-600">Don't have an account with this email yet?</span>
                <Link href="/register" className="font-bold text-[#7D2E3B] hover:underline shrink-0 ml-2">
                  Register for Free →
                </Link>
              </div>
            )}
          </div>
        )}

        {isForgotOpen && forgotMsg && (
          <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs font-medium space-y-2">
            <div className="font-bold flex items-center justify-between">
              <span>Password Recovery Notice</span>
              <button onClick={() => setIsForgotOpen(false)} className="text-gray-400 hover:text-gray-700 text-sm">✕</button>
            </div>
            <div>{forgotMsg}</div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              required
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-[#EADCDC] text-xs focus:ring-2 focus:ring-[#C86D7C] focus:border-transparent outline-none bg-white text-gray-900"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs font-bold uppercase tracking-wider text-gray-700">
                Password
              </label>
              <button
                type="button"
                onClick={handleForgotPassword}
                className="text-[11px] font-semibold text-[#7D2E3B] hover:underline"
              >
                Forgot Password?
              </button>
            </div>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-[#EADCDC] text-xs focus:ring-2 focus:ring-[#C86D7C] focus:border-transparent outline-none bg-white text-gray-900 pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700 text-xs font-bold"
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full lumi-btn-primary py-3.5 text-xs font-bold shadow-md disabled:opacity-50"
          >
            {isLoading ? 'Authenticating Profile...' : 'Sign In to LumiFace'}
          </button>
        </form>

        <div className="text-center text-xs text-gray-500 border-t border-[#F0E6E6] pt-4">
          Don't have a personal account yet?{' '}
          <Link href="/register" className="font-bold text-[#7D2E3B] hover:underline">
            Register for Free
          </Link>
        </div>

      </div>
    </div>
  )
}
