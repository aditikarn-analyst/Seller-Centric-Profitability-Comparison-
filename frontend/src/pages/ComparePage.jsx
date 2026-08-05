import { useState } from 'react'
import client from '../api/client'
import ProductForm from '../components/ProductForm'
import Recommendation from '../components/Recommendation'
import ResultCard from '../components/ResultCard'
import WaterfallChart from '../components/WaterfallChart'
import { useAuth } from '../context/AuthContext'

export default function ComparePage() {
  const { user } = useAuth()
  const [response, setResponse] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function onCompare(payload) {
    setLoading(true)
    setError(null)
    try {
      const r = await client.post('/compare', payload)
      setResponse(r.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Comparison failed')
      setResponse(null)
    } finally {
      setLoading(false)
    }
  }

  const winner = response?.results?.find((r) => r.rank === 1)

  return (
    <div className="space-y-6 py-4">
      <div>
        <h1 className="text-2xl font-bold">Compare platform profitability</h1>
        <p className="text-slate-600">
          Enter a product to see net seller profit per marketplace, itemised and explained.
          {!user && ' Sign in to save your comparison history.'}
        </p>
      </div>

      <ProductForm onCompare={onCompare} loading={loading} />

      {error && (
        <div className="rounded border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>
      )}

      {response && (
        <div className="space-y-6">
          <Recommendation recommendation={response.recommendation} />
          {winner && (
            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <WaterfallChart result={winner} />
            </div>
          )}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {response.results.map((r) => (
              <ResultCard key={r.platform} result={r} isWinner={r.rank === 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
