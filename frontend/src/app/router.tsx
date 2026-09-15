import { Route, Routes } from "react-router-dom";

import { MainLayout } from "../layouts/MainLayout";

import { DashboardPage } from "../pages/DashboardPage";
import { DispatchPage } from "../pages/DispatchPage";
import { LoginPage } from "../pages/LoginPage";
import { HistoryPage } from "../pages/HistoryPage";
import { JobsPage } from "../pages/JobsPage";
import { EmployeesPage } from "../pages/EmployeesPage";
import { VehiclesPage } from "../pages/VehiclesPage";
import { PlaceholderPage } from "../pages/PlaceholderPage";
import { RolesPermissionsPage } from "../pages/RolesPermissionsPage";
import { AuditLogsPage } from "../pages/AuditLogsPage";
import { CompleteProfilePage } from "../pages/CompleteProfilePage";
import { ProfilePage } from "../pages/ProfilePage";

import {
  ProtectedRoute,
  RoleRoute,
  PermissionRoute,
} from "../components/ProtectedRoute";

import { ROLE_ACCESS, PERMISSIONS } from "../auth/roles";

export function AppRouter() {
  return (
    <Routes>
      {/* =========================
          PUBLIC
      ========================= */}
      <Route path="/login" element={<LoginPage />} />

      {/* =========================
          AUTHENTICATED
      ========================= */}
      <Route element={<ProtectedRoute />}>
        {/* Profile completion */}
        <Route path="/complete-profile" element={<CompleteProfilePage />} />

        <Route element={<MainLayout />}>
          {/* =========================
              DASHBOARD
          ========================= */}
          <Route
            element={
              <PermissionRoute permissions={[PERMISSIONS.DASHBOARD_VIEW]} />
            }
          >
            <Route path="/" element={<DashboardPage />} />
          </Route>

          {/* =========================
              MY PROFILE
          ========================= */}
          <Route
            element={
              <PermissionRoute permissions={[PERMISSIONS.PROFILE_VIEW]} />
            }
          >
            <Route path="/profile" element={<ProfilePage />} />
          </Route>

          {/* =========================
              DISPATCH
          ========================= */}
          <Route
            element={
              <PermissionRoute permissions={[PERMISSIONS.DISPATCH_VIEW]} />
            }
          >
            <Route path="/dispatch" element={<DispatchPage />} />
          </Route>

          {/* =========================
              JOBS
              ADMIN / MANAGER / DRIVER
              ตาม permission
          ========================= */}
          <Route
            element={
              <PermissionRoute
                permissions={[PERMISSIONS.JOBS_VIEW, PERMISSIONS.JOBS_VIEW_OWN]}
              />
            }
          >
            <Route path="/jobs" element={<JobsPage />} />
          </Route>

          {/* =========================
              JOB HISTORY
          ========================= */}
          <Route
            element={
              <PermissionRoute permissions={[PERMISSIONS.HISTORY_VIEW]} />
            }
          >
            <Route path="/history" element={<HistoryPage />} />
          </Route>

          {/* =========================
              EMPLOYEES
          ========================= */}
          <Route
            element={
              <PermissionRoute permissions={[PERMISSIONS.EMPLOYEES_VIEW]} />
            }
          >
            <Route path="/employees" element={<EmployeesPage />} />
          </Route>

          {/* =========================
              VEHICLES
          ========================= */}
          <Route
            element={
              <PermissionRoute permissions={[PERMISSIONS.VEHICLES_VIEW]} />
            }
          >
            <Route path="/vehicles" element={<VehiclesPage />} />
          </Route>

          {/* =========================
              SYSTEM ADMIN
              ADMINISTRATOR ONLY
          ========================= */}
          <Route
            element={<RoleRoute allowedRoles={ROLE_ACCESS.administrator} />}
          >
            <Route
              path="/roles-permissions"
              element={<RolesPermissionsPage />}
            />

            <Route path="/audit-logs" element={<AuditLogsPage />} />
          </Route>

          {/* =========================
              FALLBACK
          ========================= */}
          <Route path="*" element={<PlaceholderPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
