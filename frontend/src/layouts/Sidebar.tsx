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
import { useAuth } from "../contexts/AuthContext";
import { hasAllowedRole, ROLE_ACCESS, type RoleName } from "../auth/roles";

export function Sidebar({
  mobileOpen,
  onClose,
}: Readonly<{ mobileOpen: boolean; onClose: () => void }>) {
  const { user } = useAuth();
  const userRole = user?.role.name;
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
          userRole={userRole}
        />
        <NavItem
          to="/dispatch"
          icon={<Activity size={18} />}
          label="Dispatch Board"
          onClick={onClose}
          allowedRoles={ROLE_ACCESS.operations}
          userRole={userRole}
        />
        <NavItem
          to="/jobs"
          icon={<ClipboardList size={18} />}
          label="Jobs"
          onClick={onClose}
          allowedRoles={ROLE_ACCESS.operations}
          userRole={userRole}
        />
        <NavItem
          to="/history"
          icon={<Boxes size={18} />}
          label="Job History"
          onClick={onClose}
          allowedRoles={ROLE_ACCESS.operations}
          userRole={userRole}
        />
        <p className="nav-label space-top">RESOURCES</p>
        <NavItem
          to="/employees"
          icon={<Users size={18} />}
          label="Employees"
          onClick={onClose}
          allowedRoles={ROLE_ACCESS.operations}
          userRole={userRole}
        />
        <NavItem
          to="/vehicles"
          icon={<CarFront size={18} />}
          label="Vehicles"
          onClick={onClose}
          allowedRoles={ROLE_ACCESS.operations}
          userRole={userRole}
        />
        <p className="nav-label space-top">SYSTEM</p>
        <NavItem
          to="/roles-permissions"
          icon={<Settings2 size={18} />}
          label="Roles & Permissions"
          onClick={onClose}
          allowedRoles={ROLE_ACCESS.administrator}
          userRole={userRole}
        />
        <NavItem
          to="/audit-logs"
          icon={<ShieldCheck size={18} />}
          label="Audit Logs"
          onClick={onClose}
          allowedRoles={ROLE_ACCESS.administrator}
          userRole={userRole}
        />
        <NavItem
          to="/profile"
          icon={<UserRound size={18} />}
          label="My Profile"
          onClick={onClose}
          userRole={userRole}
        />
        <NavItem
          to="/settings"
          icon={<Settings2 size={18} />}
          label="Settings"
          onClick={onClose}
          userRole={userRole}
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
  allowedRoles = ROLE_ACCESS.all,
  userRole,
}: Readonly<{
  to: string;
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  allowedRoles?: readonly RoleName[];
  userRole?: RoleName;
}>) {
  if (!hasAllowedRole(userRole, allowedRoles)) return null;
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
