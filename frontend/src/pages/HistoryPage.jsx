import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function HistoryPage() {
  const { user } = useAuth()
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    client
      .get('/comparisons')
      .then((r) => setRows(r.data))
      .finally(() => setLoading(false))
  }, [user])

  if (!user) {
    return (
      <p className="py-8 text-slate-600">
        Please <Link to="/login" className="underline">log in</Link> to view your history.
      </p>
    )
  }

  if (loading) return <p className="py-8 text-slate-600">Loading…</p>

  return (
    <div className="py-4">
      <h1 className="mb-4 text-2xl font-bold">Comparison history</h1>
      {rows.length === 0 ? (
        <p className="text-slate-600">No saved comparisons yet.</p>
      ) : (
        <table className="w-full rounded-lg border border-slate-200 bg-white text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-slate-500">
              <th className="p-3">When</th>
              <th className="p-3">Platform ID</th>
              <th className="p-3 text-right">Gross</th>
              <th className="p-3 text-right">Profit</th>
              <th className="p-3 text-right">Margin</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.comparison_id} className="border-b border-slate-100 last:border-0">
                <td className="p-3 text-slate-500">{new Date(c.computed_at).toLocaleString()}</td>
                <td className="p-3">{c.platform_id}</td>
                <td className="p-3 text-right font-mono">₹{c.gross_revenue}</td>
                <td className="p-3 text-right font-mono">₹{c.effective_profit}</td>
                <td className="p-3 text-right font-mono">{c.margin_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
