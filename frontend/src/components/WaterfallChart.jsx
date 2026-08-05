import { useEffect, useRef } from 'react'
import Plotly from 'plotly.js/lib/core'
import waterfall from 'plotly.js/lib/waterfall'

// README §10 chose Plotly specifically for the waterfall chart (RG8). The basic
// bundle lacks the waterfall trace, so we register only the waterfall module
// onto Plotly core — keeping the bundle small while getting the native trace.
Plotly.register([waterfall])

const num = (s) => parseFloat(s)

export default function WaterfallChart({ result }) {
  const ref = useRef(null)

  useEffect(() => {
    if (!result || !ref.current) return
    const b = result.breakdown

    const data = [
      {
        type: 'waterfall',
        orientation: 'v',
        measure: [
          'absolute', 'relative', 'relative', 'relative',
          'relative', 'relative', 'total',
        ],
        x: [
          'Selling price', '− Commission', '− Fixed fee', '− Shipping',
          '− Gateway', '− GST', '− RTO → Net',
        ],
        y: [
          num(b.gross_revenue),
          -num(b.commission),
          -num(b.fixed_fee),
          -num(b.shipping),
          -num(b.gateway),
          -num(b.gst_on_fees),
          -num(b.rto_adjusted_cost),
        ],
        connector: { line: { color: 'rgb(148,163,184)' } },
        decreasing: { marker: { color: '#ef4444' } },
        increasing: { marker: { color: '#22c55e' } },
        totals: { marker: { color: '#0f172a' } },
      },
    ]

    const layout = {
      title: `${result.platform}: ₹${b.gross_revenue} → ₹${b.net_settlement} net settlement`,
      margin: { t: 40, r: 10, b: 80, l: 50 },
      yaxis: { title: '₹' },
      showlegend: false,
    }

    Plotly.newPlot(ref.current, data, layout, { displayModeBar: false, responsive: true })
    return () => Plotly.purge(ref.current)
  }, [result])

  return <div ref={ref} className="h-80 w-full" />
}
