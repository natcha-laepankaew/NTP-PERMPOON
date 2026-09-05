import { Bell, ChevronRight, LogOut, Menu } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { logout } from "../services/api";

export function Header({ onMenuOpen }: Readonly<{ onMenuOpen: () => void }>) {
  const navigation = useNavigate();
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
          <div className="avatar">SC</div>
          <div>
            <b>Somchai Chai Dee</b>
            <span>Manager</span>
          </div>
        </div>
        <button
          className="icon-button"
          title="Sign out"
          aria-label="Sign out"
          onClick={() => {
            logout();
            navigation("/login", { replace: true });
          }}
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
