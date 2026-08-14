import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  Loader2,
  AlertCircle,
  ArrowRight,
  BarChart3,
  Grid2x2,
  Package,
  ReceiptIndianRupee,
  Scale,
  Sparkles,
  Store,
  Tag,
  Truck,
  Wallet,
} from "lucide-react";
import { api, apiErrorMessage, type ResearchResponse } from "@/lib/api";
import { RecommendationBanner } from "@/components/mpa/RecommendationBanner";
import { ResultCard } from "@/components/mpa/ResultCard";
import { PageBackdrop } from "@/components/mpa/PageBackdrop";

const CATEGORIES = [
  "Home & Kitchen",
  "Electronics Accessories",
  "Books",
  "Clothing",
  "Beauty & Personal Care",
  "Toys",
  "Sports & Fitness",
  "Automotive Accessories",
  "Grocery",
];

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Compare Marketplace Profit — Amazon vs Flipkart Fees" },
      {
        name: "description",
        content:
          "Compare net profit per unit across Amazon and Flipkart after commissions, shipping, GST, TCS and returns for Indian sellers.",
      },
      { property: "og:title", content: "Marketplace Profitability Analyzer" },
      {
        property: "og:description",
        content:
          "See which marketplace leaves you more profit after all fees, taxes and returns.",
      },
    ],
  }),
  component: ComparePage,
});

function ComparePage() {
  const [form, setForm] = useState({
    name: "",
    category: "Home & Kitchen",
    cost_price: "450.00",
    selling_price: "999.00",
    weight_g: "400",
    fulfillment_type: "",
  });
  const [data, setData] = useState<ResearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<ResearchResponse>("/compare/research", {
        name: form.name || null,
        category: form.category,
        cost_price: form.cost_price,
        selling_price: form.selling_price,
        weight_g: Number.parseInt(form.weight_g, 10),
        fulfillment_type: form.fulfillment_type || null,
      });
      setData(res.data);
    } catch (err) {
      setData(null);
      setError(apiErrorMessage(err, "Could not compare this product."));
    } finally {
      setLoading(false);
    }
  }

  const sortedResults = data
    ? [...data.results].sort((a, b) => {
        if (a.ranking_eligible !== b.ranking_eligible) return a.ranking_eligible ? -1 : 1;
        const pa = Number.parseFloat(a.net_profit_min ?? a.net_profit_max ?? "-1e9");
        const pb = Number.parseFloat(b.net_profit_min ?? b.net_profit_max ?? "-1e9");
        return pb - pa;
      })
    : [];
  const labelCls = "mb-1.5 block text-sm font-medium text-foreground";
  const iconCls =
    "pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground";

  return (
    <div className="relative isolate">
      <PageBackdrop />

      <div className="mx-auto max-w-6xl px-4 pb-16 pt-10 sm:pt-14">
        {/* Hero */}
        <header className="rise-in max-w-3xl">
          <span className="gradient-brand inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold tracking-wide text-primary-foreground shadow-[var(--shadow-glow)]">
            <Sparkles className="size-3.5" aria-hidden /> Marketplace Analytics
          </span>
          <h1 className="mt-5 font-display text-4xl font-extrabold leading-[1.05] tracking-tight sm:text-5xl lg:text-[48px]">
            Know exactly what each marketplace leaves you
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-muted-foreground">
            Enter your product economics once and see net profit per unit after commission,
            shipping, payment gateway, GST, TCS and returns — side by side.
          </p>
        </header>

        {/* Feature strip */}
        <ul className="rise-in mt-7 grid gap-3 sm:grid-cols-3">
          {[
            { icon: Store, text: "Compare Amazon, Flipkart & Meesho" },
            { icon: Truck, text: "Shipping & GST included" },
            { icon: BarChart3, text: "Full profit breakdown" },
          ].map((f) => (
            <li
              key={f.text}
              className="glass-card hover-lift flex items-center gap-3 px-4 py-3 text-sm font-medium"
            >
              <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-primary/10 text-primary">
                <f.icon className="size-4" aria-hidden />
              </span>
              <span className="min-w-0">{f.text}</span>
            </li>
          ))}
        </ul>

        <div className="mt-8 grid gap-6 lg:grid-cols-[380px_1fr]">
          <form
            onSubmit={onSubmit}
            className="glass-card hover-lift rise-in h-fit space-y-5 p-6 lg:sticky lg:top-20"
          >
            <div>
              <h2 className="font-display text-lg font-bold">Product details</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                All money values are sent exactly as typed.
              </p>
            </div>

            <div>
              <label className={labelCls} htmlFor="name">
                Product name <span className="font-normal text-muted-foreground">(optional)</span>
              </label>
              <div className="relative">
                <Package className={iconCls} aria-hidden />
                <input
                  id="name"
                  className="field-input"
                  value={form.name}
                  onChange={set("name")}
                  placeholder="Steel water bottle"
                  maxLength={120}
                />
              </div>
            </div>

            <div>
              <label className={labelCls} htmlFor="category">
                Category
              </label>
              <div className="relative">
                <Grid2x2 className={iconCls} aria-hidden />
                <select
                  id="category"
                  className="field-input appearance-none pr-9"
                  value={form.category}
                  onChange={set("category")}
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
                <ArrowRight
                  className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 rotate-90 text-muted-foreground"
                  aria-hidden
                />
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className={labelCls} htmlFor="cost">
                  Cost price (₹)
                </label>
                <div className="relative">
                  <Wallet className={iconCls} aria-hidden />
                  <input
                    id="cost"
                    className="field-input"
                    inputMode="decimal"
                    required
                    value={form.cost_price}
                    onChange={set("cost_price")}
                  />
                </div>
              </div>
              <div>
                <label className={labelCls} htmlFor="sell">
                  Selling price (₹)
                </label>
                <div className="relative">
                  <Tag className={iconCls} aria-hidden />
                  <input
                    id="sell"
                    className="field-input"
                    inputMode="decimal"
                    required
                    value={form.selling_price}
                    onChange={set("selling_price")}
                  />
                </div>
              </div>
            </div>

            <div>
              <label className={labelCls} htmlFor="weight">
                Weight (grams)
              </label>
              <div className="relative">
                <Scale className={iconCls} aria-hidden />
                <input
                  id="weight"
                  className="field-input"
                  type="number"
                  min={1}
                  step={1}
                  required
                  value={form.weight_g}
                  onChange={set("weight_g")}
                />
              </div>
            </div>

            <div>
              <label className={labelCls} htmlFor="fulfillment">
                Fulfilment <span className="font-normal text-muted-foreground">(advanced, optional)</span>
              </label>
              <div className="relative">
                <Truck className={iconCls} aria-hidden />
                <select
                  id="fulfillment"
                  className="field-input appearance-none pr-9"
                  value={form.fulfillment_type}
                  onChange={set("fulfillment_type")}
                >
                  <option value="">Any</option>
                  <option value="SELF_SHIP">Self-ship</option>
                  <option value="PLATFORM_FULFILLED">Platform-fulfilled</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="gradient-brand group inline-flex w-full items-center justify-center gap-2 rounded-xl px-5 py-3.5 text-sm font-semibold text-primary-foreground shadow-[var(--shadow-glow)] transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_18px_40px_-12px_color-mix(in_oklab,var(--color-primary)_65%,transparent)] active:scale-[0.99] disabled:opacity-60 disabled:hover:scale-100"
            >
              {loading && <Loader2 className="size-4 animate-spin" aria-hidden />}
              {loading ? "Comparing…" : "Compare Marketplace Profitability"}
              {!loading && (
                <ArrowRight
                  className="size-4 transition-transform duration-300 group-hover:translate-x-1"
                  aria-hidden
                />
              )}
            </button>
          </form>

          <div className="space-y-6">
          {error && (
            <div role="alert" className="rise-in flex items-start gap-3 rounded-2xl border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
              <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden />
              <p>{error}</p>
            </div>
          )}

          {loading && !data && (
            <div className="glass-card flex flex-col items-center gap-4 p-12 text-center">
              <span className="grid size-14 place-items-center rounded-2xl bg-primary/10 text-primary">
                <Loader2 className="size-6 animate-spin" aria-hidden />
              </span>
              <p className="text-sm font-medium">Crunching marketplace fees…</p>
              <div className="w-full max-w-sm space-y-2">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="h-3 animate-pulse rounded-full bg-muted"
                    style={{ width: `${100 - i * 18}%`, animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
            </div>
          )}

          {!loading && !data && !error && (
            <div className="glass-card rise-in flex flex-col items-center gap-5 p-10 text-center sm:p-14">
              <div className="relative grid size-24 place-items-center rounded-2xl bg-primary/8">
                <div className="dot-grid absolute inset-0 rounded-2xl opacity-10" />
                <div className="flex items-end gap-1.5">
                  <span className="block w-3 rounded-t bg-primary/70" style={{ height: 22 }} />
                  <span className="block w-3 rounded-t bg-secondary/70" style={{ height: 38 }} />
                  <span className="block w-3 rounded-t bg-accent/70" style={{ height: 30 }} />
                  <span className="block w-3 rounded-t bg-positive/70" style={{ height: 48 }} />
                </div>
                <ReceiptIndianRupee
                  className="absolute -right-2 -top-2 size-7 rounded-lg bg-card p-1 text-primary shadow-[var(--shadow-card)]"
                  aria-hidden
                />
              </div>
              <h2 className="font-display text-xl font-bold">No comparison yet</h2>
              <p className="max-w-md text-sm leading-relaxed text-muted-foreground">
                Enter your product details to compare profitability across marketplaces. You'll get
                a recommended platform, a revenue waterfall and a full itemised fee breakdown.
              </p>
            </div>
          )}

          {data && (
            <div className="rise-in space-y-6">
              <RecommendationBanner data={data} />
              <div className="grid gap-4 md:grid-cols-2">
                {sortedResults.map((r) => (
                  <ResultCard
                    key={r.marketplace}
                    result={r}
                    winner={r.marketplace === data.definitive_winner}
                  />
                ))}
              </div>
            </div>
          )}
          </div>
        </div>
      </div>
    </div>
  );
}
