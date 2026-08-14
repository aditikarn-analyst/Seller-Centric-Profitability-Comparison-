import axios from "axios";

// Base URL of the backend API. Set VITE_API_URL in front_end/.env (e.g.
// http://localhost:8000/api/v1). Falls back to a same-origin relative path so
// a reverse-proxy / same-origin deployment still works without the env var.
const ENV_API_URL = (import.meta.env as Record<string, string | undefined>).VITE_API_URL;
export const API_BASE_URL = ENV_API_URL && ENV_API_URL.length > 0 ? ENV_API_URL : "/api/v1";
export const TOKEN_KEY = "mpa_token";

export const api = axios.create({ baseURL: API_BASE_URL });

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = window.localStorage.getItem(TOKEN_KEY);
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function apiErrorMessage(err: unknown, fallback = "Something went wrong."): string {
  if (axios.isAxiosError(err)) {
    const d = err.response?.data as
      | { detail?: unknown; message?: string; error?: string }
      | undefined;
    const detail = d?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length) {
      const first = detail[0] as { msg?: string };
      if (first?.msg) return first.msg;
    }
    if (d?.message) return d.message;
    if (d?.error) return d.error;
    if (err.message) return err.message;
  }
  if (err instanceof Error) return err.message;
  return fallback;
}

export interface User {
  user_id: string | number;
  email: string;
  name: string;
  created_at: string;
}

export interface Breakdown {
  gross_revenue: string;
  commission: string;
  fixed_fee: string;
  shipping: string;
  gateway: string;
  fee_base: string;
  gst_on_fees: string;
  rto_adjusted_cost: string;
  net_settlement: string;
  tcs_withheld: string;
  cash_at_settlement: string;
  effective_profit: string;
  margin_pct: string;
  breakeven_price: string;
  [key: string]: string;
}

export interface PlatformResult {
  platform: string;
  rank: number;
  rule_id: number;
  breakdown: Breakdown;
}

export interface CompareResponse {
  product: {
    name: string;
    category: string;
    cost_price: string;
    selling_price: string;
    weight_g: number;
  };
  results: PlatformResult[];
  recommendation: {
    winner: string;
    margin_over_next: string;
    deciding_factor: string;
    explanation: { factor: string; delta: string }[];
  };
}

export interface ComparisonRow {
  comparison_id: string | number;
  product_id: string | number;
  platform_id: string | number;
  rule_id: string | number;
  gross_revenue: string;
  effective_profit: string;
  margin_pct: string;
  breakeven_price: string;
  explanation: unknown;
  computed_at: string;
}

/** Money values are strings from the API - display verbatim, never reformat. */
export const inr = (v: string) => `\u20B9${v}`;

// --- Research comparison (component-based, source-verified) ----------------

export interface FeeBreakdownItem {
  component: string;
  value_kind: string;
  amount_min: string | null;
  amount_max: string | null;
  verification_status: string;
  source_type: string;
  source_name: string | null;
  source_url: string | null;
  last_verified: string | null;
  notes: string | null;
}

export interface ResearchResult {
  marketplace: string;
  status: "COMPLETE" | "PARTIAL" | "UNAVAILABLE";
  definitive_candidate: boolean;
  ranking_eligible: boolean;
  total_fee_min: string | null;
  total_fee_max: string | null;
  net_profit_min: string | null;
  net_profit_max: string | null;
  profit_margin_min: string | null;
  profit_margin_max: string | null;
  fee_breakdown: FeeBreakdownItem[];
  verified_components: string[];
  partial_components: string[];
  unavailable_components: string[];
  missing_components: string[];
  assumptions: string[];
  limitations: string[];
  sources: { name: string | null; url: string | null; type: string }[];
}

export interface ResearchResponse {
  product: Record<string, unknown>;
  dataset_version: string;
  disclaimer: string;
  definitive_winner: string | null;
  definitive_candidates: string[];
  recommendation_note: string;
  excluded: { platform: string; reasons: string[] }[];
  results: ResearchResult[];
}
