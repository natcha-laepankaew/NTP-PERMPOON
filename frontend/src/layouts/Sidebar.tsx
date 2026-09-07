import {
  Activity,
  Boxes,
  CarFront,
  ClipboardList,
  LayoutDashboard,
  Settings2,
  ShieldCheck,
  Users,
  X,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { hasRole } from "../services/api";

export function Sidebar({
  mobileOpen,
  onClose,
}: Readonly<{ mobileOpen: boolean; onClose: () => void }>) {
  const isSuperAdmin = hasRole("SUPER_ADMIN");
  return (
    <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
      <div className="brand">
        <div className="brand-mark">N</div>
        <div>
          <strong>NTP</strong>
          <span>PERMPOON</span>
        </div>
        <button
          className="icon-button mobile-close"
          onClick={onClose}
          aria-label="Close navigation"
        >
          <X size={18} />
        </button>
      </div>
      <div className="role-chip">
        <ShieldCheck size={15} /> OPERATIONS CONTROL
      </div>
      <nav>
        <p className="nav-label">WORKSPACE</p>
        <NavItem
          to="/"
          icon={<LayoutDashboard size={18} />}
          label="Dashboard"
          onClick={onClose}
        />
        <NavItem
          to="/dispatch"
          icon={<Activity size={18} />}
          label="Dispatch Board"
          onClick={onClose}
        />
        <NavItem
          to="/jobs"
          icon={<ClipboardList size={18} />}
          label="Jobs"
          onClick={onClose}
        />
        <NavItem
          to="/history"
          icon={<Boxes size={18} />}
          label="Job History"
          onClick={onClose}
        />
        <p className="nav-label space-top">RESOURCES</p>
        <NavItem
          to="/employees"
          icon={<Users size={18} />}
          label="Employees"
          onClick={onClose}
        />
        <NavItem
          to="/vehicles"
          icon={<CarFront size={18} />}
          label="Vehicles"
          onClick={onClose}
        />
        <p className="nav-label space-top">SYSTEM</p>
        {isSuperAdmin && (
          <NavItem
            to="/settings/roles-permissions"
            icon={<Settings2 size={18} />}
            label="Roles & Permissions"
            onClick={onClose}
          />
        )}
        {isSuperAdmin && (
          <NavItem
            to="/audit-logs"
            icon={<ShieldCheck size={18} />}
            label="Audit Logs"
            onClick={onClose}
          />
        )}
        <NavItem
          to="/settings"
          icon={<Settings2 size={18} />}
          label="Settings"
          onClick={onClose}
        />
      </nav>
      <div className="sidebar-foot">
        <div className="online-dot" /> API connected <span>v0.1.0</span>
      </div>
    </aside>
  );
}

function NavItem({
  to,
  icon,
  label,
  onClick,
}: Readonly<{
  to: string;
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}>) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
      onClick={onClick}
    >
      {icon}
      <span>{label}</span>
      {label === "Dispatch Board" && <em>HOT</em>}
    </NavLink>
  );
}
