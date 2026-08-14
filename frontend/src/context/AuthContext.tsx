import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { api, TOKEN_KEY, type User } from "@/lib/api";

interface AuthValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = window.localStorage.getItem(TOKEN_KEY);
    if (!stored) {
      setLoading(false);
      return;
    }
    setToken(stored);
    api
      .get<User>("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => {
        window.localStorage.removeItem(TOKEN_KEY);
        setToken(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const finishLogin = useCallback(async (accessToken: string) => {
    window.localStorage.setItem(TOKEN_KEY, accessToken);
    setToken(accessToken);
    const me = await api.get<User>("/auth/me");
    setUser(me.data);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await api.post<{ access_token: string; token_type: string }>("/auth/login", {
        email,
        password,
      });
      await finishLogin(res.data.access_token);
    },
    [finishLogin],
  );

  const register = useCallback(
    async (name: string, email: string, password: string) => {
      await api.post("/auth/register", { email, password, name });
      await login(email, password);
    },
    [login],
  );

  const logout = useCallback(() => {
    window.localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, token, loading, login, register, logout }),
    [user, token, loading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
