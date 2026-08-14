import { Link, useNavigate } from "@tanstack/react-router";
import { BarChart3, LogOut } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-background/85 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-5 gap-y-2 px-4 py-3">
        <Link to="/" className="flex items-center gap-2 font-display font-semibold">
          <BarChart3 className="size-5 text-accent" aria-hidden />
          <span className="hidden sm:inline">Marketplace Profitability Analyzer</span>
          <span className="sm:hidden">MPA</span>
        </Link>

        <Link
          to="/"
          activeProps={{ className: "text-foreground" }}
          inactiveProps={{ className: "text-muted-foreground" }}
          activeOptions={{ exact: true }}
          className="text-sm hover:text-foreground"
        >
          Compare
        </Link>
        {user && (
          <Link
            to="/history"
            activeProps={{ className: "text-foreground" }}
            inactiveProps={{ className: "text-muted-foreground" }}
            className="text-sm hover:text-foreground"
          >
            History
          </Link>
        )}

        <div className="ml-auto flex items-center gap-3 text-sm">
          {user ? (
            <>
              <span className="hidden max-w-[180px] truncate text-muted-foreground sm:inline">
                {user.email}
              </span>
              <button
                type="button"
                onClick={() => {
                  logout();
                  navigate({ to: "/" });
                }}
                className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 hover:bg-muted"
              >
                <LogOut className="size-4" aria-hidden /> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-muted-foreground hover:text-foreground">
                Login
              </Link>
              <Link
                to="/register"
                className="rounded-md bg-primary px-3 py-1.5 font-medium text-primary-foreground hover:opacity-90"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
