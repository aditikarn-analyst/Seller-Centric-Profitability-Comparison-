export default function Recommendation({ recommendation }) {
  const r = recommendation
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <h2 className="text-xl font-semibold">
        Recommended: <span className="text-green-600">{r.winner}</span>
      </h2>
      <p className="mt-1 text-slate-600">
        Better by <strong>₹{r.margin_over_next}</strong> per unit than the next platform.
        Deciding factor: <strong>{r.deciding_factor}</strong>.
      </p>

      <h3 className="mt-4 text-sm font-medium text-slate-500">
        Why (signed contributions, sum to the gap)
      </h3>
      <ul className="mt-2 space-y-1">
        {r.explanation.map((item) => {
          const value = parseFloat(item.delta)
          const positive = value >= 0
          return (
            <li key={item.factor} className="flex justify-between text-sm">
              <span className="capitalize text-slate-600">{item.factor.replace('_', ' ')}</span>
              <span className={`font-mono ${positive ? 'text-green-600' : 'text-red-600'}`}>
                {positive ? '+' : ''}₹{item.delta}
              </span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
