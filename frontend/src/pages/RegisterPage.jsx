import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState(null)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function submit(e) {
    e.preventDefault()
    setError(null)
    try {
      await register(form.email, form.password, form.name)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <form onSubmit={submit} className="mx-auto max-w-sm space-y-4 rounded-lg border border-slate-200 bg-white p-6">
      <h1 className="text-xl font-semibold">Register</h1>
      {error && <div className="rounded bg-red-50 p-2 text-sm text-red-700">{error}</div>}
      <input
        placeholder="Name" required
        className="w-full rounded border border-slate-300 px-3 py-2"
        value={form.name} onChange={(e) => update('name', e.target.value)}
      />
      <input
        type="email" placeholder="Email" required
        className="w-full rounded border border-slate-300 px-3 py-2"
        value={form.email} onChange={(e) => update('email', e.target.value)}
      />
      <input
        type="password" placeholder="Password (min 8 chars)" required minLength={8}
        className="w-full rounded border border-slate-300 px-3 py-2"
        value={form.password} onChange={(e) => update('password', e.target.value)}
      />
      <button className="w-full rounded bg-slate-900 px-4 py-2 text-white hover:bg-slate-700">
        Create account
      </button>
    </form>
  )
}
