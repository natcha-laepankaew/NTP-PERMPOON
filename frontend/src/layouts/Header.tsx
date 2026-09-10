import { Bell, ChevronRight, LogOut, Menu } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function Header({ onMenuOpen }: Readonly<{ onMenuOpen: () => void }>) {
  const navigation = useNavigate();
  const { user, signOut } = useAuth();
  return (
    <header className="topbar">
      <button
        className="icon-button menu-button"
        onClick={onMenuOpen}
        aria-label="Open navigation"
      >
        <Menu size={20} />
      </button>
      <div className="crumb">
        <span>Operations</span>
        <ChevronRight size={15} />
        <b>Control Center</b>
      </div>
      <div className="topbar-actions">
        <button className="icon-button notification" aria-label="Notifications">
          <Bell size={19} />
          <i />
        </button>
        <div className="user">
          <div className="avatar">{user?.name.slice(0, 2).toUpperCase()}</div>
          <div>
            <b>{user?.name}</b>
            <span>{user?.role.name}</span>
          </div>
        </div>
        <button
          className="icon-button"
          title="Sign out"
          aria-label="Sign out"
          onClick={() => {
            void signOut();
            navigation("/login", { replace: true });
          }}
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
