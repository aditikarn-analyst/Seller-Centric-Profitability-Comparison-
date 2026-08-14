import { Info, Trophy } from "lucide-react";
import type { ResearchResponse } from "@/lib/api";

/**
 * Research recommendation banner. Wording is deliberately non-absolute: a result
 * is "based on available verified fee data", never "universally best". When no
 * marketplace has sufficient verified data, this states that explicitly.
 */
export function RecommendationBanner({ data }: { data: ResearchResponse }) {
  const hasWinner = Boolean(data.definitive_winner);
  return (
    <section className="hero-surface overflow-hidden rounded-lg text-primary-foreground shadow-[var(--shadow-card)]">
      <div className="p-5 sm:p-7">
        <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-widest opacity-80">
          <Trophy className="size-4" aria-hidden /> Recommendation (source-verified data)
        </div>
        <h2 className="mt-2 font-display text-2xl font-semibold sm:text-3xl">
          {hasWinner ? `Recommended: ${data.definitive_winner}` : "No definitive recommendation"}
        </h2>
        <p className="mt-2 text-sm opacity-90 sm:text-base">{data.recommendation_note}</p>
        {data.definitive_candidates.length > 0 && (
          <p className="mt-2 text-xs opacity-75">
            Definitive candidates (sufficient verified data):{" "}
            {data.definitive_candidates.join(", ")}
          </p>
        )}
      </div>

      <div className="flex items-start gap-2 border-t border-white/15 bg-black/15 p-4 text-xs opacity-80 sm:p-5">
        <Info className="mt-0.5 size-4 shrink-0" aria-hidden />
        <p>
          {data.disclaimer} · Fee dataset {data.dataset_version}.
        </p>
      </div>
    </section>
  );
}
