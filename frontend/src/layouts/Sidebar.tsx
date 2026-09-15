import {
  Activity,
  Boxes,
  CarFront,
  ClipboardList,
  LayoutDashboard,
  UserRound,
  Settings2,
  ShieldCheck,
  Users,
  X,
} from "lucide-react";

import { NavLink } from "react-router-dom";

import { PermissionGate } from "../components/PermissionGate";

import { PERMISSIONS } from "../auth/roles";

export function Sidebar({
  mobileOpen,
  onClose,
}: Readonly<{
  mobileOpen: boolean;
  onClose: () => void;
}>) {
  return (
    <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
      {/* =========================
          BRAND
      ========================= */}
      <div className="brand">
        <div className="brand-mark">N</div>

        <div>
          <strong>NTP</strong>
          <span>PERMPOON</span>
        </div>

        <button
          type="button"
          className="icon-button mobile-close"
          onClick={onClose}
          aria-label="Close navigation"
        >
          <X size={18} />
        </button>
      </div>

      {/* =========================
          ROLE / SYSTEM
      ========================= */}
      <div className="role-chip">
        <ShieldCheck size={15} />
        OPERATIONS CONTROL
      </div>

      <nav>
        {/* =========================
            WORKSPACE
        ========================= */}
        <p className="nav-label">WORKSPACE</p>

        {/* Dashboard */}
        <PermissionNavItem
          to="/"
          icon={<LayoutDashboard size={18} />}
          label="Dashboard"
          permission={PERMISSIONS.DASHBOARD_VIEW}
          onClick={onClose}
        />

        {/* Dispatch */}
        <PermissionNavItem
          to="/dispatch"
          icon={<Activity size={18} />}
          label="Dispatch Board"
          permission={PERMISSIONS.DISPATCH_VIEW}
          onClick={onClose}
          hot
        />

        {/* Jobs
            ADMIN / MANAGER = jobs.view
            DRIVER = jobs.view_own
        */}
        <PermissionNavItem
          to="/jobs"
          icon={<ClipboardList size={18} />}
          label="Jobs"
          permissions={[PERMISSIONS.JOBS_VIEW, PERMISSIONS.JOBS_VIEW_OWN]}
          onClick={onClose}
        />

        {/* Job History */}
        <PermissionNavItem
          to="/history"
          icon={<Boxes size={18} />}
          label="Job History"
          permission={PERMISSIONS.HISTORY_VIEW}
          onClick={onClose}
        />

        {/* =========================
            RESOURCES
        ========================= */}
        <p className="nav-label space-top">RESOURCES</p>

        {/* Employees */}
        <PermissionNavItem
          to="/employees"
          icon={<Users size={18} />}
          label="Employees"
          permission={PERMISSIONS.EMPLOYEES_VIEW}
          onClick={onClose}
        />

        {/* Vehicles */}
        <PermissionNavItem
          to="/vehicles"
          icon={<CarFront size={18} />}
          label="Vehicles"
          permission={PERMISSIONS.VEHICLES_VIEW}
          onClick={onClose}
        />

        {/* =========================
            SYSTEM
        ========================= */}
        <p className="nav-label space-top">SYSTEM</p>

        {/* Roles & Permissions */}
        <PermissionNavItem
          to="/roles-permissions"
          icon={<Settings2 size={18} />}
          label="Roles & Permissions"
          permission={PERMISSIONS.ROLES_PERMISSIONS_VIEW}
          onClick={onClose}
        />

        {/* Audit Logs */}
        <PermissionNavItem
          to="/audit-logs"
          icon={<ShieldCheck size={18} />}
          label="Audit Logs"
          permission={PERMISSIONS.AUDIT_LOGS_VIEW}
          onClick={onClose}
        />

        {/* My Profile */}
        <PermissionNavItem
          to="/profile"
          icon={<UserRound size={18} />}
          label="My Profile"
          permission={PERMISSIONS.PROFILE_VIEW}
          onClick={onClose}
        />

        {/* Settings
            ตอนนี้ยังไม่มี settings.view
            จึงยังไม่ควรแสดงด้วย permission
        */}
      </nav>

      {/* =========================
          FOOTER
      ========================= */}
      <div className="sidebar-foot">
        <div className="online-dot" />
        API connected
        <span>v0.1.0</span>
      </div>
    </aside>
  );
}

/* =====================================================
   Permission Nav Item
===================================================== */

function PermissionNavItem({
  to,
  icon,
  label,
  permission,
  permissions,
  onClick,
  hot = false,
}: Readonly<{
  to: string;
  icon: React.ReactNode;
  label: string;

  permission?: (typeof PERMISSIONS)[keyof typeof PERMISSIONS];

  permissions?: readonly (typeof PERMISSIONS)[keyof typeof PERMISSIONS][];

  onClick: () => void;

  hot?: boolean;
}>) {
  const content = (
    <NavLink
      to={to}
      className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
      onClick={onClick}
    >
      {icon}

      <span>{label}</span>

      {hot && <em>HOT</em>}
    </NavLink>
  );

  if (permission) {
    return <PermissionGate permission={permission}>{content}</PermissionGate>;
  }

  if (permissions) {
    return <PermissionGate permissions={permissions}>{content}</PermissionGate>;
  }

  return null;
}
