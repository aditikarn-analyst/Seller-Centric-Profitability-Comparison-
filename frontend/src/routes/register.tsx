import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { apiErrorMessage } from "@/lib/api";

export const Route = createFileRoute("/register")({
  head: () => ({
    meta: [
      { title: "Create account — Marketplace Profitability Analyzer" },
      { name: "description", content: "Create a seller account to save marketplace profit comparisons and track history." },
      { property: "og:title", content: "Create account — Marketplace Profitability Analyzer" },
      { property: "og:description", content: "Save your Amazon vs Flipkart profit comparisons." },
    ],
  }),
  component: RegisterPage,
});

function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await register(name, email, password);
      navigate({ to: "/" });
    } catch (err) {
      setError(apiErrorMessage(err, "Could not create your account."));
    } finally {
      setLoading(false);
    }
  }

  const inputCls =
    "w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring";

  return (
    <div className="mx-auto max-w-md px-4 py-14">
      <h1 className="font-display text-2xl font-bold">Create your account</h1>
      <p className="mt-1 text-sm text-muted-foreground">Save every comparison to your history.</p>
      <form onSubmit={onSubmit} className="card-surface mt-6 space-y-4 p-6">
        {error && (
          <p role="alert" className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </p>
        )}
        <div>
          <label className="mb-1 block text-sm font-medium" htmlFor="name">Name</label>
          <input id="name" required maxLength={100} className={inputCls} value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium" htmlFor="email">Email</label>
          <input id="email" type="email" required className={inputCls} value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium" htmlFor="password">Password</label>
          <input id="password" type="password" required minLength={6} className={inputCls} value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button type="submit" disabled={loading} className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-60">
          {loading && <Loader2 className="size-4 animate-spin" aria-hidden />} Create account
        </button>
        <p className="text-center text-sm text-muted-foreground">
          Already registered? <Link to="/login" className="font-medium text-foreground underline">Log in</Link>
        </p>
      </form>
    </div>
  );
}
