import { useState } from 'react'

const CATEGORIES = [
  'Home & Kitchen',
  'Electronics Accessories',
  'Books',
  'Clothing',
  'Beauty & Personal Care',
  'Toys',
  'Sports & Fitness',
  'Automotive Accessories',
  'Grocery',
]

const INITIAL = {
  name: 'Kitchen container',
  category: 'Home & Kitchen',
  cost_price: '450.00',
  selling_price: '999.00',
  weight_g: 400,
}

export default function ProductForm({ onCompare, loading }) {
  const [form, setForm] = useState(INITIAL)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  function submit(e) {
    e.preventDefault()
    onCompare({
      ...form,
      weight_g: Number(form.weight_g),
    })
  }

  return (
    <form onSubmit={submit} className="grid grid-cols-1 gap-4 rounded-lg border border-slate-200 bg-white p-6 sm:grid-cols-2">
      <label className="flex flex-col text-sm">
        <span className="mb-1 text-slate-600">Product name</span>
        <input
          className="rounded border border-slate-300 px-3 py-2"
          value={form.name}
          onChange={(e) => update('name', e.target.value)}
        />
      </label>
      <label className="flex flex-col text-sm">
        <span className="mb-1 text-slate-600">Category</span>
        <select
          className="rounded border border-slate-300 px-3 py-2"
          value={form.category}
          onChange={(e) => update('category', e.target.value)}
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </label>
      <label className="flex flex-col text-sm">
        <span className="mb-1 text-slate-600">Cost price (₹)</span>
        <input
          type="number" step="0.01" min="0.01"
          className="rounded border border-slate-300 px-3 py-2"
          value={form.cost_price}
          onChange={(e) => update('cost_price', e.target.value)}
        />
      </label>
      <label className="flex flex-col text-sm">
        <span className="mb-1 text-slate-600">Selling price (₹)</span>
        <input
          type="number" step="0.01" min="0.01"
          className="rounded border border-slate-300 px-3 py-2"
          value={form.selling_price}
          onChange={(e) => update('selling_price', e.target.value)}
        />
      </label>
      <label className="flex flex-col text-sm">
        <span className="mb-1 text-slate-600">Weight (g)</span>
        <input
          type="number" min="1"
          className="rounded border border-slate-300 px-3 py-2"
          value={form.weight_g}
          onChange={(e) => update('weight_g', e.target.value)}
        />
      </label>
      <div className="flex items-end">
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-slate-900 px-4 py-2 text-white hover:bg-slate-700 disabled:opacity-50"
        >
          {loading ? 'Comparing…' : 'Compare platforms'}
        </button>
      </div>
    </form>
  )
}
