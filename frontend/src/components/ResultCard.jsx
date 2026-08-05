import { useState } from 'react'
import BreakdownTable from './BreakdownTable'

export default function ResultCard({ result, isWinner }) {
  const [open, setOpen] = useState(false)
  const b = result.breakdown

  return (
    <div className={`rounded-lg border bg-white p-5 ${isWinner ? 'border-green-500 ring-1 ring-green-500' : 'border-slate-200'}`}>
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-medium text-slate-500">Rank #{result.rank}</span>
          <h3 className="text-lg font-semibold">{result.platform}</h3>
        </div>
        {isWinner && (
          <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
            Recommended
          </span>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-4">
        <span className="text-2xl font-bold text-slate-900">₹{b.effective_profit}</span>
        <span className="text-sm text-slate-500">profit · {b.margin_pct}% margin</span>
      </div>

      <button
        onClick={() => setOpen((v) => !v)}
        className="mt-3 text-sm text-slate-600 underline hover:text-slate-900"
      >
        {open ? 'Hide' : 'Show'} fee breakdown
      </button>
      {open && (
        <div className="mt-3">
          <BreakdownTable breakdown={b} />
        </div>
      )}
    </div>
  )
}
