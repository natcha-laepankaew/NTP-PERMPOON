import type { ReactNode } from "react";

import { hasPermission, type Permission } from "../auth/roles";

import { useAuth } from "../contexts/AuthContext";

type PermissionGateProps = {
  permission?: Permission;
  permissions?: readonly Permission[];
  mode?: "any" | "all";
  children: ReactNode;
  fallback?: ReactNode;
};

export function PermissionGate({
  permission,
  permissions,
  mode = "any",
  children,
  fallback = null,
}: PermissionGateProps) {
  const { user } = useAuth();

  if (!user) {
    return <>{fallback}</>;
  }

  const requiredPermissions = permissions ?? (permission ? [permission] : []);

  if (requiredPermissions.length === 0) {
    return <>{fallback}</>;
  }

  const allowed =
    mode === "all"
      ? requiredPermissions.every((item) =>
          hasPermission(user.permissions, item),
        )
      : requiredPermissions.some((item) =>
          hasPermission(user.permissions, item),
        );

  return allowed ? <>{children}</> : <>{fallback}</>;
}
