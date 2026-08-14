import { useState } from "react";
import { ChevronDown, Crown, ShieldAlert, ShieldCheck, ShieldQuestion } from "lucide-react";
import type { FeeBreakdownItem, ResearchResult } from "@/lib/api";

const STATUS_STYLE: Record<string, string> = {
  COMPLETE: "bg-positive/15 text-positive",
  PARTIAL: "bg-amber-500/15 text-amber-600 dark:text-amber-400",
  UNAVAILABLE: "bg-negative/15 text-negative",
};

const CONF_STYLE: Record<string, string> = {
  VERIFIED: "bg-positive/15 text-positive",
  PARTIALLY_VERIFIED: "bg-amber-500/15 text-amber-600 dark:text-amber-400",
  NOT_PUBLICLY_VERIFIABLE: "bg-negative/15 text-negative",
  ASSUMED: "bg-muted text-muted-foreground",
};

const label = (s: string) => s.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());

function profitText(r: ResearchResult): string {
  const { net_profit_min: lo, net_profit_max: hi } = r;
  if (lo && hi && lo !== hi) return `₹${lo} – ₹${hi}`;
  if (lo && hi && lo === hi) return `₹${lo}`;
  if (!lo && hi) return `up to ₹${hi}`;
  return "—";
}

function amountText(c: FeeBreakdownItem): string {
  if (c.value_kind === "NOT_VERIFIABLE") return "not disclosed";
  if (c.amount_min && c.amount_max && c.amount_min !== c.amount_max) return `₹${c.amount_min}–₹${c.amount_max}`;
  if (c.amount_min && !c.amount_max) return `from ₹${c.amount_min}`;
  return c.amount_min ? `₹${c.amount_min}` : "—";
}

export function ResultCard({ result, winner }: { result: ResearchResult; winner: boolean }) {
  const [open, setOpen] = useState(false);
  const r = result;
  const rangeNote = !r.net_profit_min && r.net_profit_max
    ? "best case only — worst case not bounded from public data"
    : r.net_profit_min && r.net_profit_max && r.net_profit_min !== r.net_profit_max
      ? "range (some fees are published as ranges)"
      : null;

  return (
    <article className={"card-surface overflow-hidden " + (winner ? "ring-2 ring-accent" : "")}>
      <div className="flex items-start justify-between gap-4 p-5">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-display text-xl font-semibold">{r.marketplace}</h3>
            {winner && (
              <span className="inline-flex items-center gap-1 rounded-full bg-accent px-2 py-0.5 text-[11px] font-semibold text-accent-foreground">
                <Crown className="size-3" aria-hidden /> Recommended
              </span>
            )}
            <span className={"rounded-full px-2 py-0.5 text-[11px] font-semibold " + (STATUS_STYLE[r.status] ?? "")}>
              {label(r.status)}
            </span>
            {!r.ranking_eligible && (
              <span className="rounded-full bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">
                Not in definitive ranking
              </span>
            )}
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            Net profit: <span className="font-medium text-foreground">{profitText(r)}</span>
            {rangeNote ? ` · ${rangeNote}` : ""}
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Total fees</p>
          <p className="font-display text-lg font-bold tabular-nums">
            {r.total_fee_min ? `₹${r.total_fee_min}` : "—"}
            {r.total_fee_max && r.total_fee_max !== r.total_fee_min ? `–₹${r.total_fee_max}` : ""}
          </p>
          {(r.profit_margin_min || r.profit_margin_max) && (
            <p className="text-xs text-muted-foreground tabular-nums">
              {r.profit_margin_min ?? r.profit_margin_max}
              {r.profit_margin_max && r.profit_margin_max !== r.profit_margin_min ? `–${r.profit_margin_max}` : ""}% margin
            </p>
          )}
        </div>
      </div>

      {/* Data Source & Assumptions — always visible, concise */}
      <div className="border-t border-border px-5 py-3 text-xs">
        <div className="flex flex-wrap gap-x-4 gap-y-1">
          {r.verified_components.length > 0 && (
            <span className="inline-flex items-center gap-1 text-positive">
              <ShieldCheck className="size-3.5" aria-hidden /> Verified: {r.verified_components.map(label).join(", ")}
            </span>
          )}
          {r.partial_components.length > 0 && (
            <span className="inline-flex items-center gap-1 text-amber-600 dark:text-amber-400">
              <ShieldQuestion className="size-3.5" aria-hidden /> Partial: {r.partial_components.map(label).join(", ")}
            </span>
          )}
          {(r.unavailable_components.length > 0 || r.missing_components.length > 0) && (
            <span className="inline-flex items-center gap-1 text-negative">
              <ShieldAlert className="size-3.5" aria-hidden /> Unavailable:{" "}
              {[...r.unavailable_components, ...r.missing_components].map(label).join(", ")}
            </span>
          )}
        </div>
        {r.limitations.length > 0 && (
          <ul className="mt-2 list-disc space-y-0.5 pl-4 text-muted-foreground">
            {r.limitations.map((l, i) => (
              <li key={i}>{l}</li>
            ))}
          </ul>
        )}
      </div>

      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center justify-between border-t border-border px-5 py-3 text-sm font-medium hover:bg-muted"
      >
        Fee breakdown & sources
        <ChevronDown className={"size-4 transition-transform " + (open ? "rotate-180" : "")} />
      </button>

      {open && (
        <div className="border-t border-border">
          <table className="w-full text-sm">
            <tbody>
              {r.fee_breakdown.map((c) => (
                <tr key={c.component} className="border-b border-border/60 last:border-0 align-top">
                  <th scope="row" className="px-5 py-2 text-left font-normal text-muted-foreground">
                    {label(c.component)}
                    {c.source_url && (
                      <a href={c.source_url} target="_blank" rel="noreferrer"
                         className="ml-2 text-[11px] underline opacity-70 hover:opacity-100">
                        source
                      </a>
                    )}
                  </th>
                  <td className="px-3 py-2 tabular-nums">{amountText(c)}</td>
                  <td className="px-5 py-2 text-right">
                    <span className={"rounded-full px-2 py-0.5 text-[10px] font-medium " + (CONF_STYLE[c.verification_status] ?? "bg-muted")}>
                      {label(c.verification_status)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {r.assumptions.length > 0 && (
            <p className="px-5 py-3 text-xs text-muted-foreground">
              Assumptions: {r.assumptions.join(" ")}
            </p>
          )}
        </div>
      )}
    </article>
  );
}
