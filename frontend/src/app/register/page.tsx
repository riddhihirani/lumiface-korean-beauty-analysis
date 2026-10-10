'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!fullName.trim() || fullName.trim().length < 2) {
      setErrorMsg('Please enter your full name (at least 2 characters).')
      return
    }
    if (!email || !email.includes('@')) {
      setErrorMsg('Please enter a valid email address.')
      return
    }
    if (!password || password.length < 6) {
      setErrorMsg('Password must be at least 6 characters long.')
      return
    }

    setIsLoading(true)
    setErrorMsg(null)

    try {
      const res = await fetch('http://127.0.0.1:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim(),
          password,
          full_name: fullName.trim()
        }),
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Registration failed.')
      }

      const data = await res.json()
      localStorage.setItem('lumiface_token', data.access_token)
      if (data.user) {
        localStorage.setItem('lumiface_user', JSON.stringify(data.user))
      }
      window.dispatchEvent(new Event('lumiface_auth_change'))
      router.push('/analyze')
    } catch (err: any) {
      setErrorMsg(err.message || 'Registration request error. Please try again.')
    } finally {
      setIsLoading(false)
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
            Create Your LumiFace Profile
          </h1>
          <p className="text-xs text-gray-500">
            Join LumiFace to unlock your personalized 3D facial analysis & K-beauty consultation report.
          </p>
        </div>

        {errorMsg && (
          <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium">
            ⚠️ {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1">
              Full Name
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Min-ah Park"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-[#EADCDC] text-xs focus:ring-2 focus:ring-[#C86D7C] focus:border-transparent outline-none bg-white text-gray-900"
            />
          </div>

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
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1">
              Password (Min. 6 Characters)
            </label>
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
            {isLoading ? 'Creating Consultation Account...' : 'Register Profile'}
          </button>
        </form>

        <div className="text-center text-xs text-gray-500 border-t border-[#F0E6E6] pt-4">
          Already registered?{' '}
          <Link href="/login" className="font-bold text-[#7D2E3B] hover:underline">
            Sign In to Your Account
          </Link>
        </div>

      </div>
    </div>
  )
}
