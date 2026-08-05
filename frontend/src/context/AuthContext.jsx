import { createContext, useContext, useEffect, useState } from 'react'
import client from '../api/client'

// The single item of global state (README §10): the authenticated user.
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [user, setUser] = useState(null)

  useEffect(() => {
    if (!token) {
      localStorage.removeItem('token')
      setUser(null)
      return
    }
    localStorage.setItem('token', token)
    client
      .get('/auth/me')
      .then((r) => setUser(r.data))
      .catch(() => setToken(null))
  }, [token])

  async function login(email, password) {
    const r = await client.post('/auth/login', { email, password })
    setToken(r.data.access_token)
  }

  async function register(email, password, name) {
    await client.post('/auth/register', { email, password, name })
    await login(email, password)
  }

  function logout() {
    setToken(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
