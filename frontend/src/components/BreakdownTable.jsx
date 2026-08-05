const ROWS = [
  ['Gross revenue', 'gross_revenue', false],
  ['Commission', 'commission', true],
  ['Fixed fee', 'fixed_fee', true],
  ['Shipping', 'shipping', true],
  ['Payment gateway', 'gateway', true],
  ['Fee base', 'fee_base', false],
  ['GST on fees', 'gst_on_fees', true],
  ['RTO-adjusted cost', 'rto_adjusted_cost', true],
  ['Net settlement (pre-TCS)', 'net_settlement', false],
  ['TCS withheld (credited back)', 'tcs_withheld', true],
  ['Cash at settlement', 'cash_at_settlement', false],
  ['Effective profit', 'effective_profit', false],
  ['Margin %', 'margin_pct', false],
  ['Break-even price', 'breakeven_price', false],
]

export default function BreakdownTable({ breakdown }) {
  return (
    <table className="w-full text-sm">
      <tbody>
        {ROWS.map(([label, key, isDeduction]) => (
          <tr key={key} className="border-b border-slate-100 last:border-0">
            <td className="py-1 text-slate-600">{label}</td>
            <td className={`py-1 text-right font-mono ${isDeduction ? 'text-red-600' : 'text-slate-900'}`}>
              {breakdown[key] == null
                ? '—'
                : `${isDeduction ? '− ' : ''}${key === 'margin_pct' ? `${breakdown[key]}%` : `₹${breakdown[key]}`}`}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
