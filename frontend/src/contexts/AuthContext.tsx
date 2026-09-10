import { createContext, useContext, useEffect, useState } from "react";
import { api, logout as clearSession, type CurrentUser } from "../services/api";

type AuthState = { user: CurrentUser | null; loading: boolean; refresh: () => Promise<void>; signOut: () => Promise<void> };
const AuthContext = createContext<AuthState | undefined>(undefined);
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null); const [loading, setLoading] = useState(true);
  const refresh = async () => { if (!localStorage.getItem("ntp_access_token")) { setUser(null); setLoading(false); return; } try { const { data } = await api.get<CurrentUser>("/users/me"); setUser(data); } catch { clearSession(); setUser(null); } finally { setLoading(false); } };
  useEffect(() => { void refresh(); }, []);
  const signOut = async () => { try { await api.post("/auth/logout"); } finally { clearSession(); setUser(null); } };
  return <AuthContext.Provider value={{ user, loading, refresh, signOut }}>{children}</AuthContext.Provider>;
}
export function useAuth() { const state = useContext(AuthContext); if (!state) throw new Error("useAuth must be used within AuthProvider"); return state; }
