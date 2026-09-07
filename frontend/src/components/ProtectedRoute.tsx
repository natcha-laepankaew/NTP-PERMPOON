import { Navigate, Outlet, useLocation } from "react-router-dom";
import { hasRole, isAuthenticated } from "../services/api";

export function ProtectedRoute() {
  const location = useLocation();
  return isAuthenticated() ? (
    <Outlet />
  ) : (
    <Navigate to="/login" replace state={{ from: location }} />
  );
}

export function SuperAdminRoute() {
  return isAuthenticated() && hasRole("SUPER_ADMIN") ? (
    <Outlet />
  ) : (
    <Navigate to="/" replace />
  );
}
