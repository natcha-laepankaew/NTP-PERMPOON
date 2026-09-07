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
import { ProtectedRoute, SuperAdminRoute } from "../components/ProtectedRoute";
import { RolesPermissionsPage } from "../pages/RolesPermissionsPage";
import { AuditLogsPage } from "../pages/AuditLogsPage";
import { CompleteProfilePage } from "../pages/CompleteProfilePage";

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/complete-profile" element={<CompleteProfilePage />} />
        <Route element={<SuperAdminRoute />}>
          <Route path="/audit-logs" element={<AuditLogsPage />} />
          <Route element={<SuperAdminRoute />}>
            <Route
              path="/settings/roles-permissions"
              element={<RolesPermissionsPage />}
            />
            <Route path="/audit-logs" element={<AuditLogsPage />} />
          </Route>
        </Route>
        <Route element={<MainLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/dispatch" element={<DispatchPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/employees" element={<EmployeesPage />} />
          <Route path="/vehicles" element={<VehiclesPage />} />
          <Route path="*" element={<PlaceholderPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
