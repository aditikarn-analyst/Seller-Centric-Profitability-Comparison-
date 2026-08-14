import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { api, apiErrorMessage, type ComparisonRow } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export const Route = createFileRoute("/history")({
  head: () => ({
    meta: [
      { title: "Comparison history — Marketplace Profitability Analyzer" },
      { name: "description", content: "Review your saved marketplace profit comparisons, newest first." },
      { property: "og:title", content: "Comparison history — Marketplace Profitability Analyzer" },
      { property: "og:description", content: "Your saved Amazon vs Flipkart profit comparisons." },
    ],
  }),
  component: HistoryPage,
});

function HistoryPage() {
  const { user, loading: authLoading } = useAuth();
  const [rows, setRows] = useState<ComparisonRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    api
      .get<ComparisonRow[]>("/comparisons")
      .then((res) => setRows(res.data))
      .catch((err) => setError(apiErrorMessage(err, "Could not load your history.")))
      .finally(() => setLoading(false));
  }, [user]);

  if (authLoading) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-14 text-sm text-muted-foreground">Loading…</div>
    );
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-md px-4 py-16 text-center">
        <h1 className="font-display text-2xl font-bold">Your comparison history</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Log in to see the comparisons saved to your account.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Link to="/login" className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90">
            Log in
          </Link>
          <Link to="/register" className="rounded-md border border-border px-4 py-2 text-sm font-medium hover:bg-muted">
            Register
          </Link>
        </div>
      </div>
    );
  }

  const sorted = rows
    ? [...rows].sort((a, b) => new Date(b.computed_at).getTime() - new Date(a.computed_at).getTime())
    : [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="font-display text-3xl font-bold">Comparison history</h1>
      <p className="mt-1 text-sm text-muted-foreground">Every comparison saved to your account, newest first.</p>

      {error && (
        <p role="alert" className="mt-6 rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </p>
      )}

      {loading && (
        <div className="card-surface mt-6 flex items-center gap-3 p-8 text-sm text-muted-foreground">
          <Loader2 className="size-4 animate-spin" aria-hidden /> Loading history…
        </div>
      )}

      {!loading && rows && sorted.length === 0 && (
        <div className="card-surface mt-6 p-8 text-sm text-muted-foreground">
          No saved comparisons yet. Run one on the{" "}
          <Link to="/" className="font-medium text-foreground underline">Compare page</Link>.
        </div>
      )}

      {!loading && sorted.length > 0 && (
        <div className="card-surface mt-6 overflow-x-auto">
          <table className="w-full min-w-[640px] text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted-foreground">
                <th className="px-4 py-3 font-medium">Computed at</th>
                <th className="px-4 py-3 font-medium">Platform</th>
                <th className="px-4 py-3 text-right font-medium">Gross revenue</th>
                <th className="px-4 py-3 text-right font-medium">Effective profit</th>
                <th className="px-4 py-3 text-right font-medium">Margin</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((r) => (
                <tr key={String(r.comparison_id)} className="border-b border-border/60 last:border-0">
                  <td className="px-4 py-3 text-muted-foreground">{r.computed_at}</td>
                  <td className="px-4 py-3">{String(r.platform_id)}</td>
                  <td className="px-4 py-3 text-right tabular-nums">₹{r.gross_revenue}</td>
                  <td className="px-4 py-3 text-right font-medium tabular-nums">₹{r.effective_profit}</td>
                  <td className="px-4 py-3 text-right tabular-nums">{r.margin_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
