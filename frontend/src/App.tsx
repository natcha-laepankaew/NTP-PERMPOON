import { useEffect, useState } from "react";
import { NavLink, Route, Routes, useNavigate } from "react-router-dom";
import {
  Activity,
  Bell,
  Boxes,
  CarFront,
  ChevronRight,
  ClipboardList,
  LayoutDashboard,
  LogOut,
  Menu,
  Search,
  Settings2,
  ShieldCheck,
  Truck,
  Users,
  X,
} from "lucide-react";
import {
  getCandidates,
  getDashboard,
  type Candidate,
  type Dashboard,
  type VehicleStatus,
} from "./api";

const statusMeta: Record<
  VehicleStatus,
  { label: string; sub: string; color: string }
> = {
  AVAILABLE: { label: "AVAILABLE", sub: "พร้อมรับงาน", color: "green" },
  BUSY: { label: "BUSY", sub: "กำลังทำงาน", color: "amber" },
  AVAILABLE_RETURN: {
    label: "AVAILABLE_RETURN",
    sub: "พร้อมรับงานขากลับ",
    color: "blue",
  },
  NOT_READY: { label: "NOT_READY", sub: "ไม่พร้อมรับงาน", color: "red" },
  MAINTENANCE: { label: "MAINTENANCE", sub: "ซ่อมบำรุง", color: "slate" },
};

function App() {
  return <MainLayout />;
}

function MainLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigation = useNavigate();
  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark">N</div>
          <div>
            <strong>NTP</strong>
            <span>PERMPOON</span>
          </div>
          <button
            className="icon-button mobile-close"
            onClick={() => setMobileOpen(false)}
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
            onClick={() => setMobileOpen(false)}
          />
          <NavItem
            to="/dispatch"
            icon={<Activity size={18} />}
            label="Dispatch Board"
            onClick={() => setMobileOpen(false)}
          />
          <NavItem
            to="/jobs"
            icon={<ClipboardList size={18} />}
            label="Jobs"
            onClick={() => setMobileOpen(false)}
          />
          <NavItem
            to="/history"
            icon={<Boxes size={18} />}
            label="Job History"
            onClick={() => setMobileOpen(false)}
          />
          <p className="nav-label space-top">RESOURCES</p>
          <NavItem
            to="/employees"
            icon={<Users size={18} />}
            label="Employees"
            onClick={() => setMobileOpen(false)}
          />
          <NavItem
            to="/vehicles"
            icon={<CarFront size={18} />}
            label="Vehicles"
            onClick={() => setMobileOpen(false)}
          />
          <p className="nav-label space-top">SYSTEM</p>
          <NavItem
            to="/reports"
            icon={<Activity size={18} />}
            label="Reports"
            onClick={() => setMobileOpen(false)}
          />
          <NavItem
            to="/settings"
            icon={<Settings2 size={18} />}
            label="Settings"
            onClick={() => setMobileOpen(false)}
          />
        </nav>
        <div className="sidebar-foot">
          <div className="online-dot" /> API connected <span>v0.1.0</span>
        </div>
      </aside>
      {mobileOpen && (
        <button
          className="mobile-overlay"
          type="button"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
        />
      )}
      <main className="main-area">
        <header className="topbar">
          <button
            className="icon-button menu-button"
            onClick={() => setMobileOpen(true)}
          >
            <Menu size={20} />
          </button>
          <div className="crumb">
            <span>Operations</span>
            <ChevronRight size={15} />
            <b>Control Center</b>
          </div>
          <div className="topbar-actions">
            <button className="icon-button notification">
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
              onClick={() => navigation("/")}
            >
              <LogOut size={18} />
            </button>
          </div>
        </header>
        <div className="page-content">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dispatch" element={<DispatchPage />} />
            <Route path="*" element={<PlaceholderPage />} />
          </Routes>
        </div>
      </main>
    </div>
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

function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch(() =>
        setData({
          counts: {
            AVAILABLE: 24,
            BUSY: 15,
            AVAILABLE_RETURN: 6,
            NOT_READY: 8,
            MAINTENANCE: 3,
          },
          today_jobs: 42,
          active_jobs: 15,
          completed_jobs: 27,
        }),
      );
  }, []);
  const counts = data?.counts;
  return (
    <>
      <PageHeading
        eyebrow="FRIDAY, 04 SEP 2026"
        title="Good morning, Somchai"
        description="Here is today's operational pulse across your fleet."
        action={
          <button
            className="button button-primary"
            onClick={() => (window.location.href = "/dispatch")}
          >
            <Search size={17} /> Find a vehicle
          </button>
        }
      />
      <section className="metrics-grid">
        <MetricCard
          label="Available now"
          value={counts?.AVAILABLE ?? "--"}
          detail="พร้อมรับงาน"
          tone="green"
          icon={<Truck size={20} />}
        />
        <MetricCard
          label="In operation"
          value={counts?.BUSY ?? "--"}
          detail="กำลังทำงาน"
          tone="amber"
          icon={<Activity size={20} />}
        />
        <MetricCard
          label="Return-ready"
          value={counts?.AVAILABLE_RETURN ?? "--"}
          detail="พร้อมรับงานขากลับ"
          tone="blue"
          icon={<Truck size={20} />}
        />
        <MetricCard
          label="Today's jobs"
          value={data?.today_jobs ?? "--"}
          detail="งานทั้งหมดวันนี้"
          tone="navy"
          icon={<ClipboardList size={20} />}
        />
      </section>
      <section className="dashboard-grid">
        <div className="panel active-jobs">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">LIVE OPERATIONS</p>
              <h2>Today's active jobs</h2>
            </div>
            <a href="/jobs">
              View all <ChevronRight size={15} />
            </a>
          </div>
          <div className="job-list">
            <JobRow
              id="JOB-20260904-001"
              route="หาดใหญ่ → พัทลุง"
              employee="สมชาย ใจดี"
              vehicle="70-1234"
              status="IN_PROGRESS"
            />
            <JobRow
              id="JOB-20260904-002"
              route="สงขลา → หาดใหญ่"
              employee="วิชัย ขับดี"
              vehicle="70-5678"
              status="ASSIGNED"
            />
            <JobRow
              id="JOB-20260904-003"
              route="หาดใหญ่ → ตรัง"
              employee="ประชา ตั้งใจ"
              vehicle="70-9999"
              status="IN_PROGRESS"
            />
          </div>
        </div>
        <div className="panel readiness">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">FLEET HEALTH</p>
              <h2>Fleet readiness</h2>
            </div>
            <span className="live-badge">
              <i /> LIVE
            </span>
          </div>
          <div className="readiness-bars">
            <ReadinessBar
              label="Available"
              value={counts?.AVAILABLE ?? 0}
              total={56}
              color="green"
            />
            <ReadinessBar
              label="In operation"
              value={counts?.BUSY ?? 0}
              total={56}
              color="amber"
            />
            <ReadinessBar
              label="Return-ready"
              value={counts?.AVAILABLE_RETURN ?? 0}
              total={56}
              color="blue"
            />
            <ReadinessBar
              label="Maintenance"
              value={counts?.MAINTENANCE ?? 0}
              total={56}
              color="slate"
            />
          </div>
          <div className="fleet-total">
            <span>Total fleet</span>
            <strong>56 vehicles</strong>
          </div>
        </div>
      </section>
    </>
  );
}

function DispatchPage() {
  const [origin, setOrigin] = useState("หาดใหญ่");
  const [employee, setEmployee] = useState("");
  const [plate, setPlate] = useState("");
  const [status, setStatus] = useState("");
  const [items, setItems] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [selected, setSelected] = useState<Candidate | null>(null);
  async function search() {
    setLoading(true);
    setSearched(true);
    try {
      const response = await getCandidates({
        origin,
        employee_name: employee,
        vehicle_plate: plate,
        status,
      });
      setItems(response.items);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    search();
  }, []);
  return (
    <>
      <PageHeading
        eyebrow="OPERATIONS / DISPATCH"
        title="Dispatch Board"
        description="Find the right vehicle for an external job in seconds."
        action={
          <button className="button button-primary">
            <ClipboardList size={17} /> Create job
          </button>
        }
      />
      <section className="dispatch-search panel">
        <div className="search-title">
          <div className="search-icon">
            <Search size={20} />
          </div>
          <div>
            <h2>Find candidate vehicles</h2>
            <p>
              Search the backend for vehicles that can start from your origin.
            </p>
          </div>
        </div>
        <div className="filters">
          <label>
            <span>Origin</span>
            <input
              value={origin}
              onChange={(event) => setOrigin(event.target.value)}
              placeholder="e.g. หาดใหญ่"
            />
          </label>
          <label>
            <span>Employee name</span>
            <input
              value={employee}
              onChange={(event) => setEmployee(event.target.value)}
              placeholder="Search employee"
            />
          </label>
          <label>
            <span>Vehicle plate</span>
            <input
              value={plate}
              onChange={(event) => setPlate(event.target.value)}
              placeholder="e.g. 70-1234"
            />
          </label>
          <label>
            <span>Status</span>
            <select
              value={status}
              onChange={(event) => setStatus(event.target.value)}
            >
              <option value="">All statuses</option>
              <option value="AVAILABLE">Available</option>
              <option value="AVAILABLE_RETURN">Return-ready</option>
              <option value="BUSY">Busy</option>
            </select>
          </label>
          <button className="button button-dark filter-button" onClick={search}>
            <Search size={17} /> Search
          </button>
        </div>
        <div className="filter-hints">
          <span>
            <i className="legend-dot green" /> Available + Ready From ={" "}
            {origin || "origin"}
          </span>
          <span>
            <i className="legend-dot blue" /> Return-ready + Current Destination
            = {origin || "origin"}
          </span>
        </div>
      </section>
      <section className="candidate-section">
        <div className="section-header">
          <div>
            <p className="eyebrow">CANDIDATE VEHICLES</p>
            <h2>
              {loading
                ? "Searching..."
                : `${items.length} vehicles can take this job`}
            </h2>
          </div>
          <span className="result-note">
            Backend filtered · Updated just now
          </span>
        </div>
        {loading ? (
          <div className="empty-state">
            <div className="spinner" /> Loading candidates
          </div>
        ) : searched && items.length === 0 ? (
          <div className="empty-state">
            <Truck size={28} />
            <strong>No vehicles found</strong>
            <span>Try clearing a filter or choosing another origin.</span>
          </div>
        ) : (
          <div className="candidate-grid">
            {items.map((item) => (
              <CandidateCard
                key={item.vehicle_id}
                candidate={item}
                onAssign={() => setSelected(item)}
              />
            ))}
          </div>
        )}
      </section>
      {selected && (
        <AssignModal candidate={selected} onClose={() => setSelected(null)} />
      )}
    </>
  );
}

function CandidateCard({
  candidate,
  onAssign,
}: Readonly<{
  candidate: Candidate;
  onAssign: () => void;
}>) {
  const meta = statusMeta[candidate.operational_status];
  return (
    <article className="candidate-card">
      <div className="candidate-top">
        <div className="vehicle-icon">
          <Truck size={21} />
        </div>
        <div>
          <h3>{candidate.vehicle_plate}</h3>
          <p>{candidate.employee_name}</p>
        </div>
        <span className={`status-pill ${meta.color}`}>
          <i />
          {meta.label}
        </span>
      </div>
      <div className="candidate-context">
        <div>
          <span>
            {candidate.candidate_type === "return"
              ? "Current destination"
              : "Ready from"}
          </span>
          <strong>
            {candidate.current_destination ??
              candidate.ready_from ??
              "ยังไม่ระบุ"}
          </strong>
        </div>
        <div>
          <span>Candidate type</span>
          <strong>
            {candidate.candidate_type === "return"
              ? "ONE_WAY return"
              : "New job"}
          </strong>
        </div>
      </div>
      <div className="candidate-foot">
        <span className="explain">
          <ShieldCheck size={15} /> {meta.sub}
        </span>
        <button className="button button-outline" onClick={onAssign}>
          Assign job <ChevronRight size={15} />
        </button>
      </div>
    </article>
  );
}

function AssignModal({
  candidate,
  onClose,
}: Readonly<{
  candidate: Candidate;
  onClose: () => void;
}>) {
  return (
    <dialog
      open
      className="modal-backdrop"
      aria-labelledby="assign-title"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
      onKeyDown={(event) => {
        if (event.key === "Escape") onClose();
      }}
    >
      <div className="modal">
        <div className="modal-heading">
          <div>
            <p className="eyebrow">ASSIGNMENT REVIEW</p>
            <h2 id="assign-title">Assign this vehicle?</h2>
          </div>
          <button className="icon-button" onClick={onClose}>
            <X size={19} />
          </button>
        </div>
        <div className="route-preview">
          <div>
            <span>ORIGIN</span>
            <strong>หาดใหญ่</strong>
          </div>
          <div className="route-line">
            <Truck size={18} />
          </div>
          <div>
            <span>DESTINATION</span>
            <strong>พัทลุง</strong>
          </div>
        </div>
        <dl className="detail-list">
          <div>
            <dt>Employee</dt>
            <dd>{candidate.employee_name}</dd>
          </div>
          <div>
            <dt>Vehicle</dt>
            <dd>{candidate.vehicle_plate}</dd>
          </div>
          <div>
            <dt>Vehicle status</dt>
            <dd>
              <span
                className={`status-pill ${statusMeta[candidate.operational_status].color}`}
              >
                <i />
                {candidate.operational_status}
              </span>
            </dd>
          </div>
        </dl>
        <div className="modal-warning">
          <ShieldCheck size={17} />
          <span>
            Availability will be checked again by the backend before assignment.
          </span>
        </div>
        <div className="modal-actions">
          <button className="button button-quiet" onClick={onClose}>
            Cancel
          </button>
          <button className="button button-primary" onClick={onClose}>
            Confirm assignment
          </button>
        </div>
      </div>
    </dialog>
  );
}

function PageHeading({
  eyebrow,
  title,
  description,
  action,
}: Readonly<{
  eyebrow: string;
  title: string;
  description: string;
  action: React.ReactNode;
}>) {
  return (
    <div className="page-heading">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </div>
  );
}
function MetricCard({
  label,
  value,
  detail,
  tone,
  icon,
}: Readonly<{
  label: string;
  value: number | string;
  detail: string;
  tone: string;
  icon: React.ReactNode;
}>) {
  return (
    <div className={`metric-card ${tone}`}>
      <div className="metric-icon">{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{detail}</small>
      </div>
      <div className="metric-trend">+12%</div>
    </div>
  );
}
function JobRow({
  id,
  route,
  employee,
  vehicle,
  status,
}: Readonly<{
  id: string;
  route: string;
  employee: string;
  vehicle: string;
  status: string;
}>) {
  return (
    <div className="job-row">
      <div className="job-id">{id}</div>
      <div>
        <strong>{route}</strong>
        <span>
          {employee} · {vehicle}
        </span>
      </div>
      <span
        className={`status-pill ${status === "IN_PROGRESS" ? "amber" : "blue"}`}
      >
        <i />
        {status}
      </span>
      <button className="icon-button">
        <ChevronRight size={17} />
      </button>
    </div>
  );
}
function ReadinessBar({
  label,
  value,
  total,
  color,
}: Readonly<{
  label: string;
  value: number;
  total: number;
  color: string;
}>) {
  return (
    <div className="bar-row">
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
      <div className="bar-track">
        <i
          className={color}
          style={{ width: `${Math.min((value / total) * 100, 100)}%` }}
        />
      </div>
    </div>
  );
}
function PlaceholderPage() {
  return (
    <div className="empty-page">
      <Boxes size={34} />
      <p className="eyebrow">COMING NEXT</p>
      <h1>Operations workspace</h1>
      <p>
        This route is scaffolded and ready for the next implementation phase.
      </p>
    </div>
  );
}

export default App;
