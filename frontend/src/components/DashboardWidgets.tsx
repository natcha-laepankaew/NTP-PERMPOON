import { ChevronRight } from "lucide-react";

export function MetricCard({
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

export function JobRow({
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
      <button className="icon-button" aria-label={`View ${id}`}>
        <ChevronRight size={17} />
      </button>
    </div>
  );
}

export function ReadinessBar({
  label,
  value,
  total,
  color,
}: Readonly<{ label: string; value: number; total: number; color: string }>) {
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
