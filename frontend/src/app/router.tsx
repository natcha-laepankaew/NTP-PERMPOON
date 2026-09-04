import { Route, Routes } from "react-router-dom";
import { DashboardPage } from "../pages/DashboardPage";
import { DispatchPage } from "../pages/DispatchPage";
import { PlaceholderPage } from "../pages/PlaceholderPage";

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/dispatch" element={<DispatchPage />} />
      <Route path="*" element={<PlaceholderPage />} />
    </Routes>
  );
}
