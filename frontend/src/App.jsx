import { Link, Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import ComparePage from './pages/ComparePage'
import HistoryPage from './pages/HistoryPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

function Navbar() {
  const { user, logout } = useAuth()
  return (
    <nav className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between p-4">
        <Link to="/" className="text-lg font-semibold text-slate-900">
          Marketplace Profitability Analyzer
        </Link>
        <div className="flex items-center gap-4 text-sm">
          <Link to="/" className="text-slate-600 hover:text-slate-900">Compare</Link>
          {user && (
            <Link to="/history" className="text-slate-600 hover:text-slate-900">History</Link>
          )}
          {user ? (
            <>
              <span className="text-slate-500">{user.email}</span>
              <button
                onClick={logout}
                className="rounded bg-slate-100 px-3 py-1 hover:bg-slate-200"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-slate-600 hover:text-slate-900">Login</Link>
              <Link
                to="/register"
                className="rounded bg-slate-900 px-3 py-1 text-white hover:bg-slate-700"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />
      <main className="mx-auto max-w-5xl p-4">
        <Routes>
          <Route path="/" element={<ComparePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
