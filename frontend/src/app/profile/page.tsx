'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getApiUrl } from '@/lib/api'

interface UserProfile {
  id: number
  email: string
  full_name: string
  created_at: string
}

export default function ProfilePage() {
  const router = useRouter()
  const [user, setUser] = useState<UserProfile | null>(null)
  const [fullNameInput, setFullNameInput] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('lumiface_token')
    if (!token) {
      router.push('/login')
      return
    }

    fetchProfile(token)
  }, [])

  const fetchProfile = async (token: string) => {
    setIsLoading(true)
    try {
      const res = await fetch(getApiUrl('/api/auth/me'), {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (!res.ok) {
        localStorage.removeItem('lumiface_token')
        localStorage.removeItem('lumiface_user')
        router.push('/login')
        return
      }

      const data: UserProfile = await res.json()
      setUser(data)
      setFullNameInput(data.full_name)
      localStorage.setItem('lumiface_user', JSON.stringify(data))
    } catch (err: any) {
      setErrorMsg('Could not fetch user profile details.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMsg(null)
    setSuccessMsg(null)

    const token = localStorage.getItem('lumiface_token')
    if (!token) {
      router.push('/login')
      return
    }

    if (fullNameInput.trim().length < 2) {
      setErrorMsg('Full name must be at least 2 characters.')
      return
    }

    setIsSaving(true)
    try {
      const res = await fetch(getApiUrl('/api/auth/profile'), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ full_name: fullNameInput.trim() })
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Failed to update profile.')
      }

      const updatedUser: UserProfile = await res.json()
      setUser(updatedUser)
      localStorage.setItem('lumiface_user', JSON.stringify(updatedUser))
      setSuccessMsg('Profile updated successfully! Your updated name will appear on all future beauty blueprint reports.')
    } catch (err: any) {
      setErrorMsg(err.message || 'Unable to save profile changes.')
    } finally {
      setIsSaving(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('lumiface_token')
    localStorage.removeItem('lumiface_user')
    router.push('/login')
  }

  if (isLoading) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="animate-spin w-8 h-8 border-4 border-[#7D2E3B] border-t-transparent rounded-full mx-auto" />
        <p className="text-xs text-gray-500 font-medium">Loading user profile security context...</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8">
      
      {/* Page Title */}
      <div className="text-center space-y-2">
        <div className="lumi-badge">Personal Account Security</div>
        <h1 className="text-3xl font-extrabold font-outfit text-gray-900 tracking-tight">
          User Consultation Profile
        </h1>
        <p className="text-xs text-[#6B6565]">
          Manage your personal consultation profile and report preferences.
        </p>
      </div>

      {/* Main Profile Card */}
      <div className="lumi-card p-6 sm:p-8 space-y-6 bg-white">
        
        {/* User Avatar Banner */}
        <div className="flex items-center gap-4 p-4 rounded-2xl bg-[#FAF7F2] border border-[#F0E6E6]">
          <div className="w-14 h-14 rounded-full bg-[#FDF2F4] text-[#7D2E3B] flex items-center justify-center font-bold text-xl border border-[#F5DDE1] shrink-0">
            {user?.full_name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="font-bold font-outfit text-gray-900 text-lg truncate">
              {user?.full_name}
            </h2>
            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
            <p className="text-[10px] text-gray-400 mt-0.5">
              Member since: {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'Recently'}
            </p>
          </div>
        </div>

        {/* Alert Messages */}
        {errorMsg && (
          <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium">
            {errorMsg}
          </div>
        )}

        {successMsg && (
          <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium">
            {successMsg}
          </div>
        )}

        {/* Update Profile Form */}
        <form onSubmit={handleUpdateProfile} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-700 uppercase tracking-wider block">
              Full Name (Appears on Personal Beauty Reports)
            </label>
            <input
              type="text"
              value={fullNameInput}
              onChange={(e) => setFullNameInput(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-[#EADCDC] text-xs focus:ring-2 focus:ring-[#C86D7C] focus:border-transparent outline-none bg-white text-gray-900"
              placeholder="Enter your full name"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block">
              Email Address (Account Identifier)
            </label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="w-full px-4 py-3 rounded-xl border border-[#EADCDC] text-xs bg-gray-100 text-gray-500 cursor-not-allowed"
            />
          </div>

          <button
            type="submit"
            disabled={isSaving}
            className="w-full lumi-btn-primary py-3.5 text-xs font-bold shadow-sm disabled:opacity-50"
          >
            {isSaving ? 'Saving Changes...' : 'Save Profile Changes'}
          </button>
        </form>

        {/* Account Actions */}
        <div className="border-t border-[#F0E6E6] pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <button
            onClick={() => router.push('/analyze')}
            className="w-full sm:w-auto lumi-btn-secondary py-2.5 px-6 text-xs font-semibold"
          >
            ✨ Start Beauty Analysis
          </button>

          <button
            onClick={handleLogout}
            className="w-full sm:w-auto px-5 py-2.5 rounded-full border border-rose-200 bg-rose-50 hover:bg-rose-100 text-rose-800 text-xs font-semibold transition-colors"
          >
            🚪 Sign Out of Account
          </button>
        </div>

      </div>

    </div>
  )
}
