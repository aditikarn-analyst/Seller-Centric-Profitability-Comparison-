import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)

  async function submit(e) {
    e.preventDefault()
    setError(null)
    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError('Incorrect email or password')
    }
  }

  return (
    <form onSubmit={submit} className="mx-auto max-w-sm space-y-4 rounded-lg border border-slate-200 bg-white p-6">
      <h1 className="text-xl font-semibold">Login</h1>
      {error && <div className="rounded bg-red-50 p-2 text-sm text-red-700">{error}</div>}
      <input
        type="email" placeholder="Email" required
        className="w-full rounded border border-slate-300 px-3 py-2"
        value={email} onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password" placeholder="Password" required
        className="w-full rounded border border-slate-300 px-3 py-2"
        value={password} onChange={(e) => setPassword(e.target.value)}
      />
      <button className="w-full rounded bg-slate-900 px-4 py-2 text-white hover:bg-slate-700">
        Login
      </button>
    </form>
  )
}
