import { Route, Routes } from "react-router-dom";
import { MainLayout } from "../layouts/MainLayout";
import { DashboardPage } from "../pages/DashboardPage";
import { DispatchPage } from "../pages/DispatchPage";
import { LoginPage } from "../pages/LoginPage";
import { PlaceholderPage } from "../pages/PlaceholderPage";

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<MainLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/dispatch" element={<DispatchPage />} />
        <Route path="*" element={<PlaceholderPage />} />
      </Route>
    </Routes>
  );
}
