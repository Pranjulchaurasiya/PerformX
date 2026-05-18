import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'
import toast from 'react-hot-toast'
import { Eye, EyeOff } from 'lucide-react'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { email, password })
      login(data.access_token, data.user)
      const role = data.user.role
      if (role === 'employee') navigate('/employee/dashboard')
      else if (role === 'manager') navigate('/manager/dashboard')
      else navigate('/admin/dashboard')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = (e: string, p: string) => { setEmail(e); setPassword(p) }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 to-primary-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white">PerformX</h1>
          <p className="text-primary-200 mt-2">Goal Setting & Progress Tracking</p>
        </div>
        <div className="card p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Sign in to your account</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Email address</label>
              <input type="email" className="input" value={email}
                onChange={e => setEmail(e.target.value)} required placeholder="you@company.com" />
            </div>
            <div>
              <label className="label">Password</label>
              <div className="relative">
                <input type={showPw ? 'text' : 'password'} className="input pr-10"
                  value={password} onChange={e => setPassword(e.target.value)} required placeholder="••••••••" />
                <button type="button" onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-2.5">
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <div className="mt-6 pt-5 border-t border-gray-100">
            <p className="text-xs text-gray-500 mb-3 font-medium">Demo accounts</p>
            <div className="grid grid-cols-3 gap-2">
              {[
                { label: 'Admin',     e: 'pranul@performx.com',   p: 'Admin@123' },
                { label: 'Manager',   e: 'akshay@performx.com',   p: 'Manager@123' },
                { label: 'Employee',  e: 'prince@performx.com',   p: 'Employee@123' },
              ].map(d => (
                <button key={d.label} type="button" onClick={() => fillDemo(d.e, d.p)}
                  className="text-xs px-2 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-600 transition-colors">
                  {d.label}
                </button>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-2 mt-2">
              {[
                { label: 'Mgr — Engineering', e: 'saandeep@performx.com', p: 'Manager@123' },
                { label: 'Emp — Returned',    e: 'vinayak@performx.com',  p: 'Employee@123' },
                { label: 'Emp — Fresh',       e: 'test@performx.com',     p: 'Employee@123' },
              ].map(d => (
                <button key={d.label} type="button" onClick={() => fillDemo(d.e, d.p)}
                  className="text-xs px-2 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-600 transition-colors">
                  {d.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
