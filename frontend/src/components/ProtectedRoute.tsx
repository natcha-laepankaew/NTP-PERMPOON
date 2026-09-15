import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import {
  hasAllowedRole,
  hasPermission,
  type Permission,
  type RoleName,
} from "../auth/roles";

function RouteLoading() {
  return (
    <main className="route-loading" aria-live="polite" aria-busy="true">
      <div className="spinner" />
      <span>Checking your session...</span>
    </main>
  );
}

export function ProtectedRoute() {
  const location = useLocation();
  const { user, loading } = useAuth();

  if (loading) return <RouteLoading />;
  return user ? (
    <Outlet />
  ) : (
    <Navigate to="/login" replace state={{ from: location }} />
  );
}

export function RoleRoute({
  allowedRoles,
}: Readonly<{ allowedRoles: readonly RoleName[] }>) {
  const location = useLocation();
  const { user, loading } = useAuth();

  if (loading) return <RouteLoading />;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  return hasAllowedRole(user.role.name, allowedRoles) ? (
    <Outlet />
  ) : (
    <Navigate to="/" replace />
  );
}

export function PermissionRoute({
  permissions,
  mode = "any",
}: Readonly<{
  permissions: readonly Permission[];
  mode?: "any" | "all";
}>) {
  const location = useLocation();
  const { user, loading } = useAuth();

  if (loading) {
    return <RouteLoading />;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const userPermissions = user.permissions ?? [];

  const allowed =
    mode === "all"
      ? permissions.every((permission) =>
          hasPermission(userPermissions, permission),
        )
      : permissions.some((permission) =>
          hasPermission(userPermissions, permission),
        );

  if (!allowed) {
    return <Navigate to="/" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
